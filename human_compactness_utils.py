def duration_between(tract_id, other_id, duration_dict):
    '''Gets the sum of driving durations between one tract and another'''
    if tract_id not in duration_dict:
        raise TractNotFoundError
    elif other_id not in duration_dict[tract_id]:
        raise TractNotFoundError
    else:
        return duration_dict[tract_id][other_id]


def calculate_human_compactness(assignment, duration_dict)
    '''
    Given the Census Tract duration dict and an assignment from IDs,
    calculate the human compactness of every district in the plan

    The duration dict is in the following format:
        {
            tractid: {tractid: distance, ... },
            tractid: {tractid: distance, ...},
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
    tracts_in_districts = {}

    for tract_id in assignments:
            district_id = assignments[tract_id]

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
                        tract_id, other_tract_id)
                else:
                    total_durations[district_id] += duration_between(
                        tract_id, other_tract_id)
        return total_durations


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
                pass
            # Otherwise, update the tract-pairwise-distance matrix with the pointwise distances
            else:
                for j in range(len(dist)):
                    if j not in pttm:
                        pass
                    elif pttm[i] not in tract_distances:
                        tract_distances[pttm[i]] = {pttm[j]: dist[j]}
                    elif pttm[j] not in tract_distances[pttm[i]]:
                        tract_distances[pttm[i]][pttm[j]] = dist[j]
                    else:
                        tract_distances[pttm[i]][pttm[j]] += dist[j]
                    # print(tract_distances)
            i+=1
            line = fh.readline()

    # Save tract matrix to file
    # TODO set filename
    with open(f'{SAVE_FILE_TO}', 'w') as f:
        f.write(json.dumps(tract_distances))
