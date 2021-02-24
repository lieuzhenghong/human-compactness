import _12_Process_Ensembles
import tract_generation
import human_compactness as hc
import dd_human_compactness as ddhc
import ed_human_compactness as edhc
import human_compactness_utils as hc_utils
from geopandas import GeoDataFrame
from gerrychain import GeographicPartition, Graph
from gerrychain.updaters import Tally, cut_edges
import spatial_diversity_utils as spatial_diversity
import json
import test_process_ensembles
import numpy as np
from functools import partial
import config


def init_stuff(initial_partition, dd_hc):
    state_fips = "09"
    state_name = _12_Process_Ensembles.state_names[state_fips].lower()
    num_districts = _12_Process_Ensembles.num_districts[state_fips]
    sample_richness = _12_Process_Ensembles.sample_richness
    tract_list = list(initial_partition.graph.nodes)

    # duration_dict = dd_hc._generate_duration_dict_()

    DD_PATH = f"./20_intermediate_files/{state_fips}_{state_name}_tract_dds.json"
    duration_dict = hc_utils.read_tract_duration_json(DD_PATH)

    tractwise_matrix = dd_hc.generate_tractwise_matrix(tract_list, duration_dict)
    lookup_table = dd_hc._form_tract_matrix_dd_lookup_table_()
    DM_PATH = f"./20_intermediate_files/{state_fips}_{state_name}_knn_sum_dd.dmx"
    duration_matrix = _12_Process_Ensembles.read_duration_matrix(DM_PATH)

    tract_dict, geoid_to_id_mapping = spatial_diversity.get_all_tract_geoids(state_fips)

    num_districts = _12_Process_Ensembles.num_districts[state_fips]

    tract_dict = tract_generation.generate_tracts_with_vrps(
        state_fips, state_name, num_districts, sample_richness
    )

    return tract_dict, duration_dict, tractwise_matrix, duration_matrix


def _dicts_are_approx_equal_(d1, d2) -> bool:
    a1 = np.array(list(d1.items()), dtype=float)
    a2 = np.array(list(d2.items()), dtype=float)
    print(a1)
    print(a2)
    return np.allclose(a1, a2)


"""
def test_explore():
    state_fips = "09"
    test_json = f"./test/test_data/data100.json"
    datadir = f"./Tract_Ensembles/2000/{state_fips}/"
    state_fips = "09"
    state_name = _12_Process_Ensembles.state_names[state_fips].lower()
    num_districts = _12_Process_Ensembles.num_districts[state_fips]
    sample_richness = _12_Process_Ensembles.sample_richness

    with open(test_json, "r") as f1:
        (
            graph,
            human_compactness_function,
            reock_compactness_function,
        ) = _12_Process_Ensembles._init_(state_fips, datadir)

        initial_partition = GeographicPartition(graph, assignment="New_Seed")
        points_downsampled = tract_generation._read_and_process_vrp_shapefile(
            state_fips, state_name, num_districts, sample_richness
        )

        edhc = hc.EDHumanCompactness(initial_partition, points_downsampled)
        # edhc._duration_between_([1, 2, 3], [1, 5, 6])
        tract_dict, geoid_to_id_mapping = spatial_diversity.get_all_tract_geoids(
            state_fips
        )
        M = edhc.generate_tractwise_matrix(
            tract_dict,
        )
"""


def test_euclidean_compactness():
    state_fips = "09"
    datadir = f"./Tract_Ensembles/2000/{state_fips}/"
    graph = Graph.from_json(datadir + "starting_plan.json")
    (
        duration_dict,
        tract_dict,
        tractwise_matrix,
        pointwise_sum_matrix,
        state_shapefile,
    ) = _12_Process_Ensembles._init_data_(state_fips, graph)

    _12_Process_Ensembles._update_graph_with_tract_dict_info_(
        graph,
        tract_dict,
    )

    tract_dict, geoid_to_id_mapping = spatial_diversity.get_all_tract_geoids(state_fips)

    state_name = config.STATE_NAMES[state_fips].lower()
    num_districts = config.NUM_DISTRICTS[state_fips]
    sample_richness = _12_Process_Ensembles.sample_richness

    test_json = f"./test/test_data/data100.json"
    with open(test_json, "r") as f1:
        initial_partition = GeographicPartition(
            graph,
            assignment="New_Seed",
        )
        new_assignment = dict(initial_partition.assignment)

        points_downsampled = tract_generation._read_and_process_vrp_shapefile(
            state_fips, state_name, num_districts, sample_richness
        )

        dd_hc = ddhc.DDHumanCompactness(
            initial_partition,
            points_downsampled,
        )

        new_assignment = dict(initial_partition.assignment)

        human_compactness_function = partial(
            dd_hc.calculate_human_compactness,
            tract_dict,
            pointwise_sum_matrix,
            tractwise_matrix,
        )

        assert True


def test_human_compactness():
    """
    Test equivalence of old human compactness function and new human compactness function
    """
    # assert False
    state_fips = "09"
    test_json = f"./test/test_data/data100.json"
    datadir = f"./Tract_Ensembles/2000/{state_fips}/"
    state_fips = "09"
    state_name = config.STATE_NAMES[state_fips].lower()
    num_districts = config.NUM_DISTRICTS[state_fips]
    sample_richness = _12_Process_Ensembles.sample_richness
    graph = Graph.from_json(datadir + "starting_plan.json")
    (
        duration_dict,
        tract_dict,
        tractwise_matrix,
        pointwise_sum_matrix,
        state_shapefile,
    ) = _12_Process_Ensembles._init_data_(state_fips, graph)

    _12_Process_Ensembles._update_graph_with_tract_dict_info_(
        graph,
        tract_dict,
    )

    tract_dict, geoid_to_id_mapping = spatial_diversity.get_all_tract_geoids(state_fips)

    with open(test_json, "r") as f1:

        initial_partition = GeographicPartition(
            graph,
            assignment="New_Seed",
        )

        points_downsampled = tract_generation._read_and_process_vrp_shapefile(
            state_fips, state_name, num_districts, sample_richness
        )

        dd_hc = ddhc.DDHumanCompactness(
            initial_partition,
            points_downsampled,
        )

        (
            human_compactness_function,
            reock_compactness_function,
        ) = _12_Process_Ensembles._init_metrics_(
            duration_dict,
            tract_dict,
            tractwise_matrix,
            pointwise_sum_matrix,
            state_shapefile,
        )

        new_assignment = dict(initial_partition.assignment)

        human_compactness_function = partial(
            dd_hc.calculate_human_compactness,
            tract_dict,
            pointwise_sum_matrix,
            tractwise_matrix,
        )

        human_compactness_function_2 = partial(
            hc_utils.calculate_human_compactness,
            duration_dict,
            tract_dict,
            pointwise_sum_matrix,
            tractwise_matrix,
        )

        with open(datadir + f"flips_10000.json") as f:
            dict_list = json.load(f)
            calcdata = {}
            refdata = {}
            for step in range(10):
                calcdata[step] = _12_Process_Ensembles.calculate_metrics_step(
                    step,
                    dict_list,
                    graph,
                    new_assignment,
                    human_compactness_function,
                    reock_compactness_function,
                )

                refdata[step] = _12_Process_Ensembles.calculate_metrics_step(
                    step,
                    dict_list,
                    graph,
                    new_assignment,
                    human_compactness_function_2,
                    reock_compactness_function,
                )

                assert _dicts_are_approx_equal_(
                    calcdata[step]["human_compactness"],
                    refdata[step]["human_compactness"],
                )