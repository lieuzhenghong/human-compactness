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
        #print(district_group) # list of census tracts

        '''
             NHGISST NHGISCTY         GISJOIN  ...                                           geometry     id  assignment
        25       220     0330  G2200330003804  ...  POLYGON ((470835.387 -779019.555, 471198.998 -...  27091           4
        27       220     0330  G2200330003805  ...  POLYGON ((473429.377 -780011.781, 473639.173 -...  27093           4
        30       220     0470  G2200470952700  ...  POLYGON ((448458.044 -787874.090, 448468.579 -...  27195           4
        47       220     0050  G2200050030500  ...  POLYGON ((500706.735 -792557.784, 500734.728 -...  27218           4
        48       220     0050  G2200050030900  ...  POLYGON ((479970.671 -805914.430, 480782.226 -...  27219           4
        '''

        group_geom = district_group.geometry
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

        start_1 = timer()


        # Get all the external points of all Census Tract in a district
        # Idea: exterior_points only has to be calculated once!
        # Then, given a specific assignment of tracts to districts, we can do a GroupBy assignment and
        # concatenate the external points.

        blank_nodes = 0

        for j in nodes: # For each Census Tract in a district
            if j not in boundary_nodes:
                continue

            # Find the geometry of that Census Tract
            group_geom_j = district_group.loc[district_group['id'] == j].geometry

            if group_geom_j is None:
                print(j)
                raise ValueError(f"tract id {j} not found")

            assert(len(group_geom_j.geom_type == 1))

            # group_geom_j is a MultiPolygon
            if group_geom_j.geom_type.iloc[0] == 'MultiPolygon':
                print(group_geom_j)
                print(len(group_geom_j))

                print(group_geom_j.geoms)

                for polygon in group_geom_j:
                    print(polygon)
                    print(polygon.exterior)
                    x, y = polygon.exterior.iloc[0].coords.xy
                    x_points = x_points + list(x)
                    y_points = y_points + list(y)

                '''
                if 'multi' in str(type(group_geom_j)):
                    raise ValueError("I've commented this code out because i don't expect to deal with MultiPolygons")
                    for z in range(len(group_geom[j])):
                        x, y = group_geom[j][z].exterior.coords.xy
                        x_points = x_points + list(x)
                        y_points = y_points + list(y)
                '''

            else:
                start_j = timer()
                exterior_points = group_geom_j.exterior.iloc[0] 
                end_j = timer()
                #print(f"Time taken to find exterior point of Census Tract {j}: {end_j - start_j}")

                if exterior_points is None: # Tract not in GEOID to ID mapping
                    blank_nodes += 1
                    print(group_geom_j)
                    print(str(type(group_geom_j)))
                    print(group_geom_j.geom_type)
                    raise ValueError("Hmm")
                    continue

                x, y = exterior_points.coords.xy # OK
                x_points = x_points + list(x)
                y_points = y_points + list(y)


        print(f"Number of tracts not in GEOID to ID mapping: {blank_nodes}")

        end_3 = timer()
        print(f"Time taken to find all external points: {end_3 - start_1}")
        points = list(zip(x_points, y_points))

        start_2 = timer()
        print(f"Calculating Convex Hull...")
        hull = ConvexHull(points)
        end_4 = timer()
        print(f"Time taken to calculate convex hull: {end_4 - start_2}")

        vertices = hull.vertices
        area_district = partition["area"][i]

        # Calculation of Reock here
        print("Calculating Reock score...")
        new_points = [points[i] for i in vertices]

        start_3 = timer()
        radius_bound_circle = make_circle(new_points)[2]
        end_5 = timer()
        print(f"Time taken to call make_circle: {end_5 - start_3}")

        area_circle = math.pi*(radius_bound_circle**2)
        reock_score = area_district/area_circle
        assert(reock_score < 1)
        dist_scores[i] = reock_score

    end_6 = timer()
    print(f"Time taken to calculate all Reock scores: {end_6 - start}")
    print(f"Reock scores: {dist_scores}")
    return dist_scores
