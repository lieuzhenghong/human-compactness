
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

1. add 
2. 
'''

# assume we have something called tract_dd and assignment

NUM_DISTRICTS = 14

total_durations = np.zeros(NUM_DISTRICTS)
tracts_in_districts = {}

for i in range(NUM_DISTRICTS):
    tracts_in_districts[i] = {}

for tract_id in assignments:
    
    total_durations += 


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
