import pandas as pd
import numpy as np
import geopandas as gpd
import json
import matplotlib.pyplot as plt
import sys
import seaborn as sns
from plotnine import *


# sys.path.append('/home/lieu/dev/geographically_sensitive_dislocation/10_code')
sys.path.append('../geographically_sensitive_dislocation/10_code')

import sample_rvps  # noqa: E402


def read_results_from_file(FILE_PATH):
    '''
    read a json file
    Returns a dataframe
    '''
    with open(FILE_PATH) as f:
        file_dict = json.load(f)
    return file_dict


def build_dataframe_from_list(data_list, start_from):
    data_dict = {'plan': [], 'district': [],
                 'sd': [], 'hc': [], 'pp': [], 'reock': [], 'ch': []}

    for plan_id, step in enumerate(data_list):
        for (district_id, district) in enumerate(step['human_compactness']):
            data_dict['plan'].append(start_from + plan_id + 1)
            data_dict['district'].append(district_id + 1)
            data_dict['sd'].append(
                step['spatial_diversity'][1][str(district_id)])
            data_dict['hc'].append(step['human_compactness'][str(district_id)])
            data_dict['pp'].append(
                step['polsby_compactness'][str(district_id)])

            if 'reock_compactness' in step:
                data_dict['reock'].append(
                    step['reock_compactness'][str(district_id)])
            else:
                data_dict['reock'].append(None)

            if 'convex_hull_compactness' in step:
                data_dict['ch'].append(
                    step['convex_hull_compactness'][str(district_id)])
            else:
                data_dict['ch'].append(None)

    df = pd.DataFrame.from_dict(data_dict)
    # print(df)
    return(df)


def build_initial_district_assignment(state_code, path, census_tracts_df):
    '''Takes in a raw census tract DF and returns the join of
    census tracts to district assignments. makes it plottable
    '''
    starting_json = read_starting_assignment(state_code, path)

    # Convert starting_json to a dataframe with the columns
    # ['GEOID', 'id', 'New_Seed']

    starting_dict = {'GEOID': [], 'id': [], 'district_assignment': []}

    for key in starting_json['nodes']:  # starting_json['nodes'] is a list
        starting_dict['GEOID'].append(key['GEOID'])
        starting_dict['id'].append(key['id'])
        starting_dict['district_assignment'].append(key['New_Seed'])

    assert(len(starting_dict['GEOID']) == len(starting_dict['id']))

    assert(len(starting_dict['id']) == len(
        starting_dict['district_assignment']))

    print(min(starting_dict['district_assignment']),
          max(starting_dict['district_assignment']))

    df2 = pd.DataFrame.from_dict(starting_dict, dtype='int')

    ctdf = census_tracts_df
    ctdf['GEOID'] = ctdf['GEOID'].astype('int')

    ctdf = ctdf.join(df2.set_index('GEOID'), on='GEOID')
    ctdf['id'].fillna(-999, inplace=True)
    ctdf['district_assignment'].fillna(-1, inplace=True)

    ctdf['id'] = ctdf['id'].astype('int').astype('str')
    ctdf['district_assignment'] = ctdf['district_assignment'].astype('int')

    print('Min district num: ', ctdf['district_assignment'].min())
    print('Max district num: ', ctdf['district_assignment'].max())

    return ctdf


def plot_district_assignment(census_tracts_df, assignment):
    df = census_tracts_df
    df['current'] = df.index.map(dict(assignment))
    df.plot(column='current', camp='tab20')


def read_starting_assignment(state_code, path):
    with open(f'{path}/starting_plan.json') as f:
        return json.load(f)


def read_shapefile(state_code, path):
    '''Returns a GeoDataFrame'''
    ctdf = gpd.read_file(
        f'{path}/Tract2000_{state_code}.shp')

    return(ctdf)


def read_assignment_file(state_code, plan_number, path):
    step_number = plan_number % 10000
    file_number = int(plan_number // 10000) * 10000
    file_name = f"{path}/flips_{file_number}.json"
    with open(file_name) as f:
        assignment_list = json.load(f)
        return assignment_list


def fill_district_assignments(assignment_list):
    import copy
    all_assignments = []

    all_assignments.append(assignment_list[0])

    for step in assignment_list[1:]:
        all_assignments.append(copy.deepcopy(all_assignments[-1]))
        for ass in step:
            all_assignments[-1][ass] = step[ass]

    assert(all_assignments[1] != all_assignments[8704])

    return all_assignments


def fill_all_district_areas(assignment_list, ctdf, df):
    for idx, step in enumerate(assignment_list):
        if (idx % 100 == 0):
            print(idx)
        s = ctdf['id'].astype(str).map(step)
        ctdf['district_assignment'] = s.fillna(
            ctdf['district_assignment']).astype(int)

        # print(ctdf['district_assignment'].min())
        # print(ctdf['district_assignment'].max())
        # do a groupby district_assignment and sum total area
        # discard index that is -999
        grouped = ctdf.groupby(['district_assignment'])['SHAPE_AREA'].sum()

        for district_id, area in grouped.items():
            if (district_id == -1):
                pass
            else:
                # remember 1-indexing
                df.loc[(df['plan'].eq(idx+1) &
                        df['district'].eq(district_id+1)), 'area'] = area
                df.loc[(df['plan'].eq(idx+1) &
                        df['district'].eq(district_id+1)), 'log_area'] = np.log(area)


def plot_district(step_number, district_number, ctdf):
    s = ctdf['id'].astype(str).map(assignment_list[step_number])
    ctdf['district_assignment'] = s.fillna(
        ctdf['district_assignment']).astype(int)

    # district_number is 1-indexed but district_assignment is 0-indexed
    ctdf['is_district'] = ctdf['district_assignment'] == district_number - 1

    ctdf.plot(column='is_district', cmap='Reds')


def plot_plan(step_number, assignment_list, ctdf, ax=None):
    s = ctdf['id'].astype(str).map(assignment_list[step_number])
    ctdf['district_assignment'] = s.fillna(
        ctdf['district_assignment']).astype(int)

    if ax is None:
        ctdf.plot(column='district_assignment', cmap='tab20')
    else:
        ctdf.plot(column='district_assignment', cmap='tab20', ax=ax)


def plot_vrps_on_census_tracts(census_tracts, STATE_CODE):
    # First convert to epsg 2163
    GEOG_WD = "../geographically_sensitive_dislocation/00_source_data/"

    print("Reading district shapefile...")
    CDB = gpd.read_file(GEOG_WD +
                        "10_US_Congressional_districts/nhgis0190_shapefile_tl2014_us_cd114th_2014/US_cd114th_2014_wgs84.shp")

    DEM_RVPS = f'{GEOG_WD}00_representative_voter_points/points_D_{STATE_CODE}_2_10000_run1.shp'
    REP_RVPS = f'{GEOG_WD}00_representative_voter_points/points_R_{STATE_CODE}_2_10000_run1.shp'
    SAMPLE_SIZE = 1000 * int(NUM_DISTRICTS)
    # after we get the points, downsample

    print("Downsampling points...")
    vrps = sample_rvps.sample_rvps(CDB, STATE_CODE, DEM_RVPS,
                                   REP_RVPS, SAMPLE_SIZE)

    census_tracts = census_tracts.to_crs({'init': 'epsg:2163'})

    vrps = vrps.to_crs({'init': 'epsg:2163'})

    ax0 = census_tracts.plot(
        column='district_assignment', alpha=0.6, cmap='tab20')
    # Plot the points on the tracts
    vrps.plot(ax=ax0, color="grey")
    fig = plt.gcf()
    fig.set_size_inches(20, 30)
    fig.savefig(f'{SAVE_PATH}/{STATE_CODE}_points_on_tracts.png', dpi=100)


def build_and_save_df_to_csv(STATE_CODE, NUM_DISTRICTS, SHAPEFILE_PATH, SAVE_PATH):
    '''
    Returns df, ctdf and assignment_list.

    df:                 DataFrame of districts
    ctdf:               DataFrame of Census Tracts
    assignment_list:    List of district assignments (dictionary mapping districts to IDs)

    '''

    PATH = f'./Tract_Ensembles/2000/{STATE_CODE}'
    # files = [(f'{PATH}/rerun/data{i}.json', i)
    #         for i in range(1000, 10000, 1000)]

    s = [x * 100 for x in range(1, 101)]

    files = [
        (f'./20_intermediate_files/{STATE_CODE}/data{x}.json', x) for x in s]

    print("Reading points...")
    df = pd.concat([build_dataframe_from_list(read_results_from_file(f[0]), f[1] - 100)
                    for f in files])

    print(df)

    print("Reading shapefile...")
    ctdf = read_shapefile(STATE_CODE, SHAPEFILE_PATH)
    ctdf = build_initial_district_assignment(STATE_CODE, PATH, ctdf)

    print("Reading assignment list...")
    assignment_list = read_assignment_file(STATE_CODE, 10000, PATH)
    print("Expanding assignment list...")
    assignment_list = fill_district_assignments(assignment_list)

    try:
        print(f"Trying to read CSV file for {STATE_CODE}_df.csv...")
        df = pd.read_csv(f'{LOAD_PATH}/{STATE_CODE}_df.csv')
    except:
        print(
            f"Could not find {LOAD_PATH}/{STATE_CODE}_df.csv, generating one now...")
        print("Filling all areas for all districts...")
        fill_all_district_areas(assignment_list, ctdf, df)
        print(f"Saving to {STATE_CODE}_df.csv...")
        df.to_csv(f'{SAVE_PATH}/{STATE_CODE}_df.csv')

    return df, ctdf, assignment_list


def _plot_corr_matrix(df):
    sns.set_style("white")
    corr = df[['sd', 'hc', 'pp', 'reock', 'ch']].corr()
    corr.to_csv(f'{SAVE_PATH}/{STATE_CODE}_corr.csv')

    df['area_binned'] = pd.cut(df['log_area'], bins=[0, 21, 23, 99],
                               labels=['small', 'medium', 'large'])
    print(df)

    g = sns.pairplot(df[['sd', 'hc', 'pp', 'reock', 'ch', 'area_binned']],
                     hue='area_binned', palette='Set2')
    g.savefig(f'{SAVE_PATH}/{STATE_CODE}_pairwise_plot.png')

    # Set up the matplotlib figure
    fig, ax = plt.subplots(figsize=(10, 10))
    sns.heatmap(corr, cmap="Reds", linewidths=.5,
                square=True, annot=True, ax=ax)
    fig.savefig(f'{SAVE_PATH}/{STATE_CODE}_corr_matrix.png')


def _plot_corr_matrix_grouped(df):
    sns.set_style("white")

    corr = df[['sd', 'hc', 'pp', 'reock', 'ch']].corr()

    corr.to_csv(f'{SAVE_PATH}/{STATE_CODE}_corr_grouped.csv')

    g = sns.pairplot(df[['sd', 'hc', 'pp', 'reock', 'ch']],
                     palette='Set2')
    g.savefig(f'{SAVE_PATH}/{STATE_CODE}_pairwise_plot_grouped.png')

    # Set up the matplotlib figure
    fig, ax = plt.subplots(figsize=(10, 10))
    sns.heatmap(corr, cmap="Reds", linewidths=.5,
                square=True, annot=True, ax=ax)
    fig.savefig(f'{SAVE_PATH}/{STATE_CODE}_corr_matrix_grouped.png')


def _plot_top_plans(grouped_df):
    '''Gets the top plans by quantile and then does a difference-in-mean-test'''

    theme_set(theme_classic())

    cutoffs = [0.9, 0.95, 0.98]

    for cutoff in cutoffs:
        grouped_df.loc[grouped_df['hc'] >
                       grouped_df['hc'].quantile(cutoff), 'from'] = 'hc'
        top_hc_plans = grouped_df[grouped_df['hc']
                                  > grouped_df['hc'].quantile(cutoff)].copy()
        grouped_df.loc[grouped_df['pp'] >
                       grouped_df['pp'].quantile(.9), 'from'] = 'pp'
        top_pp_plans = grouped_df[grouped_df['pp']
                                  > grouped_df['pp'].quantile(cutoff)].copy()
        grouped_df.loc[grouped_df['ch'] >
                       grouped_df['ch'].quantile(.9), 'from'] = 'ch'
        top_ch_plans = grouped_df[grouped_df['ch']
                                  > grouped_df['ch'].quantile(cutoff)].copy()
        grouped_df.loc[grouped_df['reock'] >
                       grouped_df['reock'].quantile(.9), 'from'] = 'reock'
        top_reock_plans = grouped_df[grouped_df['reock']
                                     > grouped_df['reock'].quantile(cutoff)].copy()
        grouped_top_df = pd.concat(
            [top_hc_plans, top_pp_plans, top_ch_plans, top_reock_plans])
        print(grouped_top_df)
        # Get these top plans and make them a geom_boxplot()
        # First reshape the data

        dd = grouped_df.copy()
        dd.loc[:, 'from'] = 'all'
        grouped_top_df_with_mean = pd.concat([grouped_top_df, dd])

        means_boxplot = (ggplot(grouped_top_df, aes(x='from', y='sd', fill='from')) +
                         geom_boxplot() +
                         geom_hline(
                             aes(yintercept=grouped_df[['sd']].mean(), linetype=['mean']))
                         )
        means_boxplot.save(
            f"{SAVE_PATH}/{STATE_CODE}_means_boxplot_{cutoff}.png")

        means_violin = (ggplot(grouped_top_df, aes(x='from', y='sd', fill='from')) +
                        geom_violin(draw_quantiles=0.5) +
                        geom_hline(
                            aes(yintercept=grouped_df[['sd']].mean(), linetype=['mean']))
                        )
        means_violin.save(
            f"{SAVE_PATH}/{STATE_CODE}_means_violin {cutoff}.png")

        means_boxplot = (ggplot(grouped_top_df_with_mean, aes(x='from', y='sd', fill='from')) +
                         geom_violin(draw_quantiles=0.5) +
                         geom_hline(
                             aes(yintercept=grouped_df[['sd']].mean(), linetype=['mean']))
                         )
        means_boxplot.save(
            f"{SAVE_PATH}/{STATE_CODE}_means_violin_with_mean_{cutoff}.png")

        # Plot some correlations in the same figure?
        hc_corrplot = (ggplot(top_hc_plans, aes(x='hc', y='sd')) +
                       geom_point(color='cornflowerblue', alpha=0.5, size=0.5)
                       )
        hc_corrplot.save(
            f"{SAVE_PATH}/{STATE_CODE}_top_hc_sd_corrplot {cutoff}.png")

        ch_corrplot = (ggplot(top_ch_plans, aes(x='ch', y='sd')) +
                       geom_point(color='cornflowerblue', alpha=0.5, size=0.5))
        ch_corrplot.save(
            f"{SAVE_PATH}/{STATE_CODE}_top_ch_sd_corrplot {cutoff}.png")


def _plot_best_and_worst_plans(assignment_list, grouped_df, ctdf):
    # Plot max and min HC
    fig, axes = plt.subplots(nrows=3, ncols=2, sharex=True, sharey=True)
    fig.set_size_inches(20, 30)

    cols = ["'Good' plans", "'Bad' plans"]
    rows = ["Human compactness", "Polsby-Popper", "Spatial Diversity"]

    for ax, col in zip(axes[0], cols):
        ax.set_title(col)

    for ax, row in zip(axes[:, 0], rows):
        ax.set_ylabel(row)

    max_hc = grouped_df['hc'].idxmax()
    min_hc = grouped_df['hc'].idxmin()
    max_pp = grouped_df['pp'].idxmax()
    min_pp = grouped_df['pp'].idxmin()
    max_sd = grouped_df['sd'].idxmax()
    min_sd = grouped_df['sd'].idxmin()

    assert(grouped_df.iloc[max_hc]['hc'] == grouped_df['hc'].max())

    plot_plan(max_hc, assignment_list, ctdf, ax=axes[0, 0])
    plot_plan(min_hc, assignment_list, ctdf, ax=axes[0, 1])
    plot_plan(max_pp, assignment_list, ctdf, ax=axes[1, 0])
    plot_plan(min_pp, assignment_list, ctdf, ax=axes[1, 1])
    # Swap the position of min and max SD
    plot_plan(min_sd, assignment_list, ctdf, ax=axes[2, 0])
    plot_plan(max_sd, assignment_list, ctdf, ax=axes[2, 1])

    fig.tight_layout()
    fig.savefig(f'{SAVE_PATH}/{STATE_CODE}_min_max_subplots.png', dpi=100)


def _squarerootify(df):
    df[['sd', 'hc', 'pp', 'reock', 'ch']] = df[[
        'sd', 'hc', 'pp', 'reock', 'ch']]**0.5
    return df


if __name__ == "__main__":

    LOAD_PATH = './30_results'
    SAVE_PATHS = ['./30_results', './31_results_rc']

    # TODO make num_districts a separate file

    num_districts = {"09": 5, "13": 13, "16": 2, "22": 7,
                     "23": 2, "44": 2,
                     "24": 8, "33": 2, "49": 3, "55": 8}
    # num_districts = {'23':2, '44':2}
    # num_districts = {'09': 5}

    SHAPEFILE_PATH = f'./Data_2000/Shapefiles'

    sns.set(style="white", color_codes=True)

    for STATE_CODE in num_districts:
        NUM_DISTRICTS = num_districts[STATE_CODE]
        print(STATE_CODE, NUM_DISTRICTS)
        df, ctdf, assignment_list = build_and_save_df_to_csv(
            STATE_CODE, NUM_DISTRICTS, SHAPEFILE_PATH, './30_results')
        for SAVE_PATH in SAVE_PATHS:
            if (SAVE_PATH == './31_results_rc'):
                df = _squarerootify(df)

            plot_vrps_on_census_tracts(ctdf, STATE_CODE)

            # Plot hc and sd by area
            df.plot.scatter(x="hc", y="sd", c='log_area', cmap='Reds')
            fig = plt.gcf()
            fig.set_size_inches(30, 20)
            fig.savefig(
                f'{SAVE_PATH}/{STATE_CODE}_hc_sd_log_area.png', dpi=100)

            grouped_df = (df.groupby('plan').sum())
            grouped_df = grouped_df.div(NUM_DISTRICTS)
            grouped_df = grouped_df.reset_index()

            # grouped_df[['sd', 'hc', 'pp']].plot.kde()
            # print(grouped_df[['sd', 'hc', 'pp']].corr())

            _plot_corr_matrix(df)
            _plot_corr_matrix_grouped(grouped_df)
            _plot_top_plans(grouped_df)
            _plot_best_and_worst_plans(assignment_list, grouped_df, ctdf)

            # Largely obsolete, don't really need this anymore
            grouped_df['hc_pp_delta'] = grouped_df['hc'] - grouped_df['pp']
            print(grouped_df[['hc_pp_delta', 'pp',
                              'hc', 'sd', 'reock', 'ch']].corr())

            sns.set_style("white")
            plt.figure(figsize=(15, 15))
            sns_plot = sns.lmplot(x="hc", y="sd", data=grouped_df)
            sns_plot.savefig(f'{SAVE_PATH}/{STATE_CODE}_hc_sd_scatter.png')

            sns_plot = sns.lmplot(x="pp", y="sd", data=grouped_df)
            sns_plot.savefig(f'{SAVE_PATH}/{STATE_CODE}_pp_sd_scatter.png')

            sns_plot = sns.lmplot(x="hc", y="pp", data=grouped_df)
            sns_plot.savefig(f'{SAVE_PATH}/{STATE_CODE}_hc_pp_scatter.png')

            sns_plot = sns.lmplot(x="hc_pp_delta", y="sd", data=grouped_df)
            sns_plot.savefig(f'{SAVE_PATH}/{STATE_CODE}_delta_sdscatter.png')

            plt.close("all")
