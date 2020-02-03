import numpy as np
import geopandas as gpd
import json
import sys

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


def read_and_process_vrp_shapefile():
    '''
        Returns points_downsampled
    '''
    # TODO make it not only read the state of Georgia

    GEOG_WD = "/home/lieu/dev/geographically_sensitive_dislocation/00_source_data/"

    print("Reading district shapefile...")
    CDB = gpd.read_file(GEOG_WD +
                        "10_US_Congressional_districts/nhgis0190_shapefile_tl2014_us_cd114th_2014/US_cd114th_2014_wgs84.shp")

    STATE_CODE = 13
    DEM_RVPS = f'{GEOG_WD}00_representative_voter_points/points_D_13_2_10000_run1.shp'
    REP_RVPS = f'{GEOG_WD}00_representative_voter_points/points_R_13_2_10000_run1.shp'
    SAMPLE_SIZE = 14000

    DM_PATH = '/home/lieu/dev/geographically_sensitive_dislocation/20_intermediate_files/duration_matrix_georgia_13.dmx'

    # after we get the points, downsample

    print("Calculating spatial join of VRPs and district shapefile...")
    points_downsampled = sample_rvps.sample_rvps(CDB, STATE_CODE, DEM_RVPS,
                                                 REP_RVPS, SAMPLE_SIZE)

    # Convert to WGS84
    points_downsampled = points_downsampled.to_crs({'init': 'epsg:4326'})

    # the points have already been spatial joined previously; drop this so we can do further
    # spatial joins
    # Also drop GEOID, those are the GEOIDs of the districts (which we don't want)
    points_downsampled = points_downsampled.drop(
        ['index_right', 'GEOID'], axis=1)

    return points_downsampled


def form_point_to_tract_mapping(voter, mapping):
    # voter.name refers to the point ID
    mapping[voter.name] = geoid_to_id_mapping[voter['GEOID']]


'''
    INPUT DATA REQUIRED:

    1. VRP shapefile
    2. 2000 Census Tract shapefile
    3. tract_dict
    4. GEOID to tract ID mapping (Daryl's initial assignment)

    DESIRED OUTPUT DATA:

    A dictionary of

    {
        id: {
            GEOID: geoid,
            pfs: [Float],
            pop: Int,
            durations: {
                tract_id: Float
            }
        }
    }

    PROCEDURE

    1. Read in Nick's VRP shapefile
    2. Downsample the VRPs (this is deterministic as I always choose seed=0)
    3. Read in the 2000 Census Tract data
    4.
'''

# All global variables here
TRACT_SPATIAL_DIVERSITY_SCORES = '/home/lieu/dev/human_compactness/tract_spatial_diversity.csv'
POINT_TO_TRACT_MAPPING = {}
CENSUS_TRACTS = gpd.read_file(
    "/home/lieu/dev/human_compactness/Data_2000/Shapefiles/Tract2000_13.shp")

# Read in Nick's VRP shapefile and downsample

points_downsampled = read_and_process_vrp_shapefile()
print(list(points_downsampled))
print(points_downsampled[:10])

# Get dictionary of tracts {id: {GEOID: geoid, pop: None, pfs: None}} and the
# GEOID to ID mapping

tract_dict, geoid_to_id_mapping = sd_utils.get_all_tract_geoids()

# tract_dict = sd_utils.build_spatial_diversity_dict(tract_dict, geoid_to_id_mapping, TRACT_SPATIAL_DIVERSITY_SCORES):

# Reproject 2000 Census Tracts to use the same projection as downsampled tracts
CENSUS_TRACTS = CENSUS_TRACTS.to_crs({'init': 'epsg:4326'})
print(CENSUS_TRACTS)

# Spatial join all points that lie in a Census Tract
# This gives us a GeoDataFrame of each VRP mapped to a GEOID of the tract
points_mapped = gpd.sjoin(
    points_downsampled, CENSUS_TRACTS, how='inner', op='within')

# The important ones are GEOID, geometry and index_right, possibly party
print(points_mapped[:10])
print(list(points_mapped))

# Populate the point_to_tract_mapping dictionary
# We need this in order to generate the tract distance JSON file

points_mapped.apply(form_point_to_tract_mapping, axis=1,
                    args=[POINT_TO_TRACT_MAPPING])

# We already have the tract distances, but if we didn't, we should regenerate it
print(len(POINT_TO_TRACT_MAPPING))

DM_PATH = '/home/lieu/dev/geographically_sensitive_dislocation/20_intermediate_files/duration_matrix_georgia_13.dmx'

#print('Calculating the sum of driving durations for each tract...')
#hc_utils.convert_point_distances_to_tract_distances(POINT_TO_TRACT_MAPPING,
#                                                    DM_PATH, './13_georgia_tract_dds.json')

# Similarly, regenerate the knn_sum_dds
#
# This takes a damn long time. I'm not sure why --- maybe sorting? Or maybe my
# computer's just throttled. It seems to freeze for some reason

print('Calculating the sum of KNN driving durations for each tract...')
hc_utils.calc_knn_sum_durations_by_tract(POINT_TO_TRACT_MAPPING,
                                         1000, DM_PATH, './13_georgia_knn_dd_sums.json')

# tracts_mapped is a GeoDataFrame which maps Census Tract GEOIDs to a list of points under them
# why do we need this again?
# tracts_mapped = points_mapped.groupby(['GEOID'])['geometry'].apply(list)
