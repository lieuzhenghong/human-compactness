from custom_types import *
from abc import ABC, abstractmethod  # Abstract base class
from gerrychain.partition.geographic import GeographicPartition
from geopandas import GeoDataFrame, GeoSeries
import numpy as np
from timeit import default_timer as timer
from collections import defaultdict
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

    @abstractmethod
    def _form_tract_matrix_dd_lookup_table_():
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

    def _calculate_knn_of_points_(
        self, dmx: PointWiseSumMatrix, point_ids: List[PointID]
    ) -> float:
        """
        Helper function that calculates the sum of distances
        from each point in point_ids to its K-nearest neighbours.
        Takes in a PointWiseSumMatrix and a list of PointIDs
        and returns the double sum:
        the sum over all point IDs
            over the sum of each point's K-nearest neighbours
        """
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
        1. Creates a District -> List[PointID] mapping.
        2. For each point in each district, calculate the sum of driving durations
        from that point to its K nearest neighbours, where K is the number of points
        in that district.
        """
        sum_of_knn_distances_in_each_district = defaultdict(float)
        points_in_each_district: Dict[
            DistrictID, List[PointID]
        ] = HumanCompactness.get_points_in_each_district(
            tract_dict, tract_to_district_mapping
        )

        start_knn = timer()
        for (district_id, point_ids) in points_in_each_district.items():
            sum_of_knn_distances_in_each_district[
                district_id
            ] = self._calculate_knn_of_points_(dmx, point_ids)
        end_knn = timer()
        print(
            f"Time taken to calculate KNN for all points in current district assignment: {end_knn - start_knn}"
        )

        return sum_of_knn_distances_in_each_district

    def _sum_of_district_distances_of_all_points_in_each_district_(
        self,
        M: TractWiseMatrix,
    ) -> Dict[DistrictID, float]:
        """
        Calculates the sum of all district pairwise distances
        of all points inside each district.
        For each point inside each district,
        take the sum of distances from it to all its co-districtors.
        1. Make the lookup table
        2. Use the TractWise matrix (N x N) matrix giving the pairwise sum
        of distances from each tract to another
        3. For each district:
            - Form a smaller tractwise matrix (MxM) of _only_ the tracts
            that are in this district
            - Sum all these values
        """
        tracts_in_districts: Dict[DistrictID, List[TractID]] = defaultdict(list)
        total_durations: Dict[DistrictID, float] = defaultdict(float)

        lookup_table = self._form_tract_matrix_dd_lookup_table_()

        tract_list: List[TractID] = list(self.partition.graph.nodes)

        # form the numpy matrix

        # Generate the mapping of Dict[DistrictID, List[TractID]]
        for tract_id in self.partition.graph.nodes:
            district_id = self.partition.assignment[tract_id]
            tracts_in_districts[district_id].append(tract_id)

        start = timer()
        for district_id, tractIDs in tracts_in_districts.items():
            # M is a NxN matrix
            matrixTractIDs = [lookup_table[tractID] for tractID in tractIDs]
            A = M[matrixTractIDs]  # (166, 815)
            sq = np.apply_along_axis(
                lambda row: row[matrixTractIDs], 1, A
            )  # (166, 166)
            total_durations[district_id] = np.sum(sq)
        end = timer()

        print(f"Time taken to do the square matrix shit: {end-start}")

        return total_durations

    def calculate_human_compactness(
        self,
        tract_dict: Dict[TractID, TractEntry],
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
                dmx, tract_dict, dict(partition.assignment)
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
