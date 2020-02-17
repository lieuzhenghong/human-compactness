import numpy as np
import geopandas as gpd
import json
import sys
import os

import spatial_diversity_utils as sd_utils
import human_compactness_utils as hc_utils

sys.path.append('/home/lieu/dev/geographically_sensitive_dislocation/10_code')

import sample_rvps  # noqa: E402

# TODO find a way to bring sample_rvps (as well as other utility functions)
# into a common library of some sort

# TODO try and make this a relative path

# Import utilities for getting GEOIDs and ids of all Census Tracts


def get_vrps_within_tracts():
    pass


def _read_and_process_vrp_shapefile(STATE_CODE, STATE_NAME, NUM_DISTRICTS, SAMPLE_RICHNESS):
    '''
        Returns points_downsampled
    '''
    GEOG_WD = "/home/lieu/dev/geographically_sensitive_dislocation/00_source_data/"

    print("Reading district shapefile...")
    CDB = gpd.read_file(GEOG_WD +
                        "10_US_Congressional_districts/nhgis0190_shapefile_tl2014_us_cd114th_2014/US_cd114th_2014_wgs84.shp")

    DEM_RVPS = f'{GEOG_WD}00_representative_voter_points/points_D_{STATE_CODE}_2_10000_run1.shp'
    REP_RVPS = f'{GEOG_WD}00_representative_voter_points/points_R_{STATE_CODE}_2_10000_run1.shp'
    SAMPLE_RICHNESS = SAMPLE_RICHNESS
    SAMPLE_SIZE = SAMPLE_RICHNESS * int(NUM_DISTRICTS)

    print(DEM_RVPS)

    DM_PATH = f'/home/lieu/dev/geographically_sensitive_dislocation/20_intermediate_files/duration_matrix_{STATE_NAME}_{STATE_CODE}.dmx'
    #DM_PATH = f'/home/lieu/dev/geographically_sensitive_dislocation/20_intermediate_files/duration_matrix_{STATE_NAME}_{STATE_CODE}_{SAMPLE_SIZE}.dmx'

    # after we get the points, downsample

    print("Downsampling points...")
    points_downsampled = sample_rvps.sample_rvps(CDB, int(STATE_CODE), DEM_RVPS,
                                                 REP_RVPS, SAMPLE_SIZE)

    # Convert to WGS84
    points_downsampled = points_downsampled.to_crs({'init': 'epsg:4326'})

    # the points have already been spatial joined previously; drop this so we can do further
    # spatial joins
    # Also drop GEOID, those are the GEOIDs of the districts (which we don't want)
    points_downsampled = points_downsampled.drop(
        ['index_right', 'GEOID'], axis=1)

    return points_downsampled


def form_point_to_tract_mapping(voter, mapping, geoid_to_id_mapping):
    '''Mutates a point_to_tract_mapping (mapping) with the tractids'''
    # voter.name refers to the point ID
    mapping[voter.name] = geoid_to_id_mapping[voter['GEOID']]


def generate_tracts_with_vrps(state_code, state_name, num_districts, sample_richness):
    '''
    Returns a tract_dict with the following schema:

        {
            tract_id: {
                'geoid': GEOID,
                'pop': Int,
                'pfs': List[Float],
                'vrps': List[PointIDs]
            }
        }

    INPUT DATA REQUIRED:

    1. VRP shapefile
    2. 2000 Census Tract shapefile
    3. tract_dict
    4. GEOID to tract ID mapping (Daryl's initial assignment)
    '''
    # All global variables here
    TRACT_SPATIAL_DIVERSITY_SCORES = '/home/lieu/dev/human_compactness/tract_spatial_diversity.csv'
    CENSUS_TRACTS = gpd.read_file(
        f"/home/lieu/dev/human_compactness/Data_2000/Shapefiles/Tract2000_{state_code}.shp")

    point_to_tract_mapping = {}

    # Read in Nick's VRP shapefile and downsample

    sample_size = int(sample_richness) * int(num_districts)

    points_downsampled = _read_and_process_vrp_shapefile(
        state_code, state_name, int(num_districts), int(sample_richness))

    print(points_downsampled)
    # print(list(points_downsampled))
    # print(points_downsampled[:10])

    # Get dictionary of tracts {id: {GEOID: geoid, pop: None, pfs: None}} and the
    # GEOID to ID mapping

    tract_dict, geoid_to_id_mapping = sd_utils.get_all_tract_geoids(state_code)

    tract_dict = sd_utils.build_spatial_diversity_dict(tract_dict,
                                                       geoid_to_id_mapping, TRACT_SPATIAL_DIVERSITY_SCORES)

    # Reproject 2000 Census Tracts to use the same projection as downsampled tracts
    CENSUS_TRACTS = CENSUS_TRACTS.to_crs({'init': 'epsg:4326'})
    # print(CENSUS_TRACTS)

    # Spatial join all points that lie in a Census Tract
    # This gives us a GeoDataFrame of each VRP mapped to a GEOID of the tract
    print("Calculating spatial join of VRPs and district shapefile...")
    points_mapped = gpd.sjoin(
        points_downsampled, CENSUS_TRACTS, how='inner', op='within')

    # The important ones are GEOID, geometry and index_right, possibly party
    print(points_mapped[:10])
    # print(list(points_mapped))

    # Populate the point_to_tract_mapping dictionary
    # We need this in order to generate the tract distance JSON file

    points_mapped.apply(form_point_to_tract_mapping, axis=1,
                        args=[point_to_tract_mapping, geoid_to_id_mapping])

    print(f'Length of point_to_tract_mapping: {len(point_to_tract_mapping)}')
    DM_PATH = f'/home/lieu/dev/geographically_sensitive_dislocation/20_intermediate_files/duration_matrix_{state_name}_{state_code}.dmx'
    #DM_PATH = f'/home/lieu/dev/geographically_sensitive_dislocation/20_intermediate_files/duration_matrix_{state_name}_{state_code}_{sample_size}.dmx'

    # Append the point ids to each census tract (where point ID is matrix row)
    pttm = point_to_tract_mapping

    # We already have the tract distances, but if we didn't, we should regenerate it
    #input("Everything OK? Press Enter if Yes, quit here if no.")

    tract_dds_filename = f'./20_intermediate_files/{state_code}_{state_name}_tract_dds.json'
    if not os.path.isfile(tract_dds_filename):
        print(
            f"Building pairwise tract distances JSON from point matrix and saving as {tract_dds_filename}...")
        hc_utils.convert_point_distances_to_tract_distances(
            pttm, DM_PATH, tract_dds_filename)
        print(f"Saved file as {tract_dds_filename}.")
    else:
        print("Pairwise tract distance JSON already exists, skipping...")

    # Build sum of driving distances
    knn_dmx_filename = f'./20_intermediate_files/{state_code}_{state_name}_knn_sum_dd.dmx'
    if not os.path.isfile(knn_dmx_filename):
        print("Building sum of K-nearest neighbour driving distance (up to 3000)...")
        hc_utils.build_knn_sum_duration_matrix(
            min(3000, sample_size), DM_PATH, knn_dmx_filename)
        print(f"Saved file as {knn_dmx_filename}.")
    else:
        print("K-nearest driving distance matrix already exists, skipping...")

    for tract_id in tract_dict:
        tract_dict[tract_id]['vrps'] = []

    for point in pttm:
        tract_dict[pttm[point]]['vrps'].append(point)

    print(f'Length of tract_dict: {len(tract_dict)}')

    # print(tract_dict)

    return tract_dict


if __name__ == "__main__":
    # (state_code, state_name, num_districts, sample_richness):
    generate_tracts_with_vrps(
        sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
