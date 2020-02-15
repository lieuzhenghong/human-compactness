from shapely.geometry import MultiPoint
from scipy.spatial import ConvexHull
import json


def convex_hull_compare():
    with open("./test_points.json", 'r') as f:
        points = json.load(f)
        print(points)
        hull = ConvexHull(points)
        ch_area = MultiPoint(points).convex_hull.area

        print(
            f"Scipy Convex Hull Area: {hull.area}, Shapely Convex Hull Area: {ch_area}")
        # Scipy Convex Hull Area: 457761.9061526276, Shapely Convex Hull Area: 13192154623.86528


if __name__ == "__main__":
    convex_hull_compare()
