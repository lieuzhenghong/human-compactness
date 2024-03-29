import csv
import json
from typing import DefaultDict
from collections import defaultdict
from custom_types import *
import config


def create_geoid_to_id_mapping(state_code) -> GeoIDToIDMapping:
    """
    Creates and returns a GeoIDtoID mapping
    Dict[GeoID, TractID]
    """
    geoid_to_id_mapping: GeoIDToIDMapping = {}
    starting_plan = f"./Data_2000/Dual_Graphs/Tract2000_{state_code}.json"
    with open(starting_plan) as f:
        data = json.load(f)
        for node in data["nodes"]:
            geoid_to_id_mapping[node["GEOID"]] = node["id"]
        return geoid_to_id_mapping


def get_all_tract_geoids(state_code) -> Tuple[TractDict, GeoIDToIDMapping]:
    """
    return a mapping of ID to {GEOID, pop, pfs}, as well as a reverse mapping of GEOID to ID
    """
    # first read the starting plan json to get all the IDs

    tract_dict: TractDict = {}
    geoid_to_id_mapping: GeoIDToIDMapping = {}

    # starting_plan = f'/home/lieu/dev/human_compactness/Data_2000/Dual_Graphs/Tract2000_{state_code}.json'
    starting_plan = f"./Data_2000/Dual_Graphs/Tract2000_{state_code}.json"

    with open(starting_plan) as f:
        data = json.load(f)

        for node in data["nodes"]:
            # Mapping for 2000 Census Tracts
            tract_dict[node["id"]] = TractEntry(
                geoid=node["GEOID"], pop=None, pfs=[], vrps=[]
            )

            geoid_to_id_mapping[node["GEOID"]] = node["id"]

    return (tract_dict, geoid_to_id_mapping)


def create_empty_tract_dict(geoid_to_id_mapping: GeoIDToIDMapping) -> TractDict:
    """
    Function that creates a TractDict without population, principal factors, or
    representative voter point data.
    Fill it in with the fill_tract_dict_with_spatial_diversity_info function
    """
    tract_dict: TractDict = {}
    for geoid, tract_id in geoid_to_id_mapping.items():
        tract_dict[tract_id] = TractEntry(geoid=geoid, pop=None, pfs=[], vrps=[])
    return tract_dict


def fill_tract_dict_with_spatial_diversity_info(
    tract_dict: TractDict,
    geoid_to_id_mapping: GeoIDToIDMapping,
    tract_spatial_diversity_scores: str,
) -> TractDict:
    """
    Fills in values of spatial diversity according to the tract_spatial_diversity CSV
    return a mapping of ID to {GEOID, [pf1, ... pf8], pop}
    """

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

    with open(tract_spatial_diversity_scores) as f:
        rdr = csv.DictReader(f)
        for row in rdr:
            # print(row['geo'], row['pf1'])

            if row["geo"] in geoid_to_id_mapping:
                tract_id = geoid_to_id_mapping[row["geo"]]
                if tract_id in tract_dict:

                    # Get the population
                    tract_dict[tract_id]["pop"] = tryParseInt(row["pop"])

                    # Get the PF values (used to calculate spatial diversity)
                    pfs = (
                        row["pf1"],
                        row["pf2"],
                        row["pf3"],
                        row["pf4"],
                        row["pf5"],
                        row["pf6"],
                        row["pf4"],
                        row["pf8"],
                    )
                    pfs = [tryParse(pf) for pf in pfs]

                    tract_dict[tract_id]["pfs"] = pfs

                    # print (tract_dict[tract_id])
                else:
                    raise TractNotFoundError

    return tract_dict


def calc_spatial_diversity(partition):
    """
    Given a Graph and an assignment of tracts to districts, calculate the spatial
    diversity for all districts


    Takes in a Partition which has a graph and a partition

    Returns the district's spatial diversity score, a weighted average of the
    individual standard deviations
    """
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
        # print(node_id, district_id)
        pop = partition.graph.nodes[node_id]["pop"]
        pfs = partition.graph.nodes[node_id]["pfs"]

        # print(pop, pfs)

        if pop is None or pfs is None:
            pass
        else:
            if district_id not in spatial_diversity_pops:
                spatial_diversity_pops[district_id] = 0
            spatial_diversity_pops[district_id] += pop
            if district_id not in spatial_diversity_sums:
                spatial_diversity_sums[district_id] = [0, 0, 0, 0, 0, 0, 0, 0]
            # Add element-wise, multiplied by population
            # this is p.q
            for idx, pf in enumerate(spatial_diversity_sums[district_id]):
                spatial_diversity_sums[district_id][idx] += pfs[idx] * pop
        # print(spatial_diversity_sums)

    # loop through again to get the variances
    # this time we're doing pf_i - mean_pfs

    for node_id in partition.graph.nodes:
        district_id = partition.assignment[node_id]
        # print(node_id, district_id)
        pop = partition.graph.nodes[node_id]["pop"]
        pfs = partition.graph.nodes[node_id]["pfs"]
        sum_pops = spatial_diversity_pops[district_id]

        # OK so now we've summed the populations and the quantities.
        # The mean is simply total quantity / sum(pop)
        # that is, pf_bar = (q.p)/sum(p)

        mean_pfs = [x / sum_pops for x in spatial_diversity_sums[district_id]]
        # print(mean_pfs)

        if pop is None or pfs is None:
            pass
        else:

            if district_id not in spatial_diversity_variances:
                spatial_diversity_variances[district_id] = [0, 0, 0, 0, 0, 0, 0, 0]
            for idx, pf in enumerate(pfs):
                # don't ask me why * pop
                spatial_diversity_variances[district_id][idx] += (
                    pf - mean_pfs[idx]
                ) ** 2 * pop

    # Spatial diversity scores are simply the sqrt of the variances divided by the sum of pops

    for district_id in spatial_diversity_variances:
        sum_pop = spatial_diversity_pops[district_id]
        # print(pop)
        # print(spatial_diversity_variances[district_id])
        spatial_diversity_scores[district_id] = [
            (x / sum_pop) ** 0.5 for x in spatial_diversity_variances[district_id]
        ]

    # We now get each spatial diversity subscore and take the weighted sum to get the final score
    fw = config.SPATIAL_DIVERSITY_FACTOR_WEIGHTS

    spatial_diversity_final_scores = {}

    for district_id in spatial_diversity_scores:
        # Multiply each factor by the factor weight
        score = sum([x * y for x, y in zip(spatial_diversity_scores[district_id], fw)])
        # After taking the weighted sum, divide it by the total factor weight
        score /= sum(fw)
        spatial_diversity_final_scores[district_id] = score

    plan_overall_score = 0

    for district_id in spatial_diversity_final_scores:
        plan_overall_score += spatial_diversity_final_scores[district_id]

    # Normalise from 0 to 1 by dividing by the number of districts
    plan_overall_score /= len(spatial_diversity_final_scores)

    return (plan_overall_score, spatial_diversity_final_scores)
