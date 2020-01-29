import geopandas as gpd
import os
import pickle
import numpy as np
import gerrychain as gc
from gerrychain import Graph
from gerrychain.tree import recursive_tree_part

all_tracts = gpd.read_file("./Tracts_2000_wPop.shp")



centroids = all_tracts.centroid


os.makedirs(os.path.dirname("./Data/Shapefiles/init.txt"), exist_ok=True)
with open("./Data/Shapefiles/init.txt", "w") as f:
    f.write("Created Folder")
    
os.makedirs(os.path.dirname("./Data/Dual_Graphs/init.txt"), exist_ok=True)
with open("./Data/Dual_Graphs/init.txt", "w") as f:
    f.write("Created Folder")

all_tracts["C_X"] = centroids.x
all_tracts["C_Y"] = centroids.y

all_tracts = all_tracts[all_tracts["GISJOIN"] != "G3600130nodata"]
#Remove weird NY Tract with no data. 

states = all_tracts["STATEA"].unique()

all_tracts["GEOID"] = (all_tracts["STATEA"].astype(int)).astype(str)+all_tracts["COUNTYA"]+all_tracts["TRACTA"]


for fips in states:

    print(f"Starting {fips}")
    
    if not os.path.exists(f"./Data/Dual_Graphs/Tract2000_{fips}.json"):
        state_tracts = all_tracts[all_tracts["STATEA"]==fips]
        
        if fips == '06':
            
            state_tracts["geometry"] = state_tracts.geometry.buffer(0)
        
        state_graph = Graph.from_geodataframe(state_tracts, ignore_errors = True)
        
        state_graph.add_data(state_tracts)
        
        state_tracts.to_file(f"./Data/Shapefiles/Tract2000_{fips}.shp")
        
        state_graph.to_json(f"./Data/Dual_Graphs/Tract2000_{fips}.json")
    
    
