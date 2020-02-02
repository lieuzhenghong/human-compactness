# TODO find a way to bring sample_rvps (as well as other utility functions)
# into a common library of some sort

# Import utilities for getting GEOIDs and ids of all Census Tracts
from spatial_diversity_utils import get_all_tract_geoids
from sum_driving_durations import sum_of_driving_durations_to_knn
from distance_matrix import read_duration_matrix_from_file
import human_compactness_utils
import sample_rvps
import geopandas as gpd
import sys
import numpy as np
import json

# TODO try and make this a relative path
sys.path.append('/home/lieu/dev/geographically_sensitive_dislocation/10_code')


def get_vrps_within_tracts():
    pass


def read_and_process_vrp_shapefile():
    '''
        Returns points_downsampled
    '''
    # TODO make it not only read the state of Georgia

    GEOG_WD = "/home/lieu/dev/geographically_sensitive_dislocation/00_source_data/"

    CDB = gpd.read_file(GEOG_WD +
                        "10_US_Congressional_districts/nhgis0190_shapefile_tl2014_us_cd114th_2014/US_cd114th_2014_wgs84.shp")

    STATE_CODE = 13
    DEM_RVPS = f'{GEOG_WD}00_representative_voter_points/points_D_13_2_10000_run1.shp'
    REP_RVPS = f'{GEOG_WD}00_representative_voter_points/points_R_13_2_10000_run1.shp'
    SAMPLE_SIZE = 14000

    DM_PATH = '/home/lieu/dev/geographically_sensitive_dislocation/20_intermediate_files/duration_matrix_georgia_13.dmx'

    # after we get the points, downsample

    points_downsampled = sample_rvps.sample_rvps(CDB, STATE_CODE, DEM_RVPS,
                                                 REP_RVPS, SAMPLE_SIZE)

    # Convert to WGS84
    points_downsampled = points_downsampled.to_crs({'init': 'epsg:4326'})

    # the points have already been spatial joined previously; drop this so we can do further
    # spatial joins
    points_downsampled = points_downsampled.drop('index_right', axis=1)

    return points_downsampled


def form_point_to_tract_mapping(voter, mapping):
    # get point ID
    mapping[voter.name] = geoid_to_id_mapping[voter['GEOID']]


'''
    INPUT DATA REQUIRED: 
       
    1. VRP shapefile
    2. 2000 Census Tract shapefile
    3. tract_dict
    4. GEOID to tract ID mapping (Daryl's initial assignment)

    DESIRED OUTPUT DATA:

    A dictionary of 

    

    PROCEDURE

    1. Read in Nick's VRP shapefile
    2. Downsample the VRPs (this is deterministic as I always choose seed=0)
    3. Read in the 2000 Census Tract data
    4. 
'''

CENSUS_TRACTS = gpd.read_file(
    "/home/lieu/dev/human_compactness/Data_2000/Shapefiles/Tract2000_13.shp")


# Read in Nick's VRP shapefile and downsample

points_downsampled = read_and_process_vrp_shapefile()

# Get dictionary of tracts {id: {GEOID: geoid, pop: None, pfs: None}} and the
# GEOID to ID mapping

tract_dict, geoid_to_id_mapping = get_all_tract_geoids()

# Reproject 2000 Census Tracts to use the same projection as downsampled tracts
CENSUS_TRACTS = CENSUS_TRACTS.to_crs({'init': 'epsg:4326'})

# Spatial join all points that lie in a Census Tract
# This gives us a GeoDataFrame of each VRP mapped to a GEOID of the tract
points_mapped = gpd.sjoin(
    points_downsampled, CENSUS_TRACTS, how='inner', op='within')

# The important ones are GEOID, geometry and index_right, possibly party
print(points_mapped[:10])

POINT_TO_TRACT_MAPPING = {}

# Populate the point_to_tract_mapping dictionary
points_mapped.apply(form_point_to_tract_mapping, axis=1,
                    args=[POINT_TO_TRACT_MAPPING])

# We now have a mapping from VRPs to GEOID, and from GEOID to id (geoid_to_id_mapping).
# We can now convert point_distances to tract_distances
convert_point_distances_to_tract_distances(
    POINT_TO_TRACT_MAPPING, DM_PATH, 'GEORGIA_13_TRACT_DISTANCES.json')

# Return a dictionary where key is GEOID (of tract) and values are the points
# in the GEOID

tracts_mapped = points_mapped.groupby(['GEOID'])['geometry'].apply(list)

print(tracts_mapped)
