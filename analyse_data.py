import pandas as pd
import numpy as np
import geopandas as gpd
import json
import matplotlib.pyplot as plt
import sys
import seaborn as sns


def read_results_from_file(FILE_PATH):
    '''
    read a json file
    Returns a dataframe
    '''
    with open(FILE_PATH) as f:
        file_dict = json.load(f)
    return file_dict


def build_dataframe_from_list(data_list, start_from):
    data_dict = {'plan': [], 'district': [], 'sd': [], 'hc': [], 'pp': []}

    for plan_id, step in enumerate(data_list):
        for (district_id, district) in enumerate(step['human_compactness']):
            data_dict['plan'].append(start_from + plan_id + 1)
            data_dict['district'].append(district_id + 1)
            data_dict['sd'].append(
                step['spatial_diversity'][1][str(district_id)])
            data_dict['hc'].append(step['human_compactness'][str(district_id)])
            data_dict['pp'].append(
                step['polsby_compactness'][str(district_id)])

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
        f'{SHAPEFILE_PATH}/Tract2000_{STATE_CODE}.shp')

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

    print(ctdf)
    s = ctdf['id'].astype(str).map(assignment_list[step_number])
    ctdf['district_assignment'] = s.fillna(
        ctdf['district_assignment']).astype(int)

    if axes is None:
        ctdf.plot(column='district_assignment', cmap='tab20')
    else:
        ctdf.plot(column='district_assignment', cmap='tab20', ax=ax)


if __name__ == "__main__":
    # read_results_from_file('./Tract_Ensembles/2000/13/rerun/data0.json')

    # data_list = read_results_from_file(
    #    './Tract_Ensembles/2000/13/rerun/data1000.json')

    STATE_CODE = sys.argv[1]
    NUM_DISTRICTS = int(sys.argv[2])

    PATH = f'./Tract_Ensembles/2000/{STATE_CODE}'
    files = [(f'{PATH}/rerun/data{i}.json', i)
             for i in range(1000, 10000, 1000)]

    print("Reading points...")
    # df = pd.concat([build_dataframe_from_list(read_results_from_file(f[0]), f[1] - 1000)
    #                for f in files])
    # print(df)
    df = pd.read_csv(f'./30_results/{STATE_CODE}_df.csv')

    # df.plot.scatter(x='pp', y='sd')
    # df.plot.scatter(x='hc', y='sd')
    # df.plot.scatter(x='hc', y='pp')

    print("Reading shapefile...")
    SHAPEFILE_PATH = f'./Data_2000/Shapefiles'
    ctdf = read_shapefile(STATE_CODE, SHAPEFILE_PATH)

    ctdf = build_initial_district_assignment(STATE_CODE, PATH, ctdf)
    # print(ctdf)
    # ctdf.plot(column='district_assignment', cmap='tab20')

    sns.set(color_codes=True)
    assignment_list = read_assignment_file(STATE_CODE, 10000, PATH)
    print("Expanding assignment list...")
    assignment_list = fill_district_assignments(assignment_list)

    '''
    print("Filling all areas for all districts...")
    fill_all_district_areas(assignment_list, ctdf, df)

    print(df)
    df.to_csv(f'./30_results/{STATE_CODE}_df.csv')
    '''

    # sns.lmplot(x="log_area", y="sd", data=df[df['log_area'].gt(21)])
    # sns.lmplot(x="log_area", y="hc", data=df)
    # df.plot.scatter(x="hc", y="sd", c='log_area', cmap='Reds')

    # ctdf.plot(column='district_assignment', cmap='tab20')

    grouped_df = (df.groupby('plan').sum())
    grouped_df = grouped_df.div(NUM_DISTRICTS)
    print(grouped_df)

    # grouped_df[['sd', 'hc', 'pp']].plot.kde()
    print(grouped_df[['sd', 'hc', 'pp']].corr())

    print(grouped_df[grouped_df['sd'] == grouped_df['sd'].max()])
    print(grouped_df[grouped_df['sd'] == grouped_df['sd'].min()])

    print(grouped_df[grouped_df['pp'] == grouped_df['pp'].max()])
    print(grouped_df[grouped_df['pp'] == grouped_df['pp'].min()])

    print(grouped_df[grouped_df['hc'] == grouped_df['hc'].max()])
    print(grouped_df[grouped_df['hc'] == grouped_df['hc'].min()])

    fig, axes = plt.subplots(nrows=3, ncols=2, sharex=True, sharey=True)
    max_hc = grouped_df['hc'].idxmax()
    min_hc = grouped_df['hc'].idxmin()
    max_pp = grouped_df['pp'].idxmax()
    min_pp = grouped_df['pp'].idxmin()
    max_sd = grouped_df['sd'].idxmax()
    min_sd = grouped_df['sd'].idxmin()

    plot_plan(max_hc, assignment_list, ctdf, ax=axes[0, 0])
    plot_plan(min_hc, assignment_list, ctdf, ax=axes[0, 1])
    plot_plan(max_pp, assignment_list, ctdf, ax=axes[1, 0])
    plot_plan(min_pp, assignment_list, ctdf, ax=axes[1, 1])
    plot_plan(max_sd, assignment_list, ctdf, ax=axes[2, 0])
    plot_plan(min_sd, assignment_list, ctdf, ax=axes[2, 1])

    # grouped_df.plot.scatter(x='hc', y='pp', c='sd', cmap='Oranges')
    # grouped_df.plot.scatter(x='hc', y='sd')  # weak negative correlation, -0.07
    # grouped_df.plot.scatter(x='pp', y='sd')  # weak negative correlation, -0.09

    # Now let's try and do some more sophisticated analysis

    grouped_df['hc_pp_delta'] = grouped_df['hc'] - grouped_df['pp']
    print(grouped_df[['hc_pp_delta', 'pp', 'hc', 'sd']].corr())

    #sns.lmplot(x="hc", y="sd", data=grouped_df)
    #sns.lmplot(x="hc_pp_delta", y="sd", data=grouped_df)

    plt.show()
