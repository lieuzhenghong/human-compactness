from scipy.spatial import cKDTree
from custom_types import *
from abc import ABC, abstractmethod  # Abstract base class
from gerrychain.partition.geographic import GeographicPartition
from geopandas import GeoDataFrame, GeoSeries
import numpy as np
from timeit import default_timer as timer
from collections import defaultdict
from pointwise_libs import distance_matrix
import human_compactness_utils as hc_utils
import json
import pandas as pd


class HumanCompactness(ABC):
    def __init__(
        self, partition: GeographicPartition, points_downsampled: GeoDataFrame
    ):
        self.partition = partition
        self.points_downsampled = points_downsampled

    @abstractmethod
    def generate_tractwise_matrix(self) -> TractWiseMatrix:
        pass

    @abstractmethod
    def generate_pointwise_sum_matrix(self) -> PointWiseSumMatrix:
        pass

    @abstractmethod
    def _sum_of_knn_distances_of_all_points_in_each_district_(
        self,
    ) -> Dict[DistrictID, float]:
        """
        Calculates the sum of all KNN pairwise distances
        of all points inside each district.
        For each point inside each district,
        look for its k-nearest neighbours
        (where k is the number of points in its district)
        and take the sum of distances from it to its k-nearest neighbours.

        Returns a Dict[DistrictID, float]
        where `float` is the
        sum of all KNN-driving durations of all points in that district.
        """
        pass

    @abstractmethod
    def _sum_of_district_distances_of_all_points_in_each_district_() -> Dict[
        DistrictID, float
    ]:
        """
        Calculates the sum of all district pairwise distances
        of all points inside each district.
        For each point inside each district,
        take the sum of distances from it to all its co-districtors.
        """
        pass

    @staticmethod
    def get_points_in_each_district(
        tract_dict: Dict[TractID, TractEntry],
        tract_to_district_mapping: Dict[TractID, DistrictID],
    ) -> Dict[DistrictID, List[PointID]]:
        """
        Given a mapping of tractID to tractentry
        and a mapping of tractID to districtID,
        returns all points in each district.
        """
        points_in_each_district: Dict[DistrictID, List[PointID]] = defaultdict(list)
        for tract_id in tract_to_district_mapping:
            district_id = tract_to_district_mapping[tract_id]
            points_in_each_district[district_id] += tract_dict[tract_id]["vrps"]

        return points_in_each_district

    def calculate_human_compactness(
        self,
        tract_dict: Dict[TractID, TractEntry],
        # tract_to_district_mapping: Dict[TractID, DistrictID],
        dmx: PointWiseSumMatrix,
        M: TractWiseMatrix,
        partition: GeographicPartition,
    ) -> Dict[DistrictID, float]:
        """
        Given the Census Tract duration dict and an assignment from IDs,
        calculate the human compactness of every district in the plan

        Maintain a total sum as a tally
        Maintain an array of tracts in each district

        For each tract in assignment, check which district it comes from. Then
        add both itself and everyone else in the district to the total human
        compactness sum.
        """
        # We need this because everything else depends on partition

        self.partition = partition
        # This is the sum of driving durations from each point
        # in each district to its K nearest neighbours,
        # where K is the number of points in that district
        sum_of_knn_distances = (
            self._sum_of_knn_distances_of_all_points_in_each_district_(
                dmx, tract_dict, partition.assignment
            )
        )

        # This should be called tractwise durations
        sum_of_district_distances = (
            self._sum_of_district_distances_of_all_points_in_each_district_(M)
        )

        print(f"Total KNN DDs 2: {sum_of_knn_distances}")
        print(f"Total DDs 2: {sum_of_district_distances}")

        all_districts = set(
            [partition.assignment[tract_id] for tract_id in partition.graph.nodes]
        )
        hc_scores = {
            district_id: sum_of_knn_distances[district_id]
            / sum_of_district_distances[district_id]
            for district_id in all_districts
        }

        return hc_scores


class EDHumanCompactness(HumanCompactness):
    """
    TODO
    Implement all class methods
    Write unit tests for all class methods
    Euclidean distance human compactness
    """

    def _create_kd_tree_(self) -> cKDTree:
        kd_tree = cKDTree(
            [(point.x, point.y) for point in self.points_downsampled["geometry"]]
        )
        return kd_tree

    def _get_sum_ED_from_voter_to_knn_(voter, kd_tree: cKDTree, k: int) -> float:
        """
        Accepts a voter Point, a kd_tree, and the number of neighbours k,
        and returns a float denoting the sum of distances between
        that voter's location and its k nearest neighbours.
        """
        distances, indices = kd_tree.query(voter, k)
        print(distances)
        return sum(distances)

    def _form_tract_matrix_dd_lookup_table_(self):
        """
        Helper function that takes in a GeographicPartition
        and forms a _lookup table_ of TractIDs to matrix index.

        Used to lookup the TractWiseMatrix generated by
        _generate_tractwise_dd_matrix.
        """
        tract_list: List[TractID] = list(self.partition.graph.nodes)
        assert sorted(tract_list) == tract_list

        # form the lookup table
        lookup_table: Dict[TractID, int] = {}
        for i, tract_id in enumerate(tract_list):
            lookup_table[tract_id] = i

        return lookup_table

    def generate_tractwise_matrix(
        self,
        tract_dict: Dict[TractID, TractEntry],
        tract_to_district_mapping: Dict[TractID, DistrictID],
    ) -> TractWiseMatrix:
        """
        TODO

        Forms a TractWiseMatrix from a kd_tree and a tract dict.

        1. For each tract, find all the points in it.
        2. Use a helper function to find the sum of pairwise distances between all of these points.
        3. Return the matrix.
        """
        pass

    def generate_pointwise_sum_matrix(self, K: int) -> PointWiseSumMatrix:
        """
        Builds the pointwise sum matrix
        Returns the PointWiseSumMatrix for euclidean distance
        This is a very slow function and should be run only once
        Save this to disk
        """
        kd_tree = self._create_kd_tree_()
        ddf = pd.DataFrame()
        ddf[0] = pd.Series(np.zeros(self.points_downsampled.shape[0]))
        for k in range(2, K + 1):
            print(k)
            # we need to add this to a column
            # so this is a series
            column_k = self.points_downsampled["geometry"].apply(
                self._get_sum_ED_from_voter_to_knn_,
                args=[kd_tree, k],
            )
            ddf[k] = column_k

        print(ddf)
        dmx: PointWiseSumMatrix = ddf.to_numpy()
        return dmx

    def _calculate_knn_of_points_(
        self, dmx: PointWiseSumMatrix, point_ids: List[PointID]
    ) -> float:
        K = len(point_ids)
        assert K < 3000
        return sum([dmx[point][K] for point in point_ids])

    def _sum_of_knn_distances_of_all_points_in_each_district_(
        self,
        dmx: PointWiseSumMatrix,
        tract_dict: Dict[TractID, TractEntry],
        tract_to_district_mapping: Dict[TractID, DistrictID],
    ) -> Dict[DistrictID, float]:
        """
        Calculates the sum of all KNN pairwise distances
        of all points inside each district.
        For each point inside each district,
        look for its k-nearest neighbours
        (where k is the number of points in its district)
        and take the sum of distances from it to its k-nearest neighbours.

        Returns a Dict[DistrictID, float]
        where `float` is the
        sum of all KNN-driving durations of all points in that district.
        """
        sum_of_knn_distances_in_each_district = defaultdict(float)

        points_in_each_district = HumanCompactness.get_points_in_each_district(
            tract_dict, tract_to_district_mapping
        )

        for (district_id, point_ids) in points_in_each_district.items():
            sum_of_knn_distances_in_each_district[
                district_id
            ] = self._calculate_knn_of_points_(dmx, point_ids)

        return sum_of_knn_distances_in_each_district

    def _sum_of_distances_of_all_points_in_list_(
        self, point_ids: List[PointID]
    ) -> float:
        """
        Helper function
        """
        # FIXME -- should be converted to a different coordinate system
        # before doing distance
        result = 0
        start = timer()
        points_in_list = self.points_downsampled.iloc[point_ids]

        for i, p1 in enumerate(point_ids):
            for j, p2 in enumerate(point_ids):
                # print(p1, p2)
                # print(points_in_list["geometry"].iloc[i])
                # print(points_in_list["geometry"].iloc[j])
                # print("Yo!")
                result += (points_in_list["geometry"].iloc[i]).distance(
                    points_in_list["geometry"].iloc[j]
                )

        print(result)
        end = timer()
        print(f"Time taken to sum distances for one district: {end-start}")
        return result

    def _sum_of_district_distances_of_all_points_in_each_district_(
        self,
        tract_dict: Dict[TractID, TractEntry],
        tract_to_district_mapping: Dict[TractID, DistrictID],
    ) -> Dict[DistrictID, float]:
        """
        Calculates the sum of all district pairwise distances
        of all points inside each district.
        For each point inside each district,
        take the sum of distances from it to all its co-districtors.
        """
        result: Dict[DistrictID, float] = {}
        points_in_each_district = HumanCompactness.get_points_in_each_district(
            tract_dict, tract_to_district_mapping
        )

        start = timer()
        for (district_id, point_ids) in points_in_each_district.items():
            result[district_id] = self._sum_of_distances_of_all_points_in_list_(
                point_ids
            )
        end = timer()
        print(
            f"Time taken to sum distances of all points in all districts: {end-start}"
        )
        return result
