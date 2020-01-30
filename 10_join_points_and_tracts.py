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
from sum_driving_durations import sum_of_driving_durations_to_knn

# Import utilities for getting GEOIDs and ids of all Census Tracts
from spatial_diversity_utils import get_all_tract_geoids

# Import KD Tree to get nearest neighbours
from calculate_pd import create_kd_tree

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

DM_PATH = '/home/lieu/dev/geographically_sensitive_dislocation/20_intermediate_files/duration_matrix_georgia_13.dmx'

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

# We can't do this --- Python runs out of memory
# print("Reading duration matrix from file...")
# dm = read_duration_matrix_from_file(DM_PATH)
# Get the 1000 nearest voters
# print("Getting nearest-1000-voters...")
# points_mapped['knn_dd_sum'] = points_mapped.apply(sum_driving_durations_to_knn, args = (dm, 1000))
# print(points_mapped[['knn_dd_sum']])

'''
#pairwise[2000][2000] = {0};
pairwise = np.zeros((2000, 2000))
fh = open(file_name, 'rt')
line = fh.readline()
i = 0
while line:
    dist = [float(x) for x in line.split('  ')]
    for j in range(len(dist)):
    	pairwise[tract[i]][tract[j]] += dist[j]
    i+=1
    line = fh.readline()
'''

# Return a dictionary where key is GEOID (of tract) and values are the points
# in the GEOID

tracts_mapped = points_mapped.groupby(['GEOID'])['geometry'].apply(list)

print(tracts_mapped)

# Duration matrix


'''
# Let pairwise be a NxN array where pairwise[i][j] (including pairwise[i][i])
# is the sum of distances from all points in the tract i to the tract j

pairwise = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16],
        ]

# Let assignment be an assignment of census tract IDs to districts
assignment = {
        0: 3,
        1: 3,
        2: 0,
        3: 2,
    }

num_districts = 14

tracts_in_districts = [[] for x in range(num_districts)]
dd_sum = [0 for x in range(num_districts)]

# Loop through once to fill up the array
for tract_id in assignment:
    tracts_in_districts[assignment[tract_id]].append(tract_id)

print(tracts_in_districts)

for idx, district in enumerate(tracts_in_districts):
    # Calculates the sum of driving durations from each tract to all others in the district.
    # Starts with sum of distances from the last element to every other element in the district
    # Then pops off the last element
    while district != []:
        last_elem = district[-1]

        # TODO ask mark about converting this loop into C

        for tract in district:
            # distances may not be symmetric
            dd_sum[idx] += (pairwise[tract][last_elem] +
                    pairwise[last_elem][tract])

        # we've double-counted the last element with itself;
        dd_sum[idx] -= pairwise[last_elem][last_elem]
        
        # pop the last element; we're done with it
        district.pop()


print(tracts_in_districts)
print(dd_sum)
'''
