from shapely.geometry import shape, mapping
from shapely.ops import cascaded_union
import fiona
import itertools
import json
import os

__version__ = (0, 1)

DATA_FILEPATH = os.path.join(os.path.dirname(__file__), u"data")


class ConstructiveGeometries(object):
    def __init__(self):
        self.data_fp = os.path.join(DATA_FILEPATH, u"faces.json")
        self.faces_fp = os.path.join(DATA_FILEPATH, u"faces.gpkg")
        self.check_data()
        self.load_definitions()

    def check_data(self):
        """Check that definitions file is present, and that faces file is readable."""
        assert os.path.exists(self.data_fp)
        with fiona.drivers():
            with fiona.open(self.faces_fp) as src:
                assert src.meta

    def load_definitions(self):
        """Load mapping of country names to face ids"""
        self.data = dict(json.load(open(self.data_fp)))
        self.all_faces = set(self.data.pop(u"__all__"))
        self.locations = set(self.data.keys())

    def construct_rest_of_world(self, excluded, name=None, fp=None):
        """Construct rest-of-world geometry and optionally write to filepath ``fp``.

        Excludes faces in location list ``excluded``. ``excluded`` must be an iterable of location strings (not face ids)."""
        for location in excluded:
            assert location in self.locations, u"Can't find location {}".format(location)
        included = self.all_faces.difference(
            reduce(set.union, [set(self.data[loc]) for loc in excluded])
        )
        geom = self._union(included)
        if fp:
            self.write_geoms_to_file(fp, [geom], [name] if name else None)
            return fp
        else:
            return geom

    def construct_difference(self, parent, excluded, name=None, fp=None):
        """Construct geometry from ``parent`` without the regions in ``excluded`` and optionally write to filepath ``fp``.

        ``excluded`` must be an iterable of location strings (not face ids)."""
        assert parent in self.locations, u"Can't find location {}".format(parent)
        for location in excluded:
            assert location in self.locations, u"Can't find location {}".format(location)
        included = set(self.data[parent]).difference(
            reduce(set.union, [set(self.data[loc]) for loc in excluded])
        )
        geom = self._union(included)
        if fp:
            self.write_geoms_to_file(fp, [geom], [name] if name else None)
            return fp
        else:
            return geom

    def write_geoms_to_file(self, fp, geoms, names=None):
        """Write unioned geometries ``geoms`` to filepath ``fp``. Optionally use ``names`` in name field."""
        if names is not None:
            assert len(geoms) == len(names), u"Inconsistent length of geometries and names"
        else:
            names = (u"Merged geometry {}".format(count) for count in itertools.count())
        meta = {
            'crs': {'no_defs': True, 'ellps': 'WGS84', 'datum': 'WGS84', 'proj': 'longlat'},
            'driver': u'GPKG',
            'schema': {'geometry': 'MultiPolygon', 'properties': {'name': 'str', 'id': 'int'}}
        }
        with fiona.drivers():
            with fiona.open(fp + '.gpkg', 'w', **meta) as sink:
                for geom, name, count in itertools.izip(geoms, itertools.count(1)):
                    sink.write({
                        'geometry': self._to_fiona(geom),
                        'properties': {'name': name, 'id': count}
                    })

    def _to_shapely(self, data):
        return shape(data['geometry'])

    def _to_fiona(self, data):
        return mapping(data)

    def _union(self, face_ids):
        shapes = []
        with fiona.drivers():
            with fiona.open(self.faces_fp) as src:
                for feat in src:
                    if int(feat[u'properties'][u'id']) in face_ids:
                        shapes.append(self._to_shapely(feat))
        return cascaded_union(shapes)
