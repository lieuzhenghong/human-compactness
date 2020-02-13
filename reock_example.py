

# -*- coding: utf-8 -*-

"""

Created on Thu Feb  6 22:43:43 2020

​

@author: darac

"""

​

​

import csv

import os

import shutil

from functools import partial

import json

import math

import numpy as np

import geopandas as gpd

import matplotlib

#matplotlib.use('Agg')

import seaborn as sns

import matplotlib.pyplot as plt

import matplotlib.ticker as ticker

import pandas

import random

import pandas as pd

from gerrychain import (

    Election,

    Graph,

    MarkovChain,

    Partition,

    accept,

    constraints,

    updaters,

)

from gerrychain.metrics import efficiency_gap, mean_median

from gerrychain.proposals import recom

from gerrychain.updaters import cut_edges

from gerrychain.updaters import *

from gerrychain.tree import recursive_tree_part

from gerrychain.updaters import Tally

from min_bound_circle import *

from gerrychain import GeographicPartition

from scipy.spatial import ConvexHull

from gerrychain.proposals import recom, propose_random_flip

from gerrychain.tree import recursive_tree_part

from gerrychain.accept import always_accept

from gerrychain.constraints import single_flip_contiguous, Validator

from networkx import is_connected, connected_components

import collections

from enum import Enum

import sys

​

import time

start_time = time.time()

​

plot_path = 'bgs_south/bgs_south.shp' 

​

state_gdf = gpd.read_file(plot_path)

graph = Graph.from_file(plot_path, ignore_errors = True)

​

#columns from GeoDF for processing

tot_pop = 'TOTPOP'

white_pop = 'NH_WHITE'

other_pop = 'NH_OTHER'

hisp_pop = "HISP"

black_pop = "NH_BLACK"

tot_cvap = "CVAP"

white_cvap = "WCVAP"

hisp_cvap = "HCVAP"

black_cvap = "BCVAP"

asian_cvap = "ACVAP"

tot_vap = "VAP"

white_vap = "WVAP"

hisp_vap = "HVAP"

black_vap = "BVAP"

other_vap = "OTHERVAP"

geo_id = 'GEOID'

county_split_id = "COUNTYFP"

​

​

#assignment (initial graph!)

assignment1= 'USCD'

​

​

beta = float(sys.argv[1])

burst = float(sys.argv[2])

run_name  = sys.argv[3]

​

total_steps = 100000

hcvap_dists = 7

hcvap_thresh = .5

bcvap_thresh = .50

bcvap_dists = 0

k_worst_dists = 3

pop_tol = .01 #U.S. Cong

#beta = 25 #in acceptance function in exponential

alpha = 1

#burst = 10 #burst length

​

  

def reock(partition):

    dist_scores = []

    state_gdf2 = state_gdf

    state_gdf2["assignment"] = [partition.assignment[i] for i in state_gdf2.index]

    state_grouped2 = state_gdf2.groupby("assignment")

    for i in range(len(partition)):

        x_points = []

        y_points = []

        group_geom = state_grouped2.get_group(i).geometry

        nodes = partition.parts[i]

        edge_tuples = partition["cut_edges_by_part"][i]

        edge_tuple_extract = [i for i,j in edge_tuples] + [j for i,j, in edge_tuples]

        state_boundary_nodes = [node for node in nodes if node in partition["boundary_nodes"] ]

        boundary_nodes = [node for node in nodes if node in edge_tuple_extract] + state_boundary_nodes           

        for j in nodes: 

            if j not in boundary_nodes:

                continue

            if 'multi' in str(type(group_geom[j])):  #to deal with case of multi-polygons             

                for z in range(len(group_geom[j])):

                    x, y = group_geom[j][z].exterior.coords.xy

                    x_points = x_points + list(x)

                    y_points = y_points + list(y)

            else:

                x, y = group_geom[j].exterior.coords.xy

                x_points = x_points + list(x)

                y_points = y_points + list(y)

        points = list(zip(x_points, y_points))

        hull = ConvexHull(points)

        vertices = hull.vertices

        new_points = [points[i] for i in vertices]

        radius_bound_circle = make_circle(new_points)[2]

        area_circle = math.pi*(radius_bound_circle**2)

        area_district = partition["area"][i]

        reock_score = area_district/area_circle

        dist_scores.append(reock_score)
    
    return dist_scores

        

    sorted_dist_scores = sorted(dist_scores)

    ave_worst_k = sum(sorted_dist_scores[:k_worst_dists])/k_worst_dists

    #returns: average of all dists, average of k-worst dists and list of dist scores orderd by partition key

    return (sum(dist_scores)/len(dist_scores)) #, ave_worst_k, dist_scores




