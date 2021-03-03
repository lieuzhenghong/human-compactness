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
import pytest


def _dicts_are_approx_equal_(d1, d2) -> bool:
    a1 = np.array(list(d1.items()), dtype=float)
    a2 = np.array(list(d2.items()), dtype=float)
    print(a1)
    print(a2)
    return np.allclose(a1, a2)


@pytest.fixture
def ed_hc():
    state_fips = "09"
    datadir = f"./Tract_Ensembles/2000/{state_fips}/"
    test_json = f"./test/test_data/data100.json"
    graph = Graph.from_json(datadir + "starting_plan.json")

    initial_partition = GeographicPartition(
        graph,
        assignment="New_Seed",
    )

    state_name = config.STATE_NAMES[state_fips].lower()
    num_districts = config.NUM_DISTRICTS[state_fips]
    sample_richness = _12_Process_Ensembles.sample_richness

    points_downsampled = tract_generation._read_and_process_vrp_shapefile(
        state_fips, state_name, num_districts, sample_richness
    )

    ed_hc = edhc.EDHumanCompactness(
        initial_partition,
        points_downsampled,
    )
    return ed_hc


@pytest.mark.skip()
def test_create_kd_tree(ed_hc):
    kd_tree = ed_hc._create_kd_tree_()
    assert True


def test_sum_of_distances_between_two_lists_of_points_(ed_hc):
    print(ed_hc._sum_of_distances_between_two_lists_of_points_([1, 2, 3], [0, 4, 5]))
    assert True


@pytest.mark.skip()
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

        ed_hc = edhc.EDHumanCompactness(
            initial_partition,
            points_downsampled,
        )

        new_assignment = dict(initial_partition.assignment)

        human_compactness_function = partial(
            ed_hc.calculate_human_compactness,
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

    with open(test_json, "r") as f1:
        refdata = json.load(f1)

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

        initial_partition = GeographicPartition(
            graph,
            assignment="New_Seed",
        )

        points_downsampled = tract_generation._read_and_process_vrp_shapefile(
            state_fips,
            config.STATE_NAMES[state_fips],
            config.NUM_DISTRICTS[state_fips],
            config.SAMPLE_RICHNESS,
        )

        dd_hc = ddhc.DDHumanCompactness(
            initial_partition,
            points_downsampled,
        )

        (
            old_human_compactness_function,
            reock_compactness_function,
        ) = _12_Process_Ensembles._init_metrics_(
            initial_partition,
            points_downsampled,
            duration_dict,
            tract_dict,
            tractwise_matrix,
            pointwise_sum_matrix,
            state_shapefile,
        )

        human_compactness_function = partial(
            dd_hc.calculate_human_compactness,
            tract_dict,
            pointwise_sum_matrix,
            tractwise_matrix,
        )

        new_assignment = dict(initial_partition.assignment)

        with open(datadir + f"flips_10000.json") as f:
            dict_list = json.load(f)
            calcdata = {}
            calcdata2 = {}
            for step in range(100):
                calcdata[step] = _12_Process_Ensembles.calculate_metrics_step(
                    step,
                    dict_list,
                    graph,
                    new_assignment,
                    human_compactness_function,
                    reock_compactness_function,
                )

                calcdata2[step] = _12_Process_Ensembles.calculate_metrics_step(
                    step,
                    dict_list,
                    graph,
                    new_assignment,
                    old_human_compactness_function,
                    reock_compactness_function,
                )

                assert _dicts_are_approx_equal_(
                    calcdata[step]["human_compactness"],
                    refdata[step]["human_compactness"],
                )

                assert _dicts_are_approx_equal_(
                    calcdata[step]["human_compactness"],
                    calcdata2[step]["human_compactness"],
                )
