import geopandas as gpd
import sys

# TODO try and make this a relative path
sys.path.append('/home/lieu/dev/geographically_sensitive_dislocation/10_code')

# TODO find a way to bring sample_rvps (as well as other utility functions)
# into a common library of some sort

# downsamples RVPs from Nick's code
import sample_rvps

# read and return a 2D array of floats
from distance_matrix import read_duration_matrix_from_file

# sum_of_driving_durations_to_knn(voter, dds, k: int)
# voter is a row of the table, dds is a numpy 2D array where dds[idx] gives the distance
# from a voter idx to all others
#from sum_driving_durations import sum_of_driving_durations_to_knn

# Import utilities for getting GEOIDs and ids of all Census Tracts
from spatial_diversity_utils import get_all_tract_geoids

tract_dict, geoid_to_id_mapping = get_all_tract_geoids()

'''
Returns a dictionary with key ID and values: {
    VRPS: [Point],
    TRACT_VRPS_KNN_DD_SUM: Float
    DD_TO_TRACT: {id: Float}
}
where VRPS is all the VRPs in the tract, TRACT_VRPS_KNN_DD_SUM is the sum of all
the driving durations of all the k-nearest-neighbours of all VRPs in the tract,
and DD_TO_TRACT (initially empty) is a dictionary giving the sum of driving
durations from all points in the tract to all points in another tract.

The dictionary should be used in Process_Ensembles.py to update the nodes in
the graph with spatial data.
'''
def get_vrps_within_tracts():
    pass


#TODO make it not only read the state of Georgia

GEOG_WD = "/home/lieu/dev/geographically_sensitive_dislocation/00_source_data/"

CDB = gpd.read_file(GEOG_WD +
"10_US_Congressional_districts/nhgis0190_shapefile_tl2014_us_cd114th_2014/US_cd114th_2014_wgs84.shp")

STATE_CODE = 13
DEM_RVPS = f'{GEOG_WD}00_representative_voter_points/points_D_13_2_10000_run1.shp'
REP_RVPS = f'{GEOG_WD}00_representative_voter_points/points_R_13_2_10000_run1.shp'
SAMPLE_SIZE = 14000

# after we get the points, downsample

points_downsampled = sample_rvps.sample_rvps(CDB, STATE_CODE, DEM_RVPS,
                                             REP_RVPS, SAMPLE_SIZE)

# Convert to WGS84
points_downsampled = points_downsampled.to_crs({'init': 'epsg:4326'})
points_downsampled = points_downsampled.drop('index_right', axis=1)

print(points_downsampled[:10])

print(list(points_downsampled))

# We only need the points' geometry for our purpose
points_downsampled = points_downsampled[['geometry', 'party']]

CENSUS_TRACTS = gpd.read_file("/home/lieu/dev/human_compactness/Data_2000/Shapefiles/Tract2000_13.shp")

CENSUS_TRACTS = CENSUS_TRACTS.to_crs({'init': 'epsg:4326'})
print(CENSUS_TRACTS[:10])

print(list(CENSUS_TRACTS))

# Spatial join all points that lie in a Census Tract
points_mapped = gpd.sjoin(points_downsampled, CENSUS_TRACTS, how='inner', op='within')

# The important ones are GEOID, geometry and index_right, possibly party
print(points_mapped[:10])
print(list(points_mapped))
print(points_mapped[['GEOID', 'geometry']])

# Return a dictionary where key is GEOID (of tract) and values are the points
# in the GEOID

tracts_mapped = points_mapped.groupby(['GEOID'])['geometry'].apply(list).reset_index()

print(tracts_mapped)


# Duration matrix
'''
with open("/home/lieu/dev/geographically_sensitive_dislocation/20_intermediate_files/duration_matrix_georgia_13.dmx") as f:
'''

'''
# doesn't work
import sample_rvps

if __name__ == "__main__":
    args = docopt(__doc__)
    print(args)
    STATE_CODE = args['STATE_CODE']
    DEM_RVPS = args['DEM_RVPS']
    REP_RVPS = args['REP_RVPS']
    SAVE_DM_TO = args['SAVE_DM_TO']
    SAMPLE_SIZE = 14000
    MATRIX_SIZE = 2000

    CDB = gpd.read_file(
        "/home/lieu/dev/geographically_sensitive_dislocation/00_source_data/\
10_US_Congressional_districts/nhgis0190_shapefile_tl2014_us_cd114th_2014/US_cd114th_2014_wgs84.shp")

    # after we get the points, downsample

    points_downsampled = sample_rvps.sample_rvps(CDB, STATE_CODE, DEM_RVPS,
                                                 REP_RVPS, SAMPLE_SIZE)

    # do a spatial join with the census tracts
'''
