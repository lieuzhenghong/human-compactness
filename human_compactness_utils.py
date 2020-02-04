import json


def duration_between(tract_id, other_id, duration_dict):
    '''Gets the sum of driving durations between one tract and another'''

    tract_id = str(tract_id)
    other_id = str(other_id)

    if tract_id not in duration_dict:
        # Don't raise value error. Some tracts have no points in them
        return 0
    elif other_id not in duration_dict[tract_id]:
        return 0
    else:
        return duration_dict[tract_id][other_id]


# TODO
def calculate_knn_of_all_tracts_in_partition(duration_dict, partition):
    '''
    First run through the districts' tracts and get the points in that district
    (form a list of points) by aggregating points in all tracts in the district.

    Then count the number of points in each district. This is that district's k.

    Read the duration_dict line by line.
    Each line corresponds to a point: find which district that point
    belongs to (if any --- check this), then get the k-nearest-neighbours

    It might be helpful instead of reading the same file at every single step,
    try to memoise, save it down somewhere...

    Really the problem is that the duration dict doesn't fit in memory.
    We can use heuristics to do something like double the size at every
    iteration but I think that's too complicated.
    '''

    # Ask Mark or Zun Yuan about this. We know file read is slow.
    pass


def calculate_human_compactness(duration_dict, knn_dd_dict, partition):
    '''
    Given the Census Tract duration dict and an assignment from IDs,
    calculate the human compactness of every district in the plan

    The duration dict is in the following format:
        {
            tractid: {tractid: distance, ... },
            tractid: {tractid: distance, ...},
            ...
        }

    The KNN dict is in the following format:
        {
            tractid: Float,
            tractid: Float
            ...
        }
The assignment dict is in the following format:
        {
            tractid: districtid
            tractid: districtid
            ...
        }

    Maintain a total sum as a tally
    Maintain an array of tracts in each district

    For each tract in assignment, check which district it comes from. Then
    add both itself and everyone else in the district to the total human
    compactness sum.
    '''

    # O(n^2) runtime

    total_durations = {}
    total_knn_dds = {}
    tracts_in_districts = {}
    all_districts = set([])

    hc_scores = {}

    for tract_id in partition.graph.nodes:
        district_id = partition.assignment[tract_id]
        all_districts.add(district_id)

        # Fill up dictionary of tracts in a specific district
        if district_id not in tracts_in_districts:
            tracts_in_districts[district_id] = [tract_id]
        else:
            tracts_in_districts[district_id].append(tract_id)

        # Add to the total duration sum. Notice we append to
        # tracts_in_districts first: this is so that we get the sum of driving
        # distances from a tract to itself as well, which makes sense

        for other_tract_id in tracts_in_districts[district_id]:
            if district_id not in total_durations:
                total_durations[district_id] = duration_between(
                    tract_id, other_tract_id, duration_dict)
            else:
                total_durations[district_id] += duration_between(
                    tract_id, other_tract_id, duration_dict)

    # Now we've got the total durations, divide by the sum of all
    # the knns. We have the sums by tract: all that remains is to
    # aggregate by district.

    for district_id in all_districts:
        for tract_id in tracts_in_districts[district_id]:
            if district_id not in total_knn_dds:
                try:
                    total_knn_dds[district_id] = knn_dd_dict[str(tract_id)]
                except KeyError:  # Some tracts have no points in them
                    pass
            else:
                try:
                    total_knn_dds[district_id] += knn_dd_dict[str(tract_id)]
                except KeyError:
                    pass

    # OK, so now we have the sum of point-to-point driving
    # durations in a district, and also the sum of KNN dds
    # in a district. Last step is to divide knn_dd by total_durations
    # to get the final human compactness score.

    print(f"Total KNN DDs: {total_knn_dds}")
    print(f"Total DDs in district: {total_durations}")

    for district_id in all_districts:
        hc_scores[district_id] = total_knn_dds[district_id] / \
            total_durations[district_id]

    print(f"HC scores: {hc_scores}")

    return hc_scores


def calc_knn_sum_durations_by_tract(pttm, N, DM_PATH, SAVE_FILE_TO):
    '''Returns a dictionary and prints a file of 
    {
        tractid: Float
    }
    where the value is the sum of k-nearest-neighbour driving durations for
    each point in the tract'''
    knn_sum_dd_by_tract = {}

    # First populate with tracts and initialise to 0

    for p in pttm:
        knn_sum_dd_by_tract[pttm[p]] = 0

    # I know I'm violating DRY here, but refactoring would take too much time
    with open(DM_PATH, 'rt') as fh:
        line = fh.readline()
        # This is currently looking at the durations from point i to all other points
        i = 0
        while line:
            # Get the distances from point i; two spaces is not a typo
            dist = [float(x) for x in line.split('  ')]

            # Very rarely, points may not lie within tracts. This is strange, but we'll ignore it
            print(f'Now processing line {i}..')
            if i not in pttm:
                print(f'Point ID not in point_to_tract_mapping: {i}')
            else:
                # We want to get the nearest N neighbours, but at
                # the same time we want to make sure the tracts are in
                # the point-to-tract mapping.

                # So we sort, but maintain the index
                # enumerate gives a enumeration giving indexes and values
                # key=lambda i:i[1] sorts based on the original values

                sorted_dist = [i for i in sorted(
                    enumerate(dist), key=lambda a:a[1])]

                num_neighbours = 0
                j = 0

                while num_neighbours < N:
                    if j not in pttm:
                        print(f'Point ID not in point_to_tract_mapping: {j}')
                    else:
                        knn_sum_dd_by_tract[pttm[i]] += sorted_dist[j][1]
                        num_neighbours += 1
                    j += 1

                print(
                    f"Sum of KNN distances for point {i} in tract {pttm[i]}: {knn_sum_dd_by_tract[pttm[i]]}")
            i += 1
            line = fh.readline()

    with open(f'{SAVE_FILE_TO}', 'w') as f:
        f.write(json.dumps(knn_sum_dd_by_tract))

    return knn_sum_dd_by_tract


def convert_point_distances_to_tract_distances(pttm, DM_PATH, SAVE_FILE_TO):
    '''Returns a JSON file giving driving durations from all points in the Census Tract
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
    '''
    tract_distances = {}

    with open(DM_PATH, 'rt') as fh:
        line = fh.readline()
        # This is currently looking at the durations from point i to all other points
        i = 0
        while line:
            # Get the distances from point i; two spaces is not a typo
            dist = [float(x) for x in line.split('  ')]
            # Very rarely, points may not lie within tracts. This is strange, but we'll ignore it
            print(f'Now processing line {i}..')
            if i not in pttm:
                print(f'Point ID not in point_to_tract_mapping: {i}')
            # Otherwise, update the tract-pairwise-distance matrix with the pointwise distances
            else:
                for j in range(len(dist)):
                    if j not in pttm:
                        print(f'Point ID not in point_to_tract_mapping: {j}')
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
    with open(f'{SAVE_FILE_TO}', 'w') as f:
        f.write(json.dumps(tract_distances))


def read_tract_duration_json(DD_PATH):
    with open(DD_PATH) as f:
        return(json.load(f))
