# -*- coding: utf-8 -*-
from __future__ import print_function

from shapely.geometry import shape, mapping
from shapely.ops import cascaded_union
import fiona
import hashlib
import itertools
import json
import os

__version__ = (0, 3, 1)

DATA_FILEPATH = os.path.join(os.path.dirname(__file__), u"data")


def sha256(filepath, blocksize=65536):
    """Generate SHA 256 hash for file at `filepath`"""
    hasher = hashlib.sha256()
    fo = open(filepath, 'rb')
    buf = fo.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = fo.read(blocksize)
    return hasher.hexdigest()


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

        gpkg_hash = json.load(open(self.data_fp))['metadata']['sha256']
        assert gpkg_hash == sha256(self.faces_fp)

    def load_definitions(self):
        """Load mapping of country names to face ids"""
        self.data = dict(json.load(open(self.data_fp))['data'])
        self.all_faces = set(self.data.pop(u"__all__"))
        self.locations = set(self.data.keys())

    def construct_rest_of_world(self, excluded, name=None, fp=None, geom=True):
        """Construct rest-of-world geometry and optionally write to filepath ``fp``.

        Excludes faces in location list ``excluded``. ``excluded`` must be an iterable of location strings (not face ids)."""
        for location in excluded:
            assert location in self.locations, u"Can't find location {}".format(location)
        included = self.all_faces.difference(
            set().union(*[set(self.data[loc]) for loc in excluded])
        )
        if not geom:
            return included
        geom = self._union(included)
        if fp:
            self.write_geoms_to_file(fp, [geom], [name] if name else None)
            return fp
        else:
            return geom

    def construct_rest_of_worlds(self, excluded, fp=None):
        """Construct many rest-of-world geometries and optionally write to filepath ``fp``.

        ``excluded`` must be a **dictionary** of {"rest-of-world label": ["names", "of", "excluded", "locations"]}``."""
        geoms = {}
        for key, locations in excluded.items():
            print("Working on location:", key)
            for location in locations:
                assert location in self.locations, u"Can't find location {}".format(location)
            included = self.all_faces.difference(
                {face for loc in locations for face in self.data[loc]}
            )
            geoms[key] = self._union(included)
        if fp:
            labels = sorted(geoms.keys())
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
            'filename': 'faces.gpkg',
            'field': 'id',
            'sha256': sha256(self.faces_fp)
        }
        data = []
        for key, locations in excluded.items():
            for location in locations:
                assert location in self.locations, u"Can't find location {}".format(location)
            included = self.all_faces.difference(
                {face for loc in locations for face in self.data[loc]}
            )
            data.append((key, sorted(included)))
        obj = {'data': data, 'metadata': metadata}
        if fp:
            with open(fp, "w") as f:
                json.dump(obj, f, indent=2)
        else:
            return obj

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
        if fp[-5:] != u'.gpkg':
            fp = fp + u'.gpkg'
        if names is not None:
            assert len(geoms) == len(names), u"Inconsistent length of geometries and names"
        else:
            names = (u"Merged geometry {}".format(count) for count in itertools.count())
        meta = {
            u'crs': {u'no_defs': True, u'ellps': u'WGS84', u'datum': u'WGS84', u'proj': u'longlat'},
            u'driver': u'GPKG',
            u'schema': {u'geometry': u'MultiPolygon', u'properties': {u'name': u'str', u'id': u'int'}}
        }
        with fiona.drivers():
            with fiona.open(fp, u'w', **meta) as sink:
                for geom, name, count in itertools.izip(geoms, names, itertools.count(1)):
                    sink.write({
                        u'geometry': self._to_fiona(geom),
                        u'properties': {u'name': name, u'id': count}
                    })
        return fp

    def _to_shapely(self, data):
        return shape(data[u'geometry'])

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
