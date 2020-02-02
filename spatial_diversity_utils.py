from typing import List
import csv
import json

# TODO make this a command-line param

TRACT_SPATIAL_DIVERSITY_SCORES = '/home/lieu/dev/human_compactness/tract_spatial_diversity.csv'
#STARTING_PLAN_FILE = '/home/lieu/dev/human_compactness/Tract_Ensembles/13/starting_plan.json'
STARTING_PLAN_FILE = '/home/lieu/dev/human_compactness/Data_2000/Dual_Graphs/Tract2000_13.json'


SPATIAL_DIVERSITY_FACTOR_WEIGHTS = (0.1464, 0.1182, 0.101, 0.0775, 0.0501, 0.0399, 0.0389, 0.0366)


# TODO allow specifiying which state
def get_all_tract_geoids():
    '''
    return a mapping of ID to {GEOID, pop, pfs}, as well as a reverse mapping of GEOID to ID
    '''
    # first read the starting plan json to get all the IDs

    tract_dict = {}
    geoid_to_id_mapping = {}

    with open(STARTING_PLAN_FILE) as f:
        data = json.load(f)
        
        for node in data["nodes"]:
            #tract_dict[node["id"]] = {'geoid': node["GEOID10"], 'pop': None, 'pfs': None}
            #geoid_to_id_mapping[node["GEOID10"]] = node["id"]

            # Mapping for 2000 Census Tracts
            tract_dict[node["id"]] = {'geoid': node["GEOID"], 'pop': None, 'pfs': None}
            geoid_to_id_mapping[node["GEOID"]] = node["id"]


    #print(tract_dict)
    return (tract_dict, geoid_to_id_mapping)

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
                    #print(tract_distances)
            i+=1
            line = fh.readline()

    # Save tract matrix to file
    # TODO set filename
    with open(f'{SAVE_FILE_TO}', 'w') as f:
        f.write(json.dumps(tract_distances))

'''
return a mapping of ID to {GEOID, [pf1, ... pf8], pop}
'''

def build_spatial_diversity_dict(tract_dict, geoid_to_id_mapping):

    def tryParse(value):
        try:
            return float(value)
        except ValueError:
            return None

    def tryParseInt(value):
        try:
            return int(value)
        except ValueError:
            return None

    with open(TRACT_SPATIAL_DIVERSITY_SCORES) as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            #print(row['geo'], row['pf1'])

            if row['geo'] in geoid_to_id_mapping:
                tract_id = geoid_to_id_mapping[row['geo']]
                if tract_id in tract_dict:

                    # Get the population
                    tract_dict[tract_id]['pop'] = tryParseInt(row['pop'])
                    
                    # Get the PF values (used to calculate spatial diversity)
                    pfs = (row['pf1'], row['pf2'],
                           row['pf3'], row['pf4'], row['pf5'],
                           row['pf6'], row['pf4'], row['pf8'])
                    pfs = [tryParse(pf) for pf in pfs]


                    tract_dict[tract_id]['pfs'] = pfs

                    #print (tract_dict[tract_id])
                else:
                    raise TractNotFoundError
            
    return tract_dict

'''
Given a Graph and an assignment of tracts to districts, calculate the spatial
diversity for all districts


Takes in a Partition which has a graph and a partition

Returns the district's spatial diversity score, a weighted average of the
individual standard deviations
'''

def calc_spatial_diversity(partition):
    print("calculating spatial diversity")
    spatial_diversity_scores = {}
    spatial_diversity_variances = {}
    spatial_diversity_sums = {}
    spatial_diversity_pops = {}

    # On the first pass, we sum the population, as well as the
    # pfs weighted by population
    # SQRT( (q -  (p.q)/sum(p))^2 . P ) / sum(p) )

    # so we obtain p.q in sums and sum(p) in pops

    for node_id in partition.graph.nodes:
        district_id = partition.assignment[node_id]
        #print(node_id, district_id)
        pop = partition.graph.nodes[node_id]['pop']
        pfs = partition.graph.nodes[node_id]['pfs']

        #print(pop, pfs)

        if pop is None or pfs is None:
            pass
        else:
            if district_id not in spatial_diversity_pops:
                spatial_diversity_pops[district_id] = 0
            spatial_diversity_pops[district_id] += pop
            if district_id not in spatial_diversity_sums:
                spatial_diversity_sums[district_id] = [0,0,0,0,0,0,0,0]
            # Add element-wise, multiplied by population
            # this is p.q
            for idx, pf in enumerate(spatial_diversity_sums[district_id]):
                spatial_diversity_sums[district_id][idx] += pfs[idx] * pop
        #print(spatial_diversity_sums)

    # loop through again to get the variances
    # this time we're doing pf_i - mean_pfs

    for node_id in partition.graph.nodes:
        district_id = partition.assignment[node_id]
        #print(node_id, district_id)
        pop = partition.graph.nodes[node_id]['pop']
        pfs = partition.graph.nodes[node_id]['pfs']
        sum_pops = spatial_diversity_pops[district_id]

        # OK so now we've summed the populations and the quantities.
        # The mean is simply total quantity / sum(pop)
        # that is, pf_bar = (q.p)/sum(p)

        mean_pfs = [x/sum_pops for x in spatial_diversity_sums[district_id]]
        #print(mean_pfs)

        if pop is None or pfs is None:
            pass
        else:

            if district_id not in spatial_diversity_variances:
                spatial_diversity_variances[district_id] = [0,0,0,0,0,0,0,0]
            for idx, pf in enumerate(pfs):
                # don't ask me why * pop
                spatial_diversity_variances[district_id][idx] += (pf - mean_pfs[idx])**2 * pop

    # Spatial diversity scores are simply the sqrt of the variances divided by the sum of pops

    for district_id in spatial_diversity_variances:
        sum_pop = spatial_diversity_pops[district_id]
        #print(pop)
        #print(spatial_diversity_variances[district_id])
        spatial_diversity_scores[district_id] = [(x/sum_pop) ** 0.5 for x in spatial_diversity_variances[district_id]]

    # We now get each spatial diversity subscore and take the weighted sum to get the final score
    fw = (SPATIAL_DIVERSITY_FACTOR_WEIGHTS)

    spatial_diversity_final_scores = {}

    for district_id in spatial_diversity_scores:
        # Multiply each factor by the factor weight
        score = sum([x*y for x, y in
            zip(spatial_diversity_scores[district_id], fw)])
        # After taking the weighted sum, divide it by the total factor weight
        score /= sum(fw)
        spatial_diversity_final_scores[district_id] = score

    plan_overall_score = 0

    for district_id in spatial_diversity_final_scores:
        plan_overall_score += spatial_diversity_final_scores[district_id]

    # Normalise from 0 to 1 by dividing by the number of districts
    plan_overall_score /= len(spatial_diversity_final_scores)

    return (plan_overall_score, spatial_diversity_final_scores)



build_spatial_diversity_dict(*get_all_tract_geoids())


