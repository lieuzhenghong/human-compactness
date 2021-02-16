# -*- coding: utf-8 -*-

"""
Created on Thu Feb 6 22:43:43 2020
@author: darac

Modified on Sat Feb 15 2020
@author: lieuzhenghong

"""

import geopandas as gpd
import shapely
from shapely.geometry import MultiPoint
from scipy.spatial import ConvexHull
from smallest_enclosing_circle import *
from timeit import default_timer as timer


def _assign_district_to_row(row, partition):
    if row["id"] not in partition.assignment:
        return None
    else:
        return partition.assignment[row["id"]]


def _assign_id_to_row(row, geoid_to_id_mapping):
    geoid = row["GEOID"]
    tract_id = geoid_to_id_mapping[geoid]
    return tract_id


def _generate_external_points(row, geoid_to_id_mapping):
    """
    For each Census Tract, generate the exterior points of that Tract
    """
    exterior_points = []

    # print(row['geometry'].geom_type)
    if row["geometry"].geom_type == "MultiPolygon":
        for polygon in row["geometry"]:
            exterior_points += list(polygon.exterior.coords)
    else:
        assert row["geometry"].geom_type == "Polygon"
        polygon = row["geometry"]
        exterior_points += list(polygon.exterior.coords)

    return exterior_points


def preprocess_dataframe(tract_df, geoid_to_id_mapping):
    """
    Preprocess the dataframe to assign a partition ID to each row in the
    Census Tract shapefile
    """
    start = timer()

    print("Assigning tract ID to each row in shapefile...")
    tract_df["id"] = tract_df.apply(
        _assign_id_to_row, axis=1, args=[geoid_to_id_mapping]
    )

    print("Building exterior points of each Census Tract...")
    tract_df["exterior_points"] = tract_df.apply(
        _generate_external_points, axis=1, args=[geoid_to_id_mapping]
    )

    end_0 = timer()
    print(f"Time taken to preprocess dataframe: {end_0 - start}")

    return tract_df


def reock(processed_tract_df, partition):
    """
    Takes a tract shapefile dataframe with external points and IDs applied and calculates
    Reock score of a given Partition assignment

    you also get Convex Hull ratio for free

    Returns: a tuple of (List[Float], List[Float]), first Reock, then Convex Hull
    """
    # start_reock_2 = timer()

    processed_tract_df["assignment"] = processed_tract_df.apply(
        _assign_district_to_row, axis=1, args=[partition]
    )

    print("Grouping by assignment...")
    grouped_df = processed_tract_df.groupby("assignment")

    # concatenate all exterior points
    all_exterior_points = grouped_df["exterior_points"].apply(list)
    # all_exterior_points is a Pandas Series

    reock_scores = {}
    ch_scores = {}

    start_reock_calc = timer()
    for i in range(len(partition)):
        points2 = all_exterior_points.iloc[i]
        # flatten points2 list of lists (of exterior points)
        points = [item for sublist in points2 for item in sublist]

        hull = ConvexHull(points)
        new_points = [points[i] for i in hull.vertices]
        ch_area = MultiPoint(new_points).convex_hull.area

        radius_bound_circle = make_circle(new_points)[2]
        area_district = partition["area"][i]
        ch_score = area_district / ch_area
        area_circle = math.pi * (radius_bound_circle ** 2)

        reock_score = area_district / area_circle
        # print(f"Reock Score: {reock_score}, Convex Hull Score: {ch_score}")

        assert ch_score > reock_score
        assert ch_score < 1
        assert reock_score < 1

        reock_scores[i] = reock_score
        ch_scores[i] = ch_score

    end_reock_calc = timer()
    print(f"Time taken in the district loop: {end_reock_calc - start_reock_calc}")

    # end_reock_2 = timer()

    return reock_scores, ch_scores


"""
def compare_reock(state_shapefile, geoid_to_id_mapping, partition):
    # reock_values = reock(state_shapefile, geoid_to_id_mapping, partition)
    reock_2_values = reock_2(state_shapefile, partition)

    # assert(reock_values == reock_2_values)
    # return reock_values
    return reock_2_values


def reock(state_shapefile, geoid_to_id_mapping, partition):
    start_reock = timer()

    dist_scores = {}
    ch_scores = []

    state_shapefile['id'] = state_shapefile.apply(
        _assign_id_to_row, axis=1, args=[geoid_to_id_mapping])
    state_shapefile['assignment'] = state_shapefile.apply(
        _assign_district_to_row, axis=1, args=[partition])

    print("Grouping by assignment...")
    state_grouped2 = state_shapefile.groupby("assignment")

    end_1 = timer()
    print(f"Time taken to do groupby: {end_1 - start_reock}")

    print("Now in each district in the partition...")
    for i in range(len(partition)):
        start_0 = timer()
        x_points = []
        y_points = []

        district_group = state_grouped2.get_group(i)

        group_geom = district_group.geometry
        # print(group_geom) # OK.
        nodes = partition.parts[i]
        # print(nodes) #OK, frozenset({56854, 414, 2103...})
        edge_tuples = partition["cut_edges_by_part"][i]
        # print(edge_tuples) # OK, {(737, 888), (111, 56822), .. }
        edge_tuple_extract = [i for i, j in edge_tuples] + \
            [j for i, j, in edge_tuples]
        state_boundary_nodes = [
            node for node in nodes if node in partition["boundary_nodes"]]
        # Nodes that make up the boundary of each district
        boundary_nodes = [
            node for node in nodes if node in edge_tuple_extract] + state_boundary_nodes
        # print(f"Boundary nodes: {boundary_nodes}") # OK

        end_2 = timer()
        start_1 = timer()

        for j in nodes:  # For each Census Tract in a district
            if j not in boundary_nodes:
                continue
            # Find the geometry of that Census Tract
            group_geom_j = district_group.loc[district_group['id']
                                              == j].geometry
            if group_geom_j is None:
                raise ValueError(f"tract id {j} not found")
            assert(len(group_geom_j.geom_type) == 1)
            # group_geom_j is a GeoSeries object that contains a MultiPolygon
            if 'MultiPolygon' in group_geom_j.geom_type.values:
                for multipolygon in group_geom_j:
                    for polygon in multipolygon:
                        x, y = polygon.exterior.coords.xy
                        x_points = x_points + list(x)
                        y_points = y_points + list(y)
            else:
                start_j = timer()
                exterior_points = group_geom_j.exterior.iloc[0]
                end_j = timer()
                # print(f"Time taken to find exterior point of Census Tract {j}: {end_j - start_j}")
                if exterior_points is None:  # Tract not in GEOID to ID mapping
                    raise ValueError("Tract not in GEOID to ID mapping")
                x, y = exterior_points.coords.xy  # OK
                x_points = x_points + list(x)
                y_points = y_points + list(y)

        points = list(zip(x_points, y_points))
        hull = ConvexHull(points)
        vertices = hull.vertices
        area_district = partition["area"][i]
        new_points = [points[i] for i in vertices]
        radius_bound_circle = make_circle(new_points)[2]
        area_circle = math.pi*(radius_bound_circle**2)
        reock_score = area_district/area_circle
        assert(reock_score < 1)
        dist_scores[i] = reock_score

    end_reock = timer()
    print(f"Reock scores: {dist_scores}")
    print(f"Time taken to calculate Reock scores: {end_reock - start_reock}")

    # TODO check if Reock scores are the same
    return dist_scores
"""
