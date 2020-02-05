import pandas as pd
import json
import matplotlib.pyplot as plt


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


if __name__ == "__main__":
    # read_results_from_file('./Tract_Ensembles/2000/13/rerun/data0.json')

    # data_list = read_results_from_file(
    #    './Tract_Ensembles/2000/13/rerun/data1000.json')

    path = './Tract_Ensembles/2000/13/rerun/data'
    files = [(f'{path}{i}.json', i) for i in range(1000, 10000, 1000)]

    df = pd.concat([build_dataframe_from_list(read_results_from_file(f[0]), f[1] - 1000)
                    for f in files])
    print(df)

    grouped_df = (df.groupby('plan').sum())
    grouped_df = grouped_df.div(13)
    print(grouped_df)

    grouped_df[['sd', 'hc', 'pp']].plot.kde()
    print(grouped_df[['sd', 'hc', 'pp']].corr())

    grouped_df.plot.scatter(x='hc', y='pp')  # pretty strong correlation, 0.38
    grouped_df.plot.scatter(x='hc', y='sd')  # weak negative correlation, -0.07
    grouped_df.plot.scatter(x='pp', y='sd')  # weak negative correlation, -0.09

    ''' Analysis of individual-level tract data
    #print(df.min(), df.max(), df.mean(), df.median(), df.std())
    #print(df.mean(), df.std())
    df[['sd', 'hc', 'pp']].plot.kde()
    print(df[['sd', 'hc', 'pp']].corr())

    #df.plot.scatter(x='hc', y='sd')
    #df.plot.scatter(x='pp', y='sd')

    # This plot looks interesting. There are some plans whereby HC is
    # very high, but PP is very low. This is strange.
    #df.plot.scatter(x='hc', y='pp')

    # Let's do a filter on those plans where pp < 0.05 and hc > 0.9
    #filtered_df = df[(df['hc'] >= 0.9) & (df['pp'] <= 0.05)]

    filtered_df = df[((df['hc'] <= 0.7) | (df['pp'] >= 0.06))]
    # We find that spatial diversity is lower (0.64 vs 0.68 --- significant?)
    # in this region, compared to the mean. The standard deviation of the
    # spatial diversity is also lower

    filtered_df.plot.scatter(x='hc', y='pp')

    filtered_df.plot.scatter(x='hc', y='sd')
    filtered_df.plot.scatter(x='pp', y='sd')

    #print(filtered_df[['sd', 'hc', 'pp']].corr())

    print(filtered_df)
    #print(filtered_df.mean(), filtered_df.std())
    '''

    plt.show()
