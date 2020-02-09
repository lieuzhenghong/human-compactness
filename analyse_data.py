import pandas as pd
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

    df2 = pd.DataFrame.from_dict(starting_dict, dtype='int')

    ctdf = census_tracts_df
    ctdf['GEOID'] = ctdf['GEOID'].astype('int')

    ctdf = ctdf.join(df2.set_index('GEOID'), on='GEOID')
    ctdf['id'].fillna(-1, inplace=True)
    ctdf['district_assignment'].fillna(-1, inplace=True)

    ctdf['id'] = ctdf['id'].astype('int').astype('str')
    ctdf['district_assignment'] = ctdf['district_assignment'].astype('int')

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
        print(type(assignment_list))
        print(len(assignment_list))
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


if __name__ == "__main__":
    # read_results_from_file('./Tract_Ensembles/2000/13/rerun/data0.json')

    # data_list = read_results_from_file(
    #    './Tract_Ensembles/2000/13/rerun/data1000.json')
    sns.set(color_codes=True)

    STATE_CODE = sys.argv[1]
    NUM_DISTRICTS = int(sys.argv[2])

    PATH = f'./Tract_Ensembles/2000/{STATE_CODE}'
    files = [(f'{PATH}/rerun/data{i}.json', i)
             for i in range(1000, 10000, 1000)]

    print("Reading points...")
    df = pd.concat([build_dataframe_from_list(read_results_from_file(f[0]), f[1] - 1000)
                    for f in files])
    print(df)

    print("Reading shapefile...")
    SHAPEFILE_PATH = f'./Data_2000/Shapefiles'
    ctdf = read_shapefile(STATE_CODE, SHAPEFILE_PATH)

    ctdf = build_initial_district_assignment(STATE_CODE, PATH, ctdf)

    print(ctdf)
    #ctdf.plot(column='district_assignment', cmap='tab20')

    assignment_list = read_assignment_file(STATE_CODE, 10000, PATH)
    assignment_list = fill_district_assignments(assignment_list)

    print(assignment_list[1])

    s = ctdf['id'].astype(str).map(assignment_list[1])

    ctdf['district_assignment'] = s.fillna(
        ctdf['district_assignment']).astype(int)

    print(ctdf)

    #ctdf.plot(column='district_assignment', cmap='tab20')

    grouped_df = (df.groupby('plan').sum())
    grouped_df = grouped_df.div(NUM_DISTRICTS)
    print(grouped_df)

    #grouped_df[['sd', 'hc', 'pp']].plot.kde()
    print(grouped_df[['sd', 'hc', 'pp']].corr())

    print(grouped_df[grouped_df['sd'] == grouped_df['sd'].max()])
    print(grouped_df[grouped_df['sd'] == grouped_df['sd'].min()])

    print(grouped_df[grouped_df['pp'] == grouped_df['pp'].max()])
    print(grouped_df[grouped_df['pp'] == grouped_df['pp'].min()])

    print(grouped_df[grouped_df['hc'] == grouped_df['hc'].max()])
    print(grouped_df[grouped_df['hc'] == grouped_df['hc'].min()])

    max_hc = grouped_df['hc'].idxmax()
    print(max_hc)

    s = ctdf['id'].astype(str).map(assignment_list[max_hc])
    ctdf['district_assignment'] = s.fillna(
        ctdf['district_assignment']).astype(int)

    ctdf.plot(column='district_assignment', cmap='tab20')

    s = ctdf['id'].astype(str).map(assignment_list[8306])

    ctdf['district_assignment'] = s.fillna(
        ctdf['district_assignment']).astype(int)
    ctdf.plot(column='district_assignment', cmap='tab20')

    grouped_df.plot.scatter(x='hc', y='pp', c='sd', cmap='Oranges')
    grouped_df.plot.scatter(x='hc', y='sd')  # weak negative correlation, -0.07
    grouped_df.plot.scatter(x='pp', y='sd')  # weak negative correlation, -0.09

    # Now let's try and do some more sophisticated analysis

    grouped_df['hc_pp_delta'] = grouped_df['hc'] - grouped_df['pp']
    print(grouped_df[['hc_pp_delta', 'pp', 'hc', 'sd']].corr())
    grouped_df.plot.scatter(x='hc_pp_delta', y='sd')

    sns.lmplot(x="hc_pp_delta", y="sd", data=grouped_df)

    plt.show()
