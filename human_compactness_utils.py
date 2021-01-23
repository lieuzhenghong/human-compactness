import json
from timeit import default_timer as timer

from typing import List, Dict
from gerrychain.partition.geographic import GeographicPartition
from typing_extensions import TypedDict
from collections import defaultdict

# TODO check these types!!!
DistrictID = int
TractID = int
TractIDStr = str
GeoID = str
PointID = int


class TractEntry(TypedDict):
    geoid: GeoID
    pop: int
    pfs: List[float]  # Principal factors (for PCA)
    vrps: List[PointID]


def duration_between(
    tract_id: TractID,
    other_id: TractID,
    duration_dict: Dict[TractIDStr, Dict[TractIDStr, float]],
):
    """Gets the sum of driving durations between one tract and another"""

    # print(f'Getting the driving duration between {tract_id} and {other_id}')

    tract_id = str(tract_id)
    other_id = str(other_id)

    if tract_id not in duration_dict:
        # Don't raise value error. Some tracts have no points in them
        # print(f'Tract_id {tract_id} not in duration dictionary')
        return 0
    elif other_id not in duration_dict[tract_id]:
        # print(f'{tract_id} doesn\'t have {other_id} in its duration dictionary')
        return 0
    else:
        return duration_dict[tract_id][other_id]


def generate_tract_matrix() -> List[List[int]]:
    """
    TODO
    """
    matrix = [[]]
    return matrix


def calculate_knn_of_all_points_in_district_new(
    district_id: DistrictID,
    district_to_tract_mapping: Dict[DistrictID, List[TractID]],
    tract_dict: Dict[TractID, TractEntry],
    tract_duration_matrix: List[List[int]],
) -> float:
    """
    TODO
    Calculate the sum of travel durations for every point
    to its K-nearest neighbours in the district.
    """
    sum_of_all_knns_in_district = 0

    tracts = district_to_tract_mapping[district_id]
    # The following line is a bit dubious... FIXME
    k = sum([tract_dict[tract_id]["pop"] for tract_id in tracts])

    for tract_id in tracts:
        sum_of_all_knns_in_district += tract_duration_matrix[tract_id][k]

    return sum_of_all_knns_in_district


def _calculate_knn_of_points(dmx, point_ids: List[PointID]) -> float:
    """
    Helper function to look up the KNN of points
    """
    K = len(point_ids)
    assert K < 3000
    return sum([dmx[point][K] for point in point_ids])


def calculate_knn_of_all_points_in_district(
    dmx,
    tract_dict: Dict[TractID, TractEntry],
    tract_to_district_mapping: Dict[TractID, DistrictID],
) -> Dict[DistrictID, float]:
    """
    Calculates the sum of driving durations
    from each point in each district
    to its K nearest neighbours,
    where K is the number of points in that district.

    Returns a Dict[DistrictID, float]
    where `float` is the
    sum of all KNN-driving durations of all points in that district.

    1. Creates a District -> List[PointID] mapping.
    2. For each point in each district, calculate the sum of driving durations
       from that point to its K nearest neighbours, where K is the number of points
       in that district.
    """
    sum_of_knn_distances_in_each_district: Dict[DistrictID, float] = defaultdict(float)
    points_in_each_district: Dict[DistrictID, List[PointID]] = defaultdict(list)

    for tract_id in tract_to_district_mapping:
        district_id = tract_to_district_mapping[tract_id]
        points_in_each_district[district_id] += tract_dict[tract_id]["vrps"]

    start_knn = timer()
    for (district_id, point_ids) in points_in_each_district.items():
        sum_of_knn_distances_in_each_district[district_id] = _calculate_knn_of_points(
            dmx, point_ids
        )
    end_knn = timer()
    print(
        f"Time taken to calculate KNN for all points in current district assignment: {end_knn - start_knn}"
    )

    return sum_of_knn_distances_in_each_district


def _calculate_pairwise_durations_(partition, duration_dict, tract_dict):
    total_durations: Dict[DistrictID, float] = defaultdict(float)
    tracts_in_districts: Dict[DistrictID, List[TractID]] = defaultdict(list)

    start = timer()
    print(f"Number of tracts: {len(partition.graph.nodes)}")
    print(f"Type of tracts: {type(partition.graph.nodes)}")
    print(f"Min tract ID: {min(partition.graph.nodes)}")
    print(f"Max tract ID: {max(partition.graph.nodes)}")

    print(f"Size of duration dict: {len(duration_dict)}")
    print(f"Size of tract dict: {len(tract_dict)}")

    for tract_id in partition.graph.nodes:
        district_id = partition.assignment[tract_id]
        district_tracts = tracts_in_districts[district_id]

        # Append each tract to the list of tracts that have been assigned to district
        district_tracts.append(tract_id)
        # Add to the total duration sum. Notice we append to
        # tracts_in_districts first:
        # this is so that we get the sum of
        # driving distances from a tract to itself as well, which makes sense
        # print(f"Getting pairwise distances between {tract_id} and {district_tracts}")

        result = 0
        for other_tract_id in district_tracts:
            result += duration_between(tract_id, other_tract_id, duration_dict)
            result += duration_between(other_tract_id, tract_id, duration_dict)
        total_durations[district_id] += result

        """
        for other_tract_id in district_tracts:
            total_durations[district_id] += duration_between(
                tract_id, other_tract_id, duration_dict
            )
            total_durations[district_id] += duration_between(
                other_tract_id, tract_id, duration_dict
            )
        """

        # We've double-counted the last self-distance: subtract away
        assert len(district_tracts)
        last_tract_id = district_tracts[-1]
        assert tract_id == last_tract_id
        total_durations[district_id] -= duration_between(
            last_tract_id, tract_id, duration_dict
        )

    end = timer()
    print(
        f"Time taken to get pairwise durations between all points in the district: {end-start}"
    )
    return total_durations


def calculate_human_compactness(
    duration_dict: Dict[TractIDStr, Dict[TractIDStr, float]],
    tract_dict: Dict[TractID, TractEntry],
    dmx,
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

    total_durations = _calculate_pairwise_durations_(
        partition, duration_dict, tract_dict
    )

    # Now we've got the total durations, divide by the sum of all
    # the knns. We have the sums by tract: all that remains is to
    # aggregate by district.
    start = timer()

    total_knn_dds = calculate_knn_of_all_points_in_district(
        dmx, tract_dict, partition.assignment
    )

    end = timer()

    print(f"Time taken to get KNN durations: {end-start}")

    # OK, so now we have the sum of point-to-point driving
    # durations in a district, and also the sum of KNN dds
    # in a district. Last step is to divide knn_dd by total_durations
    # to get the final human compactness score.

    # print(f"Total KNN DDs: {total_knn_dds}")
    # print(f"Total DDs in district: {total_durations}")

    # Get all districts
    start = timer()
    all_districts = set([])
    for tract_id in partition.graph.nodes:
        district_id = partition.assignment[tract_id]
        all_districts.add(district_id)
    end = timer()
    print(f"Time taken to fill up all_districts: {end-start}")

    start = timer()
    hc_scores: Dict[DistrictID, float] = defaultdict(float)
    for district_id in all_districts:
        hc_scores[district_id] = (
            total_knn_dds[district_id] / total_durations[district_id]
        )

    # print(f"HC scores: {hc_scores}")
    end = timer()
    print(f"Time taken to do the division: {end-start}")

    return hc_scores


def build_knn_sum_duration_matrix(K, DM_PATH, SAVE_FILE_TO):
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


def convert_point_distances_to_tract_distances(pttm, DM_PATH, SAVE_FILE_TO):
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


def read_tract_duration_json(DD_PATH):
    with open(DD_PATH) as f:
        return json.load(f)
