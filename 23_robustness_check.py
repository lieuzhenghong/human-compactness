import json
import pandas as pd


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


s = [x * 100 for x in range(1, 101)]

files = [(f'./20_intermediate_data/16/2000/data{x}.json', x) for x in s]
files2 = [(f'./20_intermediate_data/16/4000/data{x}.json', x) for x in s]
# print(files)

print("Reading points...")
df = pd.concat([build_dataframe_from_list(read_results_from_file(f[0]), f[1] - 100)
                for f in files])

df2 = pd.concat([build_dataframe_from_list(read_results_from_file(f[0]), f[1] - 100)
                 for f in files2])
print(df)
print(df2)

# First question --- what's the average difference in means between 1000, and 2000 points?
# Answer: not much. Robustness check OK

df3 = abs(df2['hc'] - df['hc'])
print(df3)
print(df3.min())  # 1.3 e-06
print(df3.max())  # 0.04
print(df3.mean())  # 0.0046
print(df3.std())  # 0.005

grouped_df = (df.groupby('plan').sum().div(2)).reset_index()
print(grouped_df.index)
print(grouped_df.dtypes)
assert(grouped_df['hc'].dtype == 'float64')

max_hc = grouped_df['hc'].idxmax()
min_hc = grouped_df['hc'].idxmin()

print("Max HC according to idxmax:", grouped_df.iloc[max_hc]['hc'])
print("Actual max HC:", grouped_df['hc'].max())
print("Min HC according to idxmax:", grouped_df.iloc[min_hc]['hc'])
print("Actual min HC:", grouped_df['hc'].min())

assert(grouped_df['hc'].max() == grouped_df.iloc[max_hc]['hc'])  # fails
