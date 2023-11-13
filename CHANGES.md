# Changelog

## 0.9.2 (2023-11-13)

* Add areas of faces

## 0.9.1 (2023-11-13)

* Complete adding type annotations

## 0.9 (2023-11-12)

* Compatiblity with ecoinvent 3.10
* Packaging switch to `pyproject.toml`
* Add `backwards_compatible` argument to include deprecated locations
* [#7 bugfix in `construct_rest_of_world`](https://github.com/ecoinvent/constructive_geometries/pull/7)
* [#4 Display key as part of error message](https://github.com/ecoinvent/constructive_geometries/pull/4)

### 0.8.2 (2022-04-29)

* Allow either "PR" or "US-PR"

### 0.8.1 (2022-04-21)

* Change code for Puerto Rico from "PR" to "US-PR". Both ISO codes are allowed. Maintains ecoinvent compatibility.
* Switch from the deprecated `shapely.ops.cascaded_union` to `shapely.ops.unnary_union`.

## 0.8 (2022-04-21)

Update base data

## 0.7 (2019-10-29)

* Fix update `fiona` calling syntax
* Fix `reduce` not a builtin for Python 3
* Fix implementation bugs in `construct_difference`

## 0.6.4 (2018-05-31)

Add Washington D.C. to ReliabilityFirst Corporation

### 0.6.3.1 (2018-05-29)

Fix problem with updated base data

## 0.6.3 (2018-05-29)

Update base data

## 0.6.2 (2018-05-14)

Update base data

## 0.6.1.3 (2018-02-17)

Packaging fixes

## 0.6.1 (2017-10-18)

Packaging fixes

## 0.6 (2017-10-18)

- Add Geomatcher class and resolve_row
- Move to Github
- Add example usage notebook

## 0.5 (2017-09-26)

- Updates for ecoinvent 3.4 (see http://geography.ecoinvent.org/report/#version-2-2-ecoinvent-3-4)
- Remove all GIS requirements

## 0.4 (2016-05-02)

- Add multiprocessing for building many RoWs
- Added simplify parameter for many RoWs

## 0.3.1 (2016-05-02)

- Add functions for RoW topologies

## 0.3 (2016-04-26)

- Changes to ``faces.json`` file to ensure consistency with ``faces.gpkg``

## 0.2 (2016-04-11)

- Topology for ecoinvent 3.2

## 0.1 (2015-07-05)

- Topology for ecoinvent 3.1
