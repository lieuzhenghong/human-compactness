import geopandas as gpd

#TODO make it not only read the state of Georgia

CENSUS_TRACTS = gpd.read_file("/home/lieu/dev/human_compactness/TRACT_DATA/Shapefiles/TRACT/TRACT_13.shp")

print(CENSUS_TRACTS[:10])

print(list(CENSUS_TRACTS))

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
