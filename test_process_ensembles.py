#!/usr/bin/env python3

import _12_Process_Ensembles
from gerrychain import Election, GeographicPartition, Graph, Partition
from gerrychain.metrics import polsby_popper
from gerrychain.updaters import Tally, cut_edges
import spatial_diversity_utils as spatial_diversity


def _is_close_(f1: float, f2: float, epsilon=0.0001) -> bool:
    return abs(f1 - f2) < epsilon


def _dicts_are_approx_equal_(d1, d2) -> bool:
    """
    Helper function
    """
    for (k, v) in d1.items():
        print(f"Comparing {k}: \n {v} \n {d2[k]}")
        if k == "spatial_diversity":
            # v = [float, Dict[int, float]]
            if not _is_close_(v[0], d2[k][0]):
                return False
            for i in v[1]:
                if not _is_close_(v[1][i], d2[k][1][str(i)]):
                    return False
        else:
            # v = Dict[int, float]
            for i in v:
                if not _is_close_(v[i], d2[k][str(i)]):
                    return False
    return True


def test_process_ensemble_main():
    """
    Tests that the calculate metrics functions gives us the expected values
    (none of the computed values have changed).
    Very useful for regression testing.
    """
    import json

    state_fips = "09"
    test_json = f"./test/test_data/data100.json"
    datadir = f"./Tract_Ensembles/2000/{state_fips}/"

    with open(test_json, "r") as f1:
        refdata = json.load(f1)

        (
            graph,
            human_compactness_function,
            reock_compactness_function,
        ) = _12_Process_Ensembles._init_(state_fips)

        initial_partition = GeographicPartition(
            graph,
            assignment="New_Seed",
            updaters={
                "cut_edges": cut_edges,
                "population": Tally("population", alias="population"),
                "spatial_diversity": spatial_diversity.calc_spatial_diversity,
                "human_compactness": human_compactness_function,
                "reock_compactness": reock_compactness_function,
            },
        )
        new_assignment = dict(initial_partition.assignment)

        with open(datadir + f"flips_10000.json") as f:
            dict_list = json.load(f)
            calcdata = {}
            for step in range(100):
                calcdata[step] = _12_Process_Ensembles.calculate_metrics_step(
                    step,
                    dict_list,
                    graph,
                    new_assignment,
                    human_compactness_function,
                    reock_compactness_function,
                )

                # print(json.loads(json.dumps(stepdata)))
                # print("\n")
                # print(data[step])

                # assert json.loads(json.dumps(stepdata)) == data[step]
                assert _dicts_are_approx_equal_(calcdata[step], refdata[step])
