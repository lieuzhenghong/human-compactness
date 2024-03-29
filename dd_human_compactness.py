from human_compactness import HumanCompactness
from custom_types import *
from timeit import default_timer as timer
import numpy as np
import human_compactness_utils as hc_utils
import json
from pointwise_libs import distance_matrix
from collections import defaultdict


class DDHumanCompactness(HumanCompactness):
    """
    Driving duration human compactness
    """

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

        self.tractwise_matrix = M
        return M

    def generate_pointwise_sum_matrix(
        self, DM_PATH, SAVE_FILE_TO
    ) -> PointWiseSumMatrix:
        """
        TODO refactor this so as not to have side effects
        Given a point matrix in DM_PATH, builds and saves a knn_sum_duration
        matrix to parameter SAVE_FILE_TO, where matrix[i][j] is the sum of
        distances from point i to its j closest neighbours.
        """
        K = 3000
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
                self.pointwise_sum_matrix = dmx
                return dmx
