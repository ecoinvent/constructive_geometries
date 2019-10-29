from functools import reduce
from multiprocessing import Pool, cpu_count
from warnings import warn
import hashlib
import itertools
import json
import os
import wrapt

try:
    from shapely.geometry import shape, mapping
    from shapely.ops import cascaded_union
    import fiona

    gis = True
except ImportError:
    gis = False


MISSING_GIS = (
    """Function not available: GIS libraries (fiona and shapely) not installed"""
)


@wrapt.decorator
def has_gis(wrapped, instance, args, kwargs):
    """Skip function execution if there are no presamples"""
    if gis:
        return wrapped(*args, **kwargs)
    else:
        warn(MISSING_GIS)


DATA_FILEPATH = os.path.join(os.path.dirname(__file__), "data")


def sha256(filepath, blocksize=65536):
    """Generate SHA 256 hash for file at `filepath`"""
    hasher = hashlib.sha256()
    fo = open(filepath, "rb")
    buf = fo.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = fo.read(blocksize)
    return hasher.hexdigest()


@has_gis
def _to_shapely(data):
    return shape(data["geometry"])


@has_gis
def _to_fiona(data):
    return mapping(data)


@has_gis
def _union(args):
    label, fp, face_ids = args
    shapes = []
    with fiona.Env():
        with fiona.open(fp) as src:
            for feat in src:
                if int(feat["properties"]["id"]) in face_ids:
                    shapes.append(_to_shapely(feat))
    return label, cascaded_union(shapes)


class ConstructiveGeometries(object):
    def __init__(self):
        self.data_fp = os.path.join(DATA_FILEPATH, "faces.json")
        self.faces_fp = os.path.join(DATA_FILEPATH, "faces.gpkg")
        self.check_data()
        self.load_definitions()

    def check_data(self):
        """Check that definitions file is present, and that faces file is readable."""
        assert os.path.exists(self.data_fp)
        if gis:
            with fiona.Env():
                with fiona.open(self.faces_fp) as src:
                    assert src.meta

        gpkg_hash = json.load(open(self.data_fp))["metadata"]["sha256"]
        assert gpkg_hash == sha256(self.faces_fp)

    def load_definitions(self):
        """Load mapping of country names to face ids"""
        self.data = dict(json.load(open(self.data_fp))["data"])
        self.all_faces = set(self.data.pop("__all__"))
        self.locations = set(self.data.keys())

    def construct_rest_of_world(self, excluded, name=None, fp=None, geom=True):
        """Construct rest-of-world geometry and optionally write to filepath ``fp``.

        Excludes faces in location list ``excluded``. ``excluded`` must be an iterable of location strings (not face ids)."""
        for location in excluded:
            assert location in self.locations, "Can't find location {}".format(location)
        included = self.all_faces.difference(
            set().union(*[set(self.data[loc]) for loc in excluded])
        )

        if not geom:
            return included
        elif not gis:
            warn(MISSING_GIS)
            return

        geom = _union(included)[1]
        if fp:
            self.write_geoms_to_file(fp, [geom], [name] if name else None)
            return fp
        else:
            return geom

    @has_gis
    def construct_rest_of_worlds(self, excluded, fp=None, use_mp=True, simplify=True):
        """Construct many rest-of-world geometries and optionally write to filepath ``fp``.

        ``excluded`` must be a **dictionary** of {"rest-of-world label": ["names", "of", "excluded", "locations"]}``."""
        geoms = {}
        raw_data = []
        for key in sorted(excluded):
            locations = excluded[key]
            for location in locations:
                assert location in self.locations, "Can't find location {}".format(
                    location
                )
            included = self.all_faces.difference(
                {face for loc in locations for face in self.data[loc]}
            )
            raw_data.append((key, self.faces_fp, included))
        if use_mp:
            with Pool(cpu_count() - 1) as pool:
                results = pool.map(_union, raw_data)
            geoms = dict(results)
        else:
            geoms = dict([_union(row) for row in raw_data])
        if simplify:
            geoms = {k: v.simplify(0.05) for k, v in geoms.items()}
        if fp:
            labels = sorted(geoms)
            self.write_geoms_to_file(fp, [geoms[key] for key in labels], labels)
            return fp
        else:
            return geoms

    def construct_rest_of_worlds_mapping(self, excluded, fp=None):
        """Construct topo mapping file for ``excluded``.

        ``excluded`` must be a **dictionary** of {"rest-of-world label": ["names", "of", "excluded", "locations"]}``.

        Topo mapping has the data format:

        .. code-block:: python

            {
                'data': [
                    ['location label', ['topo face integer ids']],
                ],
                'metadata': {
                    'filename': 'name of face definitions file',
                    'field': 'field with uniquely identifies the fields in ``filename``',
                    'sha256': 'SHA 256 hash of ``filename``'
                }
            }

        """
        metadata = {
            "filename": "faces.gpkg",
            "field": "id",
            "sha256": sha256(self.faces_fp),
        }
        data = []
        for key, locations in excluded.items():
            for location in locations:
                assert location in self.locations, "Can't find location {}".format(
                    location
                )
            included = self.all_faces.difference(
                {face for loc in locations for face in self.data[loc]}
            )
            data.append((key, sorted(included)))
        obj = {"data": data, "metadata": metadata}
        if fp:
            with open(fp, "w") as f:
                json.dump(obj, f, indent=2)
        else:
            return obj

    @has_gis
    def construct_difference(self, parent, excluded, name=None, fp=None):
        """Construct geometry from ``parent`` without the regions in ``excluded`` and optionally write to filepath ``fp``.

        ``excluded`` must be an iterable of location strings (not face ids)."""
        assert parent in self.locations, "Can't find location {}".format(parent)
        for location in excluded:
            assert location in self.locations, "Can't find location {}".format(location)
        included = set(self.data[parent]).difference(
            reduce(set.union, [set(self.data[loc]) for loc in excluded])
        )
        _, geom = _union((None, self.faces_fp, included))
        if fp:
            self.write_geoms_to_file(fp, [geom], [name] if name else None)
            return fp
        else:
            return geom

    @has_gis
    def write_geoms_to_file(self, fp, geoms, names=None):
        """Write unioned geometries ``geoms`` to filepath ``fp``. Optionally use ``names`` in name field."""
        if fp[-5:] != ".gpkg":
            fp = fp + ".gpkg"
        if names is not None:
            assert len(geoms) == len(
                names
            ), "Inconsistent length of geometries and names"
        else:
            names = ("Merged geometry {}".format(count) for count in itertools.count())
        meta = {
            "crs": {
                "no_defs": True,
                "ellps": "WGS84",
                "datum": "WGS84",
                "proj": "longlat",
            },
            "driver": "GPKG",
            "schema": {
                "geometry": "MultiPolygon",
                "properties": {"name": "str", "id": "int"},
            },
        }
        with fiona.Env():
            with fiona.open(fp, "w", **meta) as sink:
                for geom, name, count in zip(geoms, names, itertools.count(1)):
                    sink.write(
                        {
                            "geometry": _to_fiona(geom),
                            "properties": {"name": name, "id": count},
                        }
                    )
        return fp
