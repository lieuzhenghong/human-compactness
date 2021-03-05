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
import dd_human_compactness as ddhc
import ed_human_compactness as edhc
import human_compactness as hc


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
    # newdir = f"./22_intermediate_files_rerun_old/{state_fips}/"
    # newdir = f"./22_intermediate_files_rerun_new/{state_fips}/"
    # newdir = f"./22_intermediate_files_rerun_new_proj_network_off/{state_fips}/"
    newdir = f"./22_intermediate_files_new_run/{state_fips}/"

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


def calculate_metrics_step(partition: GeographicPartition) -> Dict[str, Dict]:
    result = {}
    print(partition.updaters.keys())
    for updater in partition.updaters.keys():
        if updater == "reock_compactness":
            reock_compactness, ch_compactness = partition["reock_compactness"]
            result["reock_compactness"] = reock_compactness
            result["convex_hull_compactness"] = ch_compactness
        if updater in [
            "human_compactness_dd",
            "human_compactness_ed",
            "spatial_diversity",
            "polsby_compactness",
        ]:
            result[updater] = partition[updater]

    print(result)
    return result


def main():
    for state_fips in config.FIPS_LIST:
        newdir = _create_new_dir_(state_fips)
        datadir = f"./Tract_Ensembles/2000/{state_fips}/"
        graph = Graph.from_json(datadir + "starting_plan.json")
        points_downsampled = tract_generation._read_and_process_vrp_shapefile(
            state_fips,
            config.STATE_NAMES[state_fips],
            config.NUM_DISTRICTS[state_fips],
            config.SAMPLE_RICHNESS,
        )
        tract_dict, geoid_to_id_mapping = spatial_diversity.get_all_tract_geoids(
            state_fips
        )

        SHAPEFILE_PATH = f"./Data_2000/Shapefiles/Tract2000_{state_fips}.shp"
        state_shapefile = gpd.read_file(SHAPEFILE_PATH)
        # Preprocess the state tract shapefile to include external points
        state_shapefile = reock.preprocess_dataframe(
            state_shapefile, geoid_to_id_mapping
        )
        reock_compactness_function = partial(reock.reock, state_shapefile)

        tract_dict = tract_generation.generate_tracts_with_vrps(
            state_fips,
            config.STATE_NAMES[state_fips].lower(),
            config.NUM_DISTRICTS[state_fips],
            config.SAMPLE_RICHNESS,
        )

        # We need to do this otherwise calc_spatial_diversity will break
        _update_graph_with_tract_dict_info_(
            graph,
            tract_dict,
        )

        dd_hc = ddhc.DDHumanCompactness(
            graph,
            points_downsampled,
            tract_dict,
        )
        DM_PATH = f"./20_intermediate_files/{state_fips}_{config.STATE_NAMES[state_fips].lower()}_knn_sum_dd.dmx"
        dd_hc.pointwise_sum_matrix = read_duration_matrix(DM_PATH)
        DD_PATH = f"./20_intermediate_files/{state_fips}_{config.STATE_NAMES[state_fips].lower()}_tract_dds.json"
        duration_dict = hc_utils.read_tract_duration_json(DD_PATH)
        dd_hc.tractwise_matrix = dd_hc.generate_tractwise_matrix(
            list(graph.nodes), duration_dict
        )

        ed_hc = edhc.EDHumanCompactness(
            graph,
            points_downsampled,
            tract_dict,
        )

        ED_POINTWISE_SUM_MATRIX_PATH = f"./20_intermediate_files/{state_fips}_{config.STATE_NAMES[state_fips]}_pointwise_sum_matrix.npy"
        ED_TRACTWISE_MATRIX_PATH = f"./20_intermediate_files/{state_fips}_{config.STATE_NAMES[state_fips]}_tractwise_matrix.npy"
        ed_hc.pointwise_sum_matrix = ed_hc.read_ed_pointwise_sum_matrix(
            ED_POINTWISE_SUM_MATRIX_PATH
        )
        ed_hc.tractwise_matrix = ed_hc.read_ed_tractwise_matrix(
            ED_TRACTWISE_MATRIX_PATH
        )

        human_compactness_function_dd = dd_hc.calculate_human_compactness
        human_compactness_function_ed = ed_hc.calculate_human_compactness

        new_partition = GeographicPartition(
            graph,
            assignment="New_Seed",
            updaters={
                "cut_edges": cut_edges,
                "population": Tally("population", alias="population"),
                "spatial_diversity": spatial_diversity.calc_spatial_diversity,
                "human_compactness_dd": human_compactness_function_dd,
                "human_compactness_ed": human_compactness_function_ed,
                "polsby_compactness": polsby_popper,
                "reock_compactness": reock_compactness_function,
            },
        )

        data = []

        max_steps = 10000
        step_size = 10000
        save_step_size = 100

        ts = [x * step_size for x in range(1, int(max_steps / step_size) + 1)]
        for t in ts:
            print(f"Opening flips_{t}.json")
            with open(datadir + f"flips_{t}.json") as f:
                dict_list = json.load(f)

                data = []
                calcdata = {}
                for step in range(step_size):
                    changes_this_step = dict_list[step].items()
                    new_partition: GeographicPartition = new_partition.flip(
                        {int(item[0]): int(item[1]) for item in changes_this_step}
                    )

                    start = timer()
                    calcdata[step] = calculate_metrics_step(new_partition)
                    end = timer()
                    print(f"Time taken for step {step}: {end-start}")
                    print(f"Step: {calcdata[step]}")

                    data.append(calcdata[step])
                    if step % save_step_size == save_step_size - 1:  # 999
                        print(
                            f'Saving results as {newdir + "data" + str(t-step_size + step + 1)}.json'
                        )
                        with open(
                            f"{newdir}data{(t - step_size + step + +1)}.json",
                            "w",
                        ) as tf1:
                            json.dump(data, tf1)
                            data = []


if __name__ == "__main__":
    main()