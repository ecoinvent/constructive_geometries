constructive_geometries
=======================

Simple tools to define world locations from a set of topological faces and set algebra. For example, one could define a "rest of the world" which started from all countries, but excluded every country who name started with the letter "a".

No requirements for basic use, but needs `shapely <https://github.com/Toblerity/Shapely>`__, and `fiona <https://github.com/Toblerity/Fiona>`__ for any GIS functions.

`ConstructiveGeometries` class
------------------------------

.. autoclass:: constructive_geometries.cg.ConstructiveGeometries
    :members:

`Geomatcher` class
------------------

.. autoclass:: constructive_geometries.geomatcher.Geomatcher
    :members:
