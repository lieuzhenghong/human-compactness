#!/usr/bin/env python3

import _12_Process_Ensembles
from gerrychain import Election, GeographicPartition, Graph, Partition
from gerrychain.metrics import polsby_popper
from gerrychain.updaters import Tally, cut_edges
import spatial_diversity_utils as spatial_diversity


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
        data = json.load(f1)

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
            for step in range(100):
                stepdata = _12_Process_Ensembles.calculate_metrics_step(
                    step,
                    dict_list,
                    graph,
                    new_assignment,
                    human_compactness_function,
                    reock_compactness_function,
                )

                print(json.loads(json.dumps(stepdata)))
                print("\n")
                print(data[step])

                assert json.loads(json.dumps(stepdata)) == data[step]

