from scipy.spatial import cKDTree
from custom_types import *
from abc import ABC, abstractmethod  # Abstract base class
from gerrychain.partition.geographic import GeographicPartition
from geopandas import GeoDataFrame
import numpy as np
from timeit import default_timer as timer
from collections import defaultdict
from pointwise_libs import distance_matrix
import human_compactness_utils as hc_utils
import json


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
    """

    def _create_kd_tree_(self) -> cKDTree:
        kd_tree = cKDTree([(point.x, point.y) for point in df["geometry"]])
        return kd_tree

    def _get_sum_ED_from_voter_to_knn_(voter, kd_tree: cKDTree, k: int) -> float:
        """
        Accepts a voter Point, a kd_tree, and the number of neighbours k,
        and returns a float denoting the sum of distances between
        that voter's location and its k nearest neighbours.
        """
        distances, indices = kd_tree.query(voter, k)
        return sum(distances)

    def generate_tractwise_matrix() -> TractWiseMatrix:
        pass

    def generate_pointwise_sum_matrix() -> PointWiseSumMatrix:
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

    def _sum_of_knn_distances_of_all_points_in_each_district_(
        self,
    ) -> Dict[DistrictID, float]:
        sum_of_knn_distances_in_each_district: Dict[DistrictID, float] = defaultdict(
            float
        )

        for (district_id, point_ids) in points_in_each_district.items():
            sum_of_knn_distances_in_each_district[district_id] = sum(
                [sum_of_eds_from_point_to_knn[pointid] for pointid in point_ids]
            )

        return sum_of_knn_distances_in_each_district

    def _sum_of_district_distances_of_all_points_in_each_district_() -> Dict[
        DistrictID, float
    ]:
        pass


class DDHumanCompactness(HumanCompactness):
    """
    Driving duration human compactness
    """

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

    def _duration_between_(
        self, tract_id: TractID, other_id: TractID, duration_dict: DurationDict
    ):
        """Gets the sum of driving durations between one tract and another"""

        # print(f'Getting the driving duration between {tract_id} and {other_id}')
        s_tract_id = str(tract_id)
        s_other_id = str(other_id)
        # Note we can't simply return duration_dict[s_tract_id][s_other_id]
        # because of the possibility of zeros: some tracts have no points in them
        row = duration_dict.get(s_tract_id, None)
        if row:
            return row.get(s_other_id, 0)
        return 0

    def _generate_duration_dict_(self, pttm, DM_PATH, SAVE_FILE_TO) -> DurationDict:
        # TODO Try to refactor this away
        """Returns a JSON file giving driving durations from all points in the Census Tract
        to all other points in every other Census Tract.
        Takes in three things:

            1. A mapping from points to tracts (Dict[PointId : TractId]
            2. The distance matrix file path
            3. The path to save the output tract distance file to

        Reads line by line
        Returns a JSON file with the following schema:
        {
            tractid: {tractid: distance, ... },
            tractid: {tractid: distance, ...},
            ...
        }
        Each entry in the dictionary is the sum of driving durations from each point in
        the tract to each other point in the tract.

        Note that the duration from tract_id to tract_id can (in fact is almost always nonzero)
        because it measures the sum of durations from all points in the tract
        """
        tract_distances = {}

        with open(DM_PATH, "rt") as fh:
            line = fh.readline()
            # This is currently looking at the durations from point i to all other points
            i = 0
            while line:
                # Get the distances from point i; two spaces is not a typo
                dist = [float(x) for x in line.split("  ")]
                # Very rarely, points may not lie within tracts. This is strange, but we'll ignore it
                print(f"Now processing line {i}..")
                if i not in pttm:
                    print(f"Point ID not in point_to_tract_mapping: {i}")
                # Otherwise, update the tract-pairwise-distance matrix with the pointwise distances
                else:
                    for j in range(len(dist)):
                        if j not in pttm:
                            print(f"Point ID not in point_to_tract_mapping: {j}")
                        elif pttm[i] not in tract_distances:
                            tract_distances[pttm[i]] = {pttm[j]: dist[j]}
                        elif pttm[j] not in tract_distances[pttm[i]]:
                            tract_distances[pttm[i]][pttm[j]] = dist[j]
                        else:
                            tract_distances[pttm[i]][pttm[j]] += dist[j]
                        # print(tract_distances)
                i += 1
                line = fh.readline()
        # Save tract matrix to file
        with open(f"{SAVE_FILE_TO}", "w") as f:
            f.write(json.dumps(tract_distances))

        duration_dict = hc_utils.read_tract_duration_json(SAVE_FILE_TO)
        return duration_dict

    def generate_tractwise_matrix(
        self, tract_list: List[TractID], duration_dict: DurationDict
    ) -> TractWiseMatrix:
        """
        Helper function that takes a list of TractIDs
        and a DurationDict and forms a NxN matrix
        where M[i][j] is the driving duration from
        TractID of id a, and TractID of id b
        where i = lookup_table[a] and j = lookup_table[b].

        Should be used with _form_tract_matrix_dd_lookup_table
        """

        num_tracts = len(tract_list)

        start = timer()
        M = [[] for i in range(num_tracts)]
        for i in range(num_tracts):
            for j in range(num_tracts):
                M[i].append(
                    self._duration_between_(tract_list[i], tract_list[j], duration_dict)
                )

        M = np.array(M)
        end = timer()
        print(f"Time taken to generate tractwise duration matrix: {end-start}")

        return M

    def generate_pointwise_sum_matrix(
        self, DM_PATH, SAVE_FILE_TO
    ) -> PointWiseSumMatrix:
        """
        Given a point matrix in DM_PATH, builds and saves a knn_sum_duration
        matrix to parameter SAVE_FILE_TO, where matrix[i][j] is the sum of
        distances from point i to its j closest neighbours.
        """
        with open(DM_PATH, "rt") as fh:
            with open(f"{SAVE_FILE_TO}", "w") as outfile:
                line = fh.readline()
                # This is currently looking at the durations from point i to all other points
                i = 0
                while line:
                    # Get the distances from point i; two spaces is not a typo
                    dist = [float(x) for x in line.split("  ")]
                    dd_sum = []

                    if i % 1000 == 0:
                        print(f"Now processing line {i}..")

                    sorted_dist = sorted(dist)
                    j = 0
                    while j < K:
                        if j == 0:
                            dd_sum.append(sorted_dist[0])
                        else:
                            dd_sum.append(dd_sum[-1] + sorted_dist[j])
                        j += 1

                    # print(sorted_dist[:50])
                    # print(dd_sum[:50])
                    outfile.writelines([f" {x:.2f} " for x in dd_sum])
                    outfile.write("\n")
                    i += 1
                    line = fh.readline()
                dmx = distance_matrix.read_duration_matrix(f"{SAVE_FILE_TO}")
                return dmx

    def _calculate_knn_of_points_(
        self, dmx: PointWiseSumMatrix, point_ids: List[PointID]
    ) -> float:
        """
        Helper function to look up the KNN of points
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
        sum_of_knn_distances_in_each_district: Dict[DistrictID, float] = defaultdict(
            float
        )
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
