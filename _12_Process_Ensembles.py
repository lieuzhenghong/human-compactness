from geopandas.geodataframe import GeoDataFrame
from pandas import DataFrame
from custom_types import *
from typing import Tuple, Union
import os
import json
from functools import partial

import geopandas as gpd
import numpy as np

import human_compactness_utils as hc_utils
import spatial_diversity_utils as spatial_diversity
import tract_generation
import reock as reock
from gerrychain import GeographicPartition, Graph
from gerrychain.metrics import polsby_popper
from gerrychain.updaters import Tally, cut_edges
from timeit import default_timer as timer
import config


num_elections = 1

plan_name = "Enacted"

sample_richness = 1000  # Number of VRPs to sample per district


def read_duration_matrix(DM_PATH):
    from pointwise_libs import distance_matrix

    duration_matrix = distance_matrix.read_duration_matrix_from_file(DM_PATH)
    return duration_matrix


def _create_new_dir_(state_fips: str) -> str:
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

    return newdir


def _update_graph_with_tract_dict_info_(graph: Graph, tract_dict: TractDict) -> None:
    """
    Update the partition graph with information from the TractDict
    Used in calc_spatial_diversity
    TODO: think about using the Partition Graph as the source of truth.
    Then we can get rid of TractDict.
    """
    for node in graph.nodes():
        graph.nodes[node]["pfs"] = tract_dict[node]["pfs"]
        graph.nodes[node]["pop"] = tract_dict[node]["pop"]
        graph.nodes[node]["vrps"] = tract_dict[node]["vrps"]
        # print(graph.nodes[node])


def _init_data_(
    state_fips: str, graph: Graph
) -> Tuple[
    DurationDict,
    TractDict,
    Union[DataFrame, GeoDataFrame],
    TractWiseMatrix,
    PointWiseSumMatrix,
]:
    """
    Generates a bunch of stuff needed for the various compactness functions.
    """
    print("Reading pairwise tract driving durations into memory...")
    state_name = config.STATE_NAMES[state_fips].lower()
    DD_PATH = f"./20_intermediate_files/{state_fips}_{state_name}_tract_dds.json"
    duration_dict = hc_utils.read_tract_duration_json(DD_PATH)

    print("Reading KNN duration matrix file into memory...")
    DM_PATH = f"./20_intermediate_files/{state_fips}_{state_name}_knn_sum_dd.dmx"
    pointwise_sum_matrix = read_duration_matrix(DM_PATH)

    # add population and spatial diversity data to the graph
    # tract_dict = spatial_diversity.build_spatial_diversity_dict(
    #    *spatial_diversity.get_all_tract_geoids())

    tract_dict, geoid_to_id_mapping = spatial_diversity.get_all_tract_geoids(state_fips)

    tract_dict = tract_generation.generate_tracts_with_vrps(
        state_fips, state_name, config.NUM_DISTRICTS[state_fips], sample_richness
    )

    print("Reading tract shapefile into memory...")
    SHAPEFILE_PATH = f"./Data_2000/Shapefiles/Tract2000_{state_fips}.shp"
    state_shp = gpd.read_file(SHAPEFILE_PATH)
    # Preprocess the state tract shapefile to include external points
    state_shp = reock.preprocess_dataframe(state_shp, geoid_to_id_mapping)

    # Create a square numpy NxN matrix from the pairwise tract duration dict
    tractwise_matrix = hc_utils._generate_tractwise_dd_matrix_(
        list(graph.nodes), duration_dict
    )

    return (
        duration_dict,
        tract_dict,
        tractwise_matrix,
        pointwise_sum_matrix,
        state_shp,
    )


def _init_metrics_(
    initial_partition: GeographicPartition,
    points_downsampled: GeoDataFrame,
    duration_dict: DurationDict,
    tract_dict: TractDict,
    tractwise_matrix: TractWiseMatrix,
    pointwise_sum_matrix: PointWiseSumMatrix,
    state_shapefile: Union[DataFrame, GeoDataFrame],
):
    human_compactness_function = partial(
        hc_utils.calculate_human_compactness,
        duration_dict,
        tract_dict,
        pointwise_sum_matrix,
        tractwise_matrix,
    )

    import dd_human_compactness as ddhc
    import ed_human_compactness as edhc

    dd_hc = ddhc.DDHumanCompactness(initial_partition, points_downsampled)
    ed_hc = edhc.EDHumanCompactness(initial_partition, points_downsampled)

    human_compactness_function = partial(
        dd_hc.calculate_human_compactness,
        tract_dict,
        pointwise_sum_matrix,
        tractwise_matrix,
    )

    reock_compactness_function = partial(reock.reock, state_shapefile)

    return (
        human_compactness_function,
        reock_compactness_function,
    )


def calculate_metrics_step(
    step,
    dict_list,
    graph,
    new_assignment,
    human_compactness_function,
    reock_compactness_function,
):
    print(f"Step: {step}")
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
            "human_compactness": human_compactness_function,
            "polsby_compactness": polsby_popper,
            "reock_compactness": reock_compactness_function,
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
    human_compactness_function,
    reock_compactness_function,
):
    data = []

    max_steps = 10000
    step_size = 10000
    save_step_size = 100

    ts = [x * step_size for x in range(1, int(max_steps / step_size) + 1)]

    for t in ts:
        print(f"Opening flips_{t}.json")
        with open(datadir + f"flips_{t}.json") as f:
            dict_list = json.load(f)

        for step in range(step_size):
            step_data = calculate_metrics_step(
                step,
                dict_list,
                graph,
                new_assignment,
                human_compactness_function,
                reock_compactness_function,
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
    for state_fips in config.FIPS_LIST:
        newdir = _create_new_dir_(state_fips)
        datadir = f"./Tract_Ensembles/2000/{state_fips}/"
        graph = Graph.from_json(datadir + "starting_plan.json")

        (
            duration_dict,
            tract_dict,
            tractwise_matrix,
            pointwise_sum_matrix,
            state_shapefile,
        ) = _init_data_(state_fips, graph)

        _update_graph_with_tract_dict_info_(
            graph,
            tract_dict,
        )

        initial_partition = GeographicPartition(
            graph,
            assignment="New_Seed",
        )

        points_downsampled = tract_generation._read_and_process_vrp_shapefile(
            state_fips,
            config.STATE_NAMES[state_fips],
            config.NUM_DISTRICTS[state_fips],
            sample_richness,
        )

        (human_compactness_function, reock_compactness_function,) = _init_metrics_(
            initial_partition,
            points_downsampled,
            duration_dict,
            tract_dict,
            tractwise_matrix,
            pointwise_sum_matrix,
            state_shapefile,
        )

        new_assignment = dict(initial_partition.assignment)
        # load graph and make initial partition
        calculate_metrics(
            new_assignment,
            datadir,
            newdir,
            graph,
            human_compactness_function,
            reock_compactness_function,
        )


if __name__ == "__main__":
    main_old()
