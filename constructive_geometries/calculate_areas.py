from pathlib import Path
from pyproj import Geod
from shapely.geometry import shape
import fiona
import json

DATA_DIR = Path(__file__).parent.resolve() / "data"


def calculate_face_areas():
    # Stolen from https://stackoverflow.com/a/64165076/164864
    areas = {}
    geod = Geod(ellps="WGS84")

    with fiona.Env():
        with fiona.open(DATA_DIR / "faces.gpkg") as src:
            for feat in src:
                polygon = shape(feat.geometry)
                areas[feat.properties["id"]] = abs(
                    geod.geometry_area_perimeter(polygon)[0]
                )

    with open(DATA_DIR / "areas.json", "w") as f:
        json.dump(areas, f, indent=2)


if __name__ == "__main__":
    calculate_face_areas()
