import ast
import csv
import os
import pickle
import random
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
from gerrychain import Election, Graph, Partition, GeographicPartition
from gerrychain.metrics import polsby_popper
from gerrychain.updaters import Tally, cut_edges

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

DD_PATH = './13_georgia_tract_dds.json'
DURATION_DICT = hc_utils.read_tract_duration_json(DD_PATH)
KNN_DD_PATH = './13_georgia_knn_dd_sums.json'
KNN_DICT = hc_utils.read_tract_duration_json(KNN_DD_PATH)

plan_name = "Enacted"

# fips_list = ['13','25','49','51','55']
fips_list = ['13']


for state_fips in fips_list:

    data = []

    # datadir = f"./Tract_Ensembles/{state_fips}/"
    datadir = f"./Tract_Ensembles/2000/{state_fips}/"

    newdir = f"./Tract_Ensembles/2000/{state_fips}/rerun/"

    os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
    with open(newdir + "init.txt", "w") as f:
        f.write("Created Folder")

    graph = Graph.from_json(datadir + 'starting_plan.json')

    # add population and spatial diversity data to the graph
    spatial_diversity_dict = spatial_diversity.build_spatial_diversity_dict(
        *spatial_diversity.get_all_tract_geoids())

    # just for reference
    num_Nones = 0
    for node in graph.nodes():

        if spatial_diversity_dict[node]['pfs'] is None:
            num_Nones += 1

        graph.nodes[node]['pfs'] = spatial_diversity_dict[node]['pfs']
        graph.nodes[node]['pop'] = spatial_diversity_dict[node]['pop']
        # print(graph.nodes[node])

    print(f'Number of districts without a PF score: {num_Nones}')

    initial_partition = GeographicPartition(
        graph,
        assignment='New_Seed',
        updaters={
            "cut_edges": cut_edges,
            "population": Tally("population", alias="population"),
            "spatial_diversity": spatial_diversity.calc_spatial_diversity,
            "human_compactness": partial(hc_utils.calculate_human_compactness, DURATION_DICT),
            "polsby_compactness": polsby_popper,
            # "PRES2008": election
        }
    )

    new_assignment = dict(initial_partition.assignment)
    # load graph and make initial partition

    # load json one at a time
    max_steps = 100000
    step_size = 10000

    ts = [x * step_size for x in range(1, int(max_steps / step_size) + 1)]

    data.append([])

    for t in ts:

        with open(datadir+f'flips_{t}.json') as f:
            dict_list = ast.literal_eval(f.read())

            # Make new partition by updating dictionary

        for step in range(step_size):

            changes_this_step = (dict_list[step].items())
            print(len(changes_this_step))

            new_assignment.update(
                {int(item[0]): int(item[1]) for item in changes_this_step})

            new_partition = GeographicPartition(
                graph,
                assignment=new_assignment,
                updaters={
                    "cut_edges": cut_edges,
                    "population": Tally("population", alias="population"),
                    "spatial_diversity": spatial_diversity.calc_spatial_diversity,
                    "human_compactness": partial(hc_utils.calculate_human_compactness, DURATION_DICT, KNN_DICT),
                    "polsby_compactness": polsby_popper,
                }
            )

            print(f'Step number: {step}')
            print("Calculating spatial diversity...")
            print(new_partition['spatial_diversity'])
            print("Calculating human compactness...")
            print(new_partition['human_compactness'])
            print("Calculating Polsby-Popper compactness...")
            print(new_partition['polsby_compactness'])

            # INSERT YOUR FUNCTIONS EVALUATED ON new_partition HERE
            data[-1].append({
                'spatial_diversity': new_partition['spatial_diversity'],
                'human_compactness': new_partition['human_compactness'],
                'polsby_compactness': new_partition['polsby_compactness']
            })

        with open(newdir + "data" + str(t) + ".csv", "w") as tf1:
            writer = csv.writer(tf1, lineterminator="\n")
            writer.writerows(data)

        step_changesdata = []
