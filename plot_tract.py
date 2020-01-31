# import plotting utilities
import geopandas as gpd
import geoplot as gplt
import matplotlib.pyplot as plt

# Plot vrps on census tracts.
#
# Takes in two shapefiles, census_tracts and points, and plots an overlay of
# VRPS. Saves it in 

def plot_vrps_on_census_tracts(census_tracts, vrps, filename):
    # First convert to epsg 2163
    census_tracts = census_tracts.to_crs({'init': 'epsg:2163'})
    vrps = vrps.to_crs({'init': 'epsg:2163'})

    ax0 = census_tracts.plot(color='white', edgecolor='black')
    vrps.plot(ax=ax0)
    fig = plt.gcf()
    fig.set_size_inches(30, 20)
    fig.savefig(f'{filename}.png', dpi=100)

