import os
import sys
import json
from functools import partial

import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from maup import assign

import human_compactness_utils as hc_utils
import spatial_diversity_utils as spatial_diversity
import tract_generation
import reock as reock
from gerrychain import Election, GeographicPartition, Graph, Partition
from gerrychain.metrics import polsby_popper
from gerrychain.updaters import Tally, cut_edges
from timeit import default_timer as timer

matplotlib.use("Agg")


state_names = {
    "02": "Alaska",
    "01": "Alabama",
    "05": "Arkansas",
    "04": "Arizona",
    "06": "California",
    "08": "Colorado",
    "09": "Connecticut",
    "10": "Delaware",
    "12": "Florida",
    "13": "Georgia",
    "66": "Guam",
    "15": "Hawaii",
    "19": "Iowa",
    "16": "Idaho",
    "17": "Illinois",
    "18": "Indiana",
    "20": "Kansas",
    "21": "Kentucky",
    "22": "Louisiana",
    "25": "Massachusetts",
    "24": "Maryland",
    "23": "Maine",
    "26": "Michigan",
    "27": "Minnesota",
    "29": "Missouri",
    "28": "Mississippi",
    "30": "Montana",
    "37": "North_Carolina",
    "38": "North_Dakota",
    "31": "Nebraska",
    "33": "New_Hampshire",
    "34": "New_Jersey",
    "35": "New_Mexico",
    "32": "Nevada",
    "36": "New_York",
    "39": "Ohio",
    "40": "Oklahoma",
    "41": "Oregon",
    "42": "Pennsylvania",
    "72": "Puerto_Rico",
    "44": "Rhode_Island",
    "45": "South_Carolina",
    "46": "South_Dakota",
    "47": "Tenessee",
    "48": "Texas",
    "49": "Utah",
    "51": "Virginia",
    "50": "Vermont",
    "53": "Washington",
    "55": "Wisconsin",
    "54": "West_Virginia",
    "56": "Wyoming",
}

# TODO fill this in
num_districts = {
    "01": 7,
    "04": 8,
    "08": 7,
    "09": 5,
    "13": 13,
    "16": 2,
    "19": 4,
    "22": 7,
    "24": 8,
    "33": 2,
    "23": 2,
    "44": 2,
    "49": 3,
    "55": 8,
}

num_elections = 1

plan_name = "Enacted"

# I'll be doing the following districts:

# fips_list = ['13'] # Georgia
# fips_list = ['22']  # Louisiana
# fips_list = ['24'] # Maryland
# fips_list = ['55']  # Wisconsin
# fips_list = ['04', '08', '16', '19', '33', '49']
# fips_list = ['13', '22', '24', '55']
# fips_list = ['16']
# fips_list = ['19', '33', '49']
# fips_list = ['23', '44'] # Maine and Rhode Island
fips_list = ["09"]
sample_richness = 1000  # Number of VRPs to sample per district


def read_duration_matrix(DM_PATH):
    from pointwise_libs import distance_matrix

    duration_matrix = distance_matrix.read_duration_matrix_from_file(DM_PATH)
    return duration_matrix


def _create_new_dir_(state_fips: str) -> None:
    """
    Creates a new directory to put the result files
    """
    # newdir = f"./20_intermediate_files/{state_fips}/"
    # newdir = f"./21_intermediate_files_rerun/{state_fips}/"
    # newdir = f"./22_intermediate_files_rerun_2/{state_fips}/"
    newdir = f"./22_intermediate_files_rerun_old/{state_fips}/"
    # newdir = f"./22_intermediate_files_rerun_new/{state_fips}/"
    # newdir = f"./22_intermediate_files_rerun_new_proj_network_off/{state_fips}/"

    os.makedirs(os.path.dirname(newdir + "init"), exist_ok=True)
    with open(newdir + "init", "w") as f:
        f.write("Created Folder")


def main_old():
    """
    1. Read tract shapefile into memoru
    2. Read KNN duration matrix file into memory
    3. Create new folder if it doesn't exist
    4. Open up _starting_plan.json
    5. Create Graph from _starting_plan.json
    6. tract_dict, geoid_to_id_mapping = spatial_diversity.get_all_tract_geoids(
            state_fips)
    7. tract_dict = tract_generation.generate_tracts_with_vrps(
            state_fips, state_name, num_districts[state_fips], sample_richness)
    8. # Preprocess the state tract shapefile to include external points
        state_shp = reock.preprocess_dataframe(
            state_shp, geoid_to_id_mapping)
    9. initial_partition
    10. new_assignment
    11. Run 10,000 cycles, calculate all metrics
    """
    for state_fips in fips_list:
        _create_new_dir_(state_fips)

        state_name = state_names[state_fips].lower()
        DD_PATH = f"./20_intermediate_files/{state_fips}_{state_name}_tract_dds.json"
        DM_PATH = f"./20_intermediate_files/{state_fips}_{state_name}_knn_sum_dd.dmx"
        DURATION_DICT = hc_utils.read_tract_duration_json(DD_PATH)
        SHAPEFILE_PATH = f"./Data_2000/Shapefiles/Tract2000_{state_fips}.shp"

        print("Reading tract shapefile into memory...")
        state_shp = gpd.read_file(SHAPEFILE_PATH)

        print("Reading KNN duration matrix file into memory...")
        duration_matrix = read_duration_matrix(DM_PATH)

        datadir = f"./Tract_Ensembles/2000/{state_fips}/"

        graph = Graph.from_json(datadir + "starting_plan.json")

        # add population and spatial diversity data to the graph
        # tract_dict = spatial_diversity.build_spatial_diversity_dict(
        #    *spatial_diversity.get_all_tract_geoids())

        tract_dict, geoid_to_id_mapping = spatial_diversity.get_all_tract_geoids(
            state_fips
        )

        tract_dict = tract_generation.generate_tracts_with_vrps(
            state_fips, state_name, num_districts[state_fips], sample_richness
        )

        # Preprocess the state tract shapefile to include external points
        state_shp = reock.preprocess_dataframe(state_shp, geoid_to_id_mapping)

        # just for reference
        num_Nones = 0
        for node in graph.nodes():

            if tract_dict[node]["pfs"] is None:
                num_Nones += 1

            graph.nodes[node]["pfs"] = tract_dict[node]["pfs"]
            graph.nodes[node]["pop"] = tract_dict[node]["pop"]
            # print(graph.nodes[node])

        # Checking the number of empty tracts (tracts without VRPs)
        empty_tracts = []

        for tract_id in tract_dict:
            if len(tract_dict[tract_id]["vrps"]) == 0:
                empty_tracts.append(tract_id)

        print(f"Number of empty tracts: {len(empty_tracts)}")

        initial_partition = GeographicPartition(
            graph,
            assignment="New_Seed",
            updaters={
                "cut_edges": cut_edges,
                "population": Tally("population", alias="population"),
                "spatial_diversity": spatial_diversity.calc_spatial_diversity,
                "human_compactness": partial(
                    hc_utils.calculate_human_compactness,
                    DURATION_DICT,
                    tract_dict,
                    duration_matrix,
                ),
                "polsby_compactness": polsby_popper,
                "reock_compactness": partial(reock.reock, state_shp),
                # "reock_compactness": partial(reock.compare_reock, state_shp, geoid_to_id_mapping),
            },
        )

        new_assignment = dict(initial_partition.assignment)
        # load graph and make initial partition
        calculate_metrics(
            new_assignment,
            datadir,
            newdir,
            graph,
            DURATION_DICT,
            tract_dict,
            duration_matrix,
            state_shp,
        )


def calculate_metrics_step(
    step,
    step_size,
    dict_list,
    graph,
    new_assignment,
    DURATION_DICT,
    tract_dict,
    duration_matrix,
    state_shp,
):
    print(f"Step: {step}. Step Size: {step_size}")

    start = timer()

    changes_this_step = dict_list[step].items()
    print(f"Changes this step: {len(changes_this_step)}")

    print("Updating new assignment...")
    new_assignment.update({int(item[0]): int(item[1]) for item in changes_this_step})

    print("Building new GeographicPartition...")
    new_partition = GeographicPartition(
        graph,
        assignment=new_assignment,
        updaters={
            "cut_edges": cut_edges,
            "population": Tally("population", alias="population"),
            "spatial_diversity": spatial_diversity.calc_spatial_diversity,
            "human_compactness": partial(
                hc_utils.calculate_human_compactness,
                DURATION_DICT,
                tract_dict,
                duration_matrix,
            ),
            "polsby_compactness": polsby_popper,
            "reock_compactness": partial(reock.reock, state_shp),
            # "reock_compactness": partial(reock.compare_reock, state_shp, geoid_to_id_mapping),
        },
    )

    print("Appending new data...")

    start_hc = timer()
    human_compactness = new_partition["human_compactness"]
    end_hc = timer()
    print(f"Time taken to calculate human compactness: {end_hc - start_hc}")

    start_reock = timer()
    reock_compactness, ch_compactness = new_partition["reock_compactness"]
    end_reock = timer()
    print(f"Time taken to calculate reock compactness: {end_reock - start_reock}")

    end = timer()

    print(f"Time taken for step {step}: {end-start}")

    return {
        "spatial_diversity": new_partition["spatial_diversity"],
        "polsby_compactness": new_partition["polsby_compactness"],
        "human_compactness": human_compactness,
        "reock_compactness": reock_compactness,
        "convex_hull_compactness": ch_compactness,
    }


def calculate_metrics(
    new_assignment,
    datadir,
    newdir,
    graph,
    DURATION_DICT,
    tract_dict,
    duration_matrix,
    state_shp,
):
    data = []

    max_steps = 10000
    step_size = 10000
    save_step_size = 100

    ts = [x * step_size for x in range(1, int(max_steps / step_size) + 1)]

    for t in ts:
        print(f"Opening flips_{t}.json")
        with open(datadir + f"flips_{t}.json") as f:
            # dict_list = ast.literal_eval(f.read())
            dict_list = json.load(f)
            # Make new partition by updating dictionary

        for step in range(step_size):
            step_data = calculate_metrics_step(
                step,
                step_size,
                dict_list,
                graph,
                new_assignment,
                DURATION_DICT,
                tract_dict,
                duration_matrix,
                state_shp,
            )
            data.append(step_data)
            if step % save_step_size == save_step_size - 1:  # 999
                print(
                    f'Saving results as {newdir + "data" + str(t-step_size + step + 1)}.json'
                )
                with open(
                    newdir + "data" + str(t - step_size + step + +1) + ".json", "w"
                ) as tf1:
                    json.dump(data, tf1)
                    data = []


if __name__ == "__main__":
    main_old()
