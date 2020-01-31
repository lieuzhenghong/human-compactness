import geopandas as gpd
import os
import pickle
import csv
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt 
import networkx as nx
from functools import partial
import json
import random
from gerrychain.tree import recursive_tree_part
from gerrychain import Graph
###########
# Get environment var from SLURM
# and convert
###########

state_fips = '08'
num_districts = 7

'''
Currently Running:
1 - UT
2 - PA 
3 - OH (1 Island)
4 - GA (3 Islands)
5 - WI (1 Island)
6 - LA
7 - AZ
8 - KY
9 - CO
'''



newdir = f"./Tract_Ensembles/2000/{state_fips}/"
os.makedirs(os.path.dirname(newdir + "init.txt"), exist_ok=True)
with open(newdir + "init.txt", "w") as f:
    f.write("Created Folder")

##########
# Set Initial Partition
##########

from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges

graph = Graph.from_json(f'./Data_2000/Dual_Graphs/Tract2000_{state_fips}.json')

print(nx.is_connected(graph))
print([len(x) for x in nx.connected_components(graph)])

#graph = graph.subgraph(list(nx.connected_components(graph))[0])
#print(len(graph))

totpop = 0

for n in graph.nodes():
    graph.nodes[n]["FL5001"] = int(graph.nodes[n]["FL5001"])
    totpop += graph.nodes[n]["FL5001"]

cddict =  recursive_tree_part(graph, range(num_districts), 
                                          totpop / num_districts, "FL5001", .02, 1)

            
for node in graph.nodes():
    graph.nodes[node]['New_Seed'] = cddict[node]

graph.to_json(newdir + 'starting_plan.json')


initial_partition = Partition(
    graph,
    assignment='New_Seed',
    updaters={
        "cut_edges": cut_edges,
        "population": Tally("FL5001", alias="population"),
    }
)


############
# Uniform Tree Utilities
############
from gerrychain.tree import recursive_tree_part, bipartition_tree_random, PopulatedGraph,contract_leaves_until_balanced_or_none,find_balanced_edge_cuts


def get_spanning_tree_u_w(G):
    node_set=set(G.nodes())
    x0=random.choice(tuple(node_set))
    x1=x0
    while x1==x0:
        x1=random.choice(tuple(node_set))
    node_set.remove(x1)
    tnodes ={x1}
    tedges=[]
    current=x0
    current_path=[x0]
    current_edges=[]
    while node_set != set():
        next=random.choice(list(G.neighbors(current)))
        current_edges.append((current,next))
        current = next
        current_path.append(next)

        if next in tnodes:
            for x in current_path[:-1]:
                node_set.remove(x)
                tnodes.add(x)
            for ed in current_edges:
                tedges.append(ed)
            current_edges = []
            if node_set != set():
                current=random.choice(tuple(node_set))
            current_path=[current]


        if next in current_path[:-1]:
            current_path.pop()
            current_edges.pop()
            for i in range(len(current_path)):
                if current_edges !=[]:
                    current_edges.pop()
                if current_path.pop() == next:
                    break
            if len(current_path)>0:
                current=current_path[-1]
            else:
                current=random.choice(tuple(node_set))
                current_path=[current]

    #tgraph = Graph()
    #tgraph.add_edges_from(tedges)
    return G.edge_subgraph(tedges)

def my_uu_bipartition_tree_random(
    graph,
    pop_col,
    pop_target,
    epsilon,
    node_repeats=1,
    spanning_tree=None,
    choice=random.choice):
    populations = {node: graph.nodes[node][pop_col] for node in graph}

    possible_cuts = []
    #if spanning_tree is None:
    #    spanning_tree = get_spanning_tree_u_w(graph)

    tree_attempts = 0
    while len(possible_cuts) == 0:
        tree_attempts += 1
        if tree_attempts == 25:
            #print('25 trees')
            return set()
        spanning_tree = get_spanning_tree_u_w(graph)
        h = PopulatedGraph(spanning_tree, populations, pop_target, epsilon)
        possible_cuts = find_balanced_edge_cuts(h, choice=choice)

    return choice(possible_cuts).subset



############
# Run a simulation!
############

from gerrychain import MarkovChain
from gerrychain.constraints import single_flip_contiguous, contiguous_bfs, within_percent_of_ideal_population
from gerrychain.proposals import propose_random_flip
from gerrychain.accept import always_accept
from gerrychain.metrics import efficiency_gap, mean_median, partisan_bias, partisan_gini
from gerrychain.proposals import recom


ideal_population = sum(initial_partition["population"].values()) / len(
    initial_partition
)

proposal = partial(
    recom, pop_col="FL5001", pop_target=ideal_population, epsilon=0.01, node_repeats=1, method =my_uu_bipartition_tree_random)
    
threshold = 0.02
    
chain = MarkovChain(
    proposal=proposal,
    constraints=[within_percent_of_ideal_population(initial_partition, threshold)],
    accept=always_accept,
    initial_state=initial_partition,
    total_steps=100000
)

pos = {node:(float(graph.nodes[node]['C_X']), float(graph.nodes[node]['C_Y'])) for node in graph.nodes}


pop_vec = []
cut_vec = []

chain_flips = []

step_index = 0
for part in chain: 
    step_index += 1
    
    if part.flips is not None:
        chain_flips.append(dict(part.flips))
    else: 
        chain_flips.append(dict())
    #Too much writing!
    #if part.flips is not None:
    #    with open(newdir+f'flips_{step_index}.json', 'w') as fp:
    #        json.dump(dict(part.flips), fp)
    #else:
    #    with open(newdir+f'flips_{step_index}.json', 'w') as fp:
    #        json.dump(dict(), fp)


    pop_vec.append(sorted(list(part["population"].values())))
    cut_vec.append(len(part["cut_edges"]))
        
    if step_index % 10000 == 0:
        print(step_index)
        
        with open(newdir+f'flips_{step_index}.json', 'w') as fp1:
            json.dump(chain_flips, fp1)
        
        with open(newdir + "pop" + str(step_index) + ".csv", "w") as tf1:
            writer = csv.writer(tf1, lineterminator="\n")
            writer.writerows(pop_vec)

        with open(newdir + "cuts" + str(step_index) + ".csv", "w") as tf1:
            writer = csv.writer(tf1, lineterminator="\n")
            writer.writerows([cut_vec])     
            
            
        plt.figure(figsize=(8, 6), dpi=500)
        nx.draw(graph, pos=pos, node_color=[dict(part.assignment)[node] for node in graph.nodes()], node_size = 20, cmap='tab20')                   
        plt.savefig(newdir + "plot" + str(step_index) + ".png")
        plt.close()
        
        pop_vec = []
        cut_vec = []
        chain_flips = []

        
    
