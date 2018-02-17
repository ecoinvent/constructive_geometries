Constructive Geometries - Python library
========================================

|Documentation Status| |Build Status| |Coverage Status|

Simple tools to define world locations from a set of topological faces
and set algebra. For example, one could define a “rest of the world”
which started from all countries, but excluded every country who name
started with the letter “a”.

`Documentation <http://constructive-geometries.readthedocs.io/?badge=latest>`__
and `usage
example <https://github.com/cmutel/constructive_geometries/blob/master/examples/Geomatching.ipynb>`__.

Builds on top of `constructive
geometries <https://github.com/cmutel/constructive_geometries>`__.

Basic installation needs
`wrapt <http://wrapt.readthedocs.io/en/latest/>`__ and
`country_converter <https://github.com/konstantinstadler/country_converter>`__;
GIS functions need `shapely <https://github.com/Toblerity/Shapely>`__,
and `fiona <https://github.com/Toblerity/Fiona>`__.

.. |Documentation Status| image:: https://readthedocs.org/projects/constructive-geometries/badge/?version=latest
   :target: http://constructive-geometries.readthedocs.io/?badge=latest
.. |Build Status| image:: https://travis-ci.org/cmutel/constructive_geometries.svg?branch=master
   :target: https://travis-ci.org/cmutel/constructive_geometries
.. |Coverage Status| image:: https://coveralls.io/repos/github/cmutel/constructive_geometries/badge.svg?branch=master
   :target: https://coveralls.io/github/cmutel/constructive_geometries?branch=master
