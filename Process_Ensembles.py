import geopandas as gpd
import os
import pickle
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import seaborn as sns
import networkx as nx
from functools import partial
import json
import random
from maup import assign
import numpy as np
import ast


state_names={"02":"Alaska","01":"Alabama","05":"Arkansas","04":"Arizona",
"06":"California","08":"Colorado","09":"Connecticut","10":"Delaware",
"12":"Florida","13":"Georgia","66":"Guam","15":"Hawaii","19":"Iowa",
"16":"Idaho","17":"Illinois","18":"Indiana","20":"Kansas","21":"Kentucky",
"22":"Louisiana","25":"Massachusetts","24":"Maryland","23":"Maine","26":"Michigan",
"27":"Minnesota","29":"Missouri","28":"Mississippi","30":"Montana",
"37":"North_Carolina","38":"North_Dakota","31":"Nebraska","33":"New_Hampshire",
"34":"New_Jersey","35":"New_Mexico","32":"Nevada","36":"New_York","39":"Ohio",
"40":"Oklahoma","41":"Oregon","42":"Pennsylvania","72":"Puerto_Rico",
"44":"Rhode_Island","45":"South_Carolina","46":"South_Dakota","47":"Tenessee",
"48":"Texas","49":"Utah","51":"Virginia","50":"Vermont","53":"Washington",
"55":"Wisconsin","54":"West_Virginia","56":"Wyoming"}


num_elections = 1



plan_name = "Enacted"

# [TODO ask daryl why this is here]
#election_name = election_names[0]



from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges

# Import utilities for calculating spatial diversity
import spatial_diversity_utils as spatial_diversity

#fips_list = ['13','25','49','51','55']
fips_list = ['13']
    

for state_fips in fips_list:

    data = []

        
    datadir = f"./Tract_Ensembles/{state_fips}/"
    
    newdir = f"./Tract_Ensembles/{state_fips}/rerun/"
    
    os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
    with open(newdir + "init.txt", "w") as f:
        f.write("Created Folder")

    graph = Graph.from_json(datadir + 'starting_plan.json')

    # add population and spatial diversity data to the graph
    spatial_diversity_dict = spatial_diversity.build_spatial_diversity_dict(*spatial_diversity.get_all_tract_geoids())

    # just for reference
    num_Nones = 0
    for node in graph.nodes():

        if spatial_diversity_dict[node]['pfs'] is None:
            num_Nones += 1

        graph.nodes[node]['pfs'] = spatial_diversity_dict[node]['pfs']
        graph.nodes[node]['pop'] = spatial_diversity_dict[node]['pop']
        #print(graph.nodes[node])
    
    # 884 Nones! That's too many. What's going on?
    # [TODO] investigate why there are so many None values in the build_spatial_diversity_dict fn
    # [TODO] this is because we are using the 2010 Census Tract values and Stephanopoulos uses
    # 2000 Census Tract values and many of them have changed 
    print(num_Nones)


    initial_partition = Partition(
        graph,
        assignment='New_Seed',
        updaters={
            "cut_edges": cut_edges,
            "population": Tally("population", alias="population"),
            "spatial_diversity": spatial_diversity.calc_spatial_diversity,
            #"PRES2008": election
        }
    )
            
    new_assignment = dict(initial_partition.assignment)
    #load graph and make initial partition

    #load json one at a time
    max_steps = 100000
    step_size = 10000

    ts = [x * step_size for x in range(1, int(max_steps / step_size) + 1)]
        
    data.append([])

    for t in ts:

        with open(datadir+f'flips_{t}.json') as f:
            dict_list = ast.literal_eval(f.read())

            #if t = ts[0]:
            #    data.remove(0)
 
            
        

            #Make new partition by updating dictionary

            
            
        for step in range(step_size):

            changes_this_step = (dict_list[step].items())
        
            new_assignment.update({int(item[0]):int(item[1]) for item in changes_this_step})
            
            new_partition = Partition(
                graph,
                assignment=new_assignment,
                updaters={
                    "cut_edges": cut_edges,
                    "population": Tally("population", alias="population"),
                    "spatial_diversity": spatial_diversity.calc_spatial_diversity,
                }
            )
            
            print(step)
            #print(new_partition['spatial_diversity'])

            #INSERT YOUR FUNCTIONS EVALUATED ON new_partition HERE
            data[-1].append(new_partition['spatial_diversity']) 

        with open(newdir + "data" + str(t) + ".csv", "w") as tf1:
            writer = csv.writer(tf1, lineterminator="\n")
            writer.writerows(data)            
                      
        
        step_changesdata = []
