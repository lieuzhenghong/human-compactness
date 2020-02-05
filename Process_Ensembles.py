import ast
import csv
import os
import pickle
import random
import sys
import json
from functools import partial

import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import seaborn as sns
from maup import assign

import human_compactness_utils as hc_utils
import spatial_diversity_utils as spatial_diversity
import tract_generation
from gerrychain import Election, GeographicPartition, Graph, Partition
from gerrychain.metrics import polsby_popper
from gerrychain.updaters import Tally, cut_edges
from timeit import default_timer as timer

matplotlib.use('Agg')


state_names = {"02": "Alaska", "01": "Alabama", "05": "Arkansas", "04": "Arizona",
               "06": "California", "08": "Colorado", "09": "Connecticut", "10": "Delaware",
               "12": "Florida", "13": "Georgia", "66": "Guam", "15": "Hawaii", "19": "Iowa",
               "16": "Idaho", "17": "Illinois", "18": "Indiana", "20": "Kansas", "21": "Kentucky",
               "22": "Louisiana", "25": "Massachusetts", "24": "Maryland", "23": "Maine", "26": "Michigan",
               "27": "Minnesota", "29": "Missouri", "28": "Mississippi", "30": "Montana",
               "37": "North_Carolina", "38": "North_Dakota", "31": "Nebraska", "33": "New_Hampshire",
               "34": "New_Jersey", "35": "New_Mexico", "32": "Nevada", "36": "New_York", "39": "Ohio",
               "40": "Oklahoma", "41": "Oregon", "42": "Pennsylvania", "72": "Puerto_Rico",
               "44": "Rhode_Island", "45": "South_Carolina", "46": "South_Dakota", "47": "Tenessee",
               "48": "Texas", "49": "Utah", "51": "Virginia", "50": "Vermont", "53": "Washington",
               "55": "Wisconsin", "54": "West_Virginia", "56": "Wyoming"}

num_elections = 1

plan_name = "Enacted"

# fips_list = ['13','25','49','51','55']
#fips_list = ['13']
fips_list = ['22']


for state_fips in fips_list:
    DD_PATH = f'./{state_fips}_{state_names[state_fips].lower()}_tract_dds.json'
    DURATION_DICT = hc_utils.read_tract_duration_json(DD_PATH)
    DM_PATH = f'./{state_fips}_{state_names[state_fips].lower()}_knn_sum_dd.dmx'

    sys.path.append(
        '/home/lieu/dev/geographically_sensitive_dislocation/10_code')

    import distance_matrix  # noqa: E402

    print("Reading KNN duration matrix file into memory...")
    DMX = distance_matrix.read_duration_matrix_from_file(DM_PATH)

    data = []

    # datadir = f"./Tract_Ensembles/{state_fips}/"
    datadir = f"./Tract_Ensembles/2000/{state_fips}/"

    newdir = f"./Tract_Ensembles/2000/{state_fips}/rerun/"

    os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
    with open(newdir + "init.txt", "w") as f:
        f.write("Created Folder")

    graph = Graph.from_json(datadir + 'starting_plan.json')

    # add population and spatial diversity data to the graph
    # tract_dict = spatial_diversity.build_spatial_diversity_dict(
    #    *spatial_diversity.get_all_tract_geoids())

    tract_dict = tract_generation.generate_tracts_with_vrps()

    # just for reference
    num_Nones = 0
    for node in graph.nodes():

        if tract_dict[node]['pfs'] is None:
            num_Nones += 1

        graph.nodes[node]['pfs'] = tract_dict[node]['pfs']
        graph.nodes[node]['pop'] = tract_dict[node]['pop']
        # print(graph.nodes[node])

    # Checking the number of empty tracts (tracts without VRPs)
    empty_tracts = []

    for tract_id in tract_dict:
        if len(tract_dict[tract_id]['vrps']) == 0:
            #print(f"Tract {tract_id} is empty")
            empty_tracts.append(tract_id)

    print(f"Number of empty tracts: {len(empty_tracts)}")
    #print(f"IDs of empty tracts: {empty_tracts}")

    initial_partition = GeographicPartition(
        graph,
        assignment='New_Seed',
        updaters={
            "cut_edges": cut_edges,
            "population": Tally("population", alias="population"),
            "spatial_diversity": spatial_diversity.calc_spatial_diversity,
            "human_compactness": partial(hc_utils.calculate_human_compactness,
                                         DURATION_DICT, tract_dict, DMX),
            "polsby_compactness": polsby_popper,
            # "PRES2008": election
        }
    )

    new_assignment = dict(initial_partition.assignment)
    # load graph and make initial partition

    # load json one at a time
    print("Loading JSON files...")

    max_steps = 100000
    step_size = 10000
    save_step_size = 1000

    ts = [x * step_size for x in range(1, int(max_steps / step_size) + 1)]

    data.append([])

    for t in ts:

        with open(datadir+f'flips_{t}.json') as f:
            dict_list = ast.literal_eval(f.read())

            # Make new partition by updating dictionary

        for step in range(step_size):

            start = timer()

            changes_this_step = (dict_list[step].items())
            print(f'Changes this step: {len(changes_this_step)}')

            new_assignment.update(
                {int(item[0]): int(item[1]) for item in changes_this_step})

            new_partition = GeographicPartition(
                graph,
                assignment=new_assignment,
                updaters={
                    "cut_edges": cut_edges,
                    "population": Tally("population", alias="population"),
                    "spatial_diversity": spatial_diversity.calc_spatial_diversity,
                    "human_compactness": partial(hc_utils.calculate_human_compactness,
                                                 DURATION_DICT, tract_dict, DMX),
                    "polsby_compactness": polsby_popper,
                }
            )

            print(f'Step number: {step}')
            # print("Calculating spatial diversity...")
            # print(new_partition['spatial_diversity'])
            # print("Calculating human compactness...")
            # print(new_partition['human_compactness'])
            # print("Calculating Polsby-Popper compactness...")
            # print(new_partition['polsby_compactness'])

            # INSERT YOUR FUNCTIONS EVALUATED ON new_partition HERE
            data[-1].append(
                {
                    'spatial_diversity': new_partition['spatial_diversity'],
                    'human_compactness': new_partition['human_compactness'],
                    'polsby_compactness': new_partition['polsby_compactness']
                })

            end = timer()

            print(f"Time taken for step {step}: {end-start}")

            if step % save_step_size == 0:
                print(f'Saving results as {str(t-step_size + step)}.json')
                with open(newdir + "data" + str(t-step_size + step) + ".json", "w") as tf1:
                    json.dump(data[-1], tf1)
                    # We need to throw away the old data
                    # otherwise we'll run out of memory
                    # data.append([])
                    data = []
                    #writer = csv.writer(tf1, lineterminator="\n")
                    # writer.writerows(data)

        step_changesdata = []
