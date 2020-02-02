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

    For each tract in assignment, check which district it comes from.
    Then add both itself and everyone else in the district to the total human compactness sum.
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

        # Add to the total duration sum
        for other_tract_id in tracts_in_districts[district_id]:
            if district_id not in total_durations:
                total_durations[district_id] = duration_between(tract_id, other_tract_id)
            else:
                total_durations[district_id] += duration_between(tract_id, other_tract_id)
    return total_durations

'''
# Let pairwise be a NxN array where pairwise[i][j] (including pairwise[i][i])
# is the sum of distances from all points in the tract i to the tract j

pairwise = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16],
        ]

# Let assignment be an assignment of census tract IDs to districts
assignment = {
        0: 3,
        1: 3,
        2: 0,
        3: 2,
    }

num_districts = 14

tracts_in_districts = [[] for x in range(num_districts)]
dd_sum = [0 for x in range(num_districts)]

# Loop through once to fill up the array
for tract_id in assignment:
    tracts_in_districts[assignment[tract_id]].append(tract_id)

print(tracts_in_districts)

for idx, district in enumerate(tracts_in_districts):
    # Calculates the sum of driving durations from each tract to all others in the district.
    # Starts with sum of distances from the last element to every other element in the district
    # Then pops off the last element
    while district != []:
        last_elem = district[-1]

        # TODO ask mark about converting this loop into C

        for tract in district:
            # distances may not be symmetric
            dd_sum[idx] += (pairwise[tract][last_elem] +
                    pairwise[last_elem][tract])

        # we've double-counted the last element with itself;
        dd_sum[idx] -= pairwise[last_elem][last_elem]
        
        # pop the last element; we're done with it
        district.pop()


print(tracts_in_districts)
print(dd_sum)
'''
