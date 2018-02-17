constructive_geometries
=======================

|build-status| |coverage|

Simple tools to define world locations from a set of topological faces and set algebra. For example, one could define a "rest of the world" which started from all countries, but excluded every country who name started with the letter "a".

No requirements for basic use, but needs `shapely <https://github.com/Toblerity/Shapely>`__, and `fiona <https://github.com/Toblerity/Fiona>`__ for any GIS functions.

.. note:: See the `usage example <https://github.com/cmutel/constructive_geometries/blob/master/examples/Geomatching.ipynb>`__

Installation
------------

Because of the GIS library dependencies, it is easiest to install using `conda <>`__. Installation into a new environment is recommended (doesn't need to be called ``cg``):

.. code-block:: bash

    conda create -n cg python=3.6
    source activate cg
    conda install -c conda-forge -c cmutel -c konstantinstadler country_converter constructive_geometries

`ConstructiveGeometries` class
------------------------------

.. autoclass:: constructive_geometries.cg.ConstructiveGeometries
    :members:

`Geomatcher` class
------------------

.. autoclass:: constructive_geometries.geomatcher.Geomatcher
    :members:

.. |build-status| image:: https://travis-ci.org/cmutel/constructive_geometries.svg?branch=master
    :alt: build status
    :scale: 100%
    :target: https://travis-ci.org/cmutel/constructive_geometries

.. |coverage| image:: https://coveralls.io/repos/github/cmutel/constructive_geometries/badge.svg?branch=master
    :alt: build status
    :scale: 100%
    :target: https://coveralls.io/github/cmutel/constructive_geometries?branch=master
