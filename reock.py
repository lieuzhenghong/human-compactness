# -*- coding: utf-8 -*-

"""
Created on Thu Feb  6 22:43:43 2020
@author: darac
"""

import geopandas as gpd
from scipy.spatial import ConvexHull
from smallestenclosingcircle import *
from timeit import default_timer as timer


def assign_district_to_row(row, geoid_to_id_mapping, partition):
    if row['id'] not in partition.assignment:
        return None
    else:
        return partition.assignment[row['id']]

def assign_id_to_row(row, geoid_to_id_mapping, partition):
    geoid = row['GEOID']
    tract_id = geoid_to_id_mapping[geoid]
    return tract_id

def reock(state_shapefile, geoid_to_id_mapping, partition):
    start = timer()

    dist_scores = {}
    ch_scores = []
    #state_shapefile["assignment"] = [partition.assignment[i]
    #                                 for i in state_shapefile.index]

    print("Assinging ID and assignment to each row in shapefile...")
    state_shapefile['id'] = state_shapefile.apply(assign_id_to_row, axis=1, args=[geoid_to_id_mapping, partition])
    state_shapefile['assignment'] = state_shapefile.apply(assign_district_to_row, axis=1, args=[geoid_to_id_mapping, partition])

    end_0 = timer()
    print(f"Time taken to do dataframe.apply: {end_0 - start}")

    print("Grouping by assignment...")
    state_grouped2 = state_shapefile.groupby("assignment")

    end_1 = timer()
    print(f"Time taken to do groupby: {end_1 - start}")


    print("Now in each district in the partition...")
    for i in range(len(partition)):
        start_0 = timer()

        x_points = []

        y_points = []

        district_group = state_grouped2.get_group(i)
        #print(district_group)
        group_geom = state_grouped2.get_group(i).geometry
        #print(group_geom) # OK. 

        nodes = partition.parts[i]
        #print(nodes) #OK, frozenset({56854, 414, 2103...})

        edge_tuples = partition["cut_edges_by_part"][i]

        #print(edge_tuples) # OK, {(737, 888), (111, 56822), .. }

        edge_tuple_extract = [i for i, j in edge_tuples] + \
            [j for i, j, in edge_tuples]

        state_boundary_nodes = [
            node for node in nodes if node in partition["boundary_nodes"]]

        # Nodes that make up the boundary of each district
        boundary_nodes = [
            node for node in nodes if node in edge_tuple_extract] + state_boundary_nodes
        
        #print(f"Boundary nodes: {boundary_nodes}") # OK

        end_2 = timer()
        print(f"Time taken to do data pre-processing (extracting edges and nodes): {end_2 - start_0}")

        for j in nodes:
            #print(district_group.dtypes)
            #print(f"Node: {j}")
            group_geom_j = district_group.loc[district_group['id'] == j].geometry
            #print(group_geom_j)
            #print(len(group_geom_j))

            if j not in boundary_nodes:
                continue

            if group_geom_j.exterior.iloc[0] is None: # Tract not in GEOID to ID mapping
                continue

            if 'multi' in str(type(group_geom_j)):
                raise ValueError("I've commented this code out because i don't expect to deal with MultiPolygons")
                '''
                for z in range(len(group_geom[j])):
                    x, y = group_geom[j][z].exterior.coords.xy
                    x_points = x_points + list(x)
                    y_points = y_points + list(y)
                '''

            else:
                #x, y = district_group.loc['id' == j].geometry.exterior.coords.xy
                #print(group_geom_j.exterior)
                #print(type(group_geom_j.exterior))
                #print(type(group_geom_j.exterior.iloc[0]))

                x, y = group_geom_j.exterior.iloc[0].coords.xy # OK

                #x, y = group_geom[j].exterior.coords.xy #this line is the issue

                x_points = x_points + list(x)

                y_points = y_points + list(y)

        end_3 = timer()
        print(f"Time taken to find all external points: {end_3 - start_0}")
        points = list(zip(x_points, y_points))

        print(f"Calculating Convex Hull...")
        hull = ConvexHull(points)
        end_4 = timer()
        print(f"Time taken to calculate convex hull: {end_4 - start_0}")

        vertices = hull.vertices
        area_district = partition["area"][i]

        # Calculation of Reock here
        print("Calculating Reock score...")
        new_points = [points[i] for i in vertices]

        radius_bound_circle = make_circle(new_points)[2]
        end_5 = timer()
        print(f"Time taken to call make_circle: {end_5 - start_0}")

        area_circle = math.pi*(radius_bound_circle**2)
        reock_score = area_district/area_circle
        dist_scores[i] = reock_score

    end_6 = timer()
    print(f"Time taken to calculate all Reock scores: {end_6 - start}")
    #print(f"Reock scores: {dist_scores}")
    return dist_scores
