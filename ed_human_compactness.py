from scipy.spatial import cKDTree
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
from human_compactness import HumanCompactness


class EDHumanCompactness(HumanCompactness):
    """
    TODO
    Implement all class methods
    Write unit tests for all class methods
    Euclidean distance human compactness
    """

    def _create_kd_tree_(self) -> cKDTree:
        p_converted: GeoDataFrame = self.points_downsampled.to_crs("ESRI:102010")
        kd_tree = cKDTree([(point.x, point.y) for point in p_converted["geometry"]])
        return kd_tree

    def _get_sum_ED_from_voter_to_knn_(self, voter, kd_tree: cKDTree, k: int) -> float:
        """
        Accepts a voter Point, a kd_tree, and the number of neighbours k,
        and returns a float denoting the sum of distances between
        that voter's location and its k nearest neighbours.
        """
        distances, _ = kd_tree.query(voter, k)  # distances are sorted
        # print(distances, indices)
        return distances

    def _sum_of_distances_between_two_lists_of_points_(
        self, point_ids_1: List[PointID], point_ids_2: List[PointID]
    ) -> float:
        """
        Helper function that calculates the sum of distances between two lists of PointIDs
        """
        # FIXME -- should be converted to a different coordinate system
        # before doing distance
        result = 0
        p1s = self.points_downsampled.iloc[point_ids_1]["geometry"]
        p2s = self.points_downsampled.iloc[point_ids_2]["geometry"]
        # print(p1s)
        # print(p2s)

        for i, p1 in enumerate(point_ids_1):
            for j, p2 in enumerate(point_ids_2):
                result += p1s.iloc[i].distance(p2s.iloc[j])

        return result

    def generate_tractwise_matrix(
        self,
        tract_dict: Dict[TractID, TractEntry],
    ) -> TractWiseMatrix:
        """
        Forms a TractWiseMatrix from a kd_tree and a tract dict.

        1. For each tract, find all the points in it.
        2. Use a helper function to find the sum of pairwise distances between all of these points.
        3. Return the matrix.

        Use only with the lookup table.
        """
        self.points_downsampled = self.points_downsampled.to_crs("ESRI:102010")
        tract_list: List[TractID] = list(self.partition.graph.nodes)
        assert sorted(tract_list) == tract_list
        start = timer()

        num_tracts = len(tract_list)

        M = [[] for i in range(num_tracts)]
        for i in range(num_tracts):
            start_i = timer()
            for j in range(num_tracts):
                M[i].append(
                    self._sum_of_distances_between_two_lists_of_points_(
                        tract_dict[tract_list[i]]["vrps"],
                        tract_dict[tract_list[j]]["vrps"],
                    )
                )
            end_i = timer()
            print(f"Tract {i} of {num_tracts}: {end_i - start_i}")

        M = np.array(M)
        end = timer()
        print(f"Time taken to generate tractwise duration matrix: {end-start}")

        self.points_downsampled = self.points_downsampled.to_crs("EPSG:4326")
        return M

    def generate_pointwise_sum_matrix(self, K: int) -> PointWiseSumMatrix:
        """
        Builds the pointwise sum matrix
        Returns the PointWiseSumMatrix for euclidean distance
        This is a very slow function and should be run only once
        Save this to disk
        """
        self.points_downsampled = self.points_downsampled.to_crs("ESRI:102010")
        kd_tree: cKDTree = self._create_kd_tree_()

        dmk = self.points_downsampled["geometry"].apply(
            self._get_sum_ED_from_voter_to_knn_,
            args=[kd_tree, K],
        )

        def sum_column(l):
            from functools import reduce

            a = [0]
            for index, ele in enumerate(l):
                a.append(a[index] + ele)

            return a[1:]

        dmx = dmk.apply(
            sum_column,
        )

        dmx = dmx.apply(pd.Series)

        dmx: PointWiseSumMatrix = dmx.to_numpy()
        self.points_downsampled = self.points_downsampled.to_crs("EPSG:4326")
        return dmx

    def save_ed_tractwise_matrix(
        self, tract_dict: TractDict, save_file_to: str
    ) -> TractWiseMatrix:
        """"""
        matrix = self.generate_tractwise_matrix(tract_dict)
        self.tractwise_matrix = matrix
        np.save(save_file_to, matrix)
        return matrix

    def save_ed_pointwise_sum_matrix(self, save_file_to: str) -> PointWiseMatrix:
        matrix = self.generate_pointwise_sum_matrix(3000)
        self.pointwise_sum_matrix = matrix
        np.save(save_file_to, matrix)
        return matrix

    def read_ed_tractwise_matrix(self, file_location: str) -> TractWiseMatrix:
        matrix = np.load(file_location)
        self.tractwise_matrix = matrix
        return matrix

    def read_ed_pointwise_sum_matrix(self, file_location: str) -> PointWiseMatrix:
        matrix = np.load(file_location)
        self.pointwise_sum_matrix = matrix
        return matrix
