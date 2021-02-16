from typing import Dict
from scipy.spatial import cKDTree
import geopandas as gpd
from shapely.geometry import Point
import numpy as np
from custom_types import *
from typing import List, Dict, TypedDict, Any
from human_compactness_utils import get_points_in_each_district
from gerrychain.partition.geographic import GeographicPartition
from collections import defaultdict
import pandas as pd


def create_kd_tree(df: gpd.GeoDataFrame):
    kd_tree = cKDTree([(point.x, point.y) for point in df["geometry"]])
    return kd_tree


def _generate_tractwise_ed_matrix_(
    tract_dict: Dict[TractID, TractEntry], kd_tree: cKDTree
) -> TractWiseMatrix:
    """
    TODO
    """
    """
    num_tracts = len(tract_dict)

    start = timer()
    M = [[] for i in range(num_tracts)]
    for i in range(num_tracts):
        for j in range(num_tracts):
            p1: Point = ...[i]
            p2: Point = ...[j]
            M[i].append(p1.distance(p2))

    M = np.array(M)
    end = timer()
    print(f"Time taken to generate tractwise euclidean distance matrix: {end-start}")
    return M
    """


def _get_sum_ED_from_voter_to_knn_(voter, kd_tree: cKDTree, k: int) -> float:
    """
    Accepts a voter Point, a kd_tree, and the number of neighbours k,
    and returns a float denoting the sum of distances between
    that voter's location and its k nearest neighbours.
    """
    distances, indices = kd_tree.query(voter, k)
    return sum(distances)


def _build_knn_sum_duration_matrix_(K, points_downsampled) -> PointWiseSumMatrix:
    """
    We want this to build the pointwise sum matrix
    Returns the PointWiseSumMatrix for euclidean distance
    This is a very slow function and should be run only once
    Save this to disk
    """
    kd_tree = create_kd_tree(points_downsampled)
    ddf = pd.DataFrame()
    ddf[0] = pd.Series(np.zeros(points_downsampled.shape[0]))
    for k in range(2, K + 1):
        print(k)
        # we need to add this to a column
        # so this is a series
        column_k = points_downsampled["geometry"].apply(
            _get_sum_ED_from_voter_to_knn_,
            args=[kd_tree, k],
        )
        ddf[k] = column_k

    print(ddf)
    dmx: PointWiseSumMatrix = ddf.to_numpy()
    return dmx


def _get_sum_of_knn_distances_in_each_district_(
    sum_of_eds_from_point_to_knn: Dict[PointID, float],
    points_in_each_district: Dict[DistrictID, List[PointID]],
):
    sum_of_knn_distances_in_each_district: Dict[DistrictID, float] = defaultdict(float)

    for (district_id, point_ids) in points_in_each_district.items():
        sum_of_knn_distances_in_each_district[district_id] = sum(
            [sum_of_eds_from_point_to_knn[pointid] for pointid in point_ids]
        )

    return sum_of_knn_distances_in_each_district
