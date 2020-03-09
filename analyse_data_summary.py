from scipy.stats import ttest_ind
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

'''
We want to do two things here:

1. Does a particular compactness measure track spatial diversity better than
another? (Correlation over the entire sample)

2. Does a particular compactness measure have significantly lower scores than
another over a small sample (top 1000/500/200 plans)?

Also 3 if we have time/ability:

3.

'''


LOAD_PATH = './30_results'
num_districts = {"09": 5, "13": 13, "16": 2, "22": 7, "23": 2, "44": 2, "24":
                 8, "33": 2, "49": 3, "55": 8}
state_names = {"02": "Alaska", "01": "Alabama", "05": "Arkansas", "04": "Arizona",
               "06": "California", "08": "Colorado", "09": "Connecticut", "10": "Delaware",
               "12": "Florida", "13": "Georgia", "66": "Guam", "15": "Hawaii", "19": "Iowa",
               "16": "Idaho", "17": "Illinois", "18": "Indiana", "20": "Kansas", "21": "Kentucky",
               "22": "Louisiana", "25": "Massachusetts", "24": "Maryland", "23": "Maine", "26": "Michigan",
               "27": "Minnesota", "29": "Missouri", "28": "Mississippi", "30": "Montana",
               "37": "North_Carolina", "38": "North_Dakota", "31": "Nebraska", "33": "New_Hampshire",
               "34": "New_Jersey", "35": "New_Mexico", "32": "Nevada", "36": "New_York", "39": "Ohio",
               "40": "Oklahoma", "41": "Oregon", "42": "Pennsylvania", "72": "Puerto_Rico",
               "44": "Rhode_Island", "45": "South_Carolina", "46": "South_Dakota", "47": "Tenessee",
               "48": "Texas", "49": "Utah", "51": "Virginia", "50": "Vermont", "53": "Washington",
               "55": "Wisconsin", "54": "West_Virginia", "56": "Wyoming"}


def _get_best_and_worst_plans(grouped_df):
    # cutoffs = [0.01]
    # cutoffs = [0.90]
    cutoffs = [0.95]
    # cutoffs = [0.98]
    for cutoff in cutoffs:
        grouped_df.loc[grouped_df['hc'] >
                       grouped_df['hc'].quantile(cutoff), 'from'] = 'hc'
        top_hc_plans = grouped_df[grouped_df['hc']
                                  > grouped_df['hc'].quantile(cutoff)].copy()
        grouped_df.loc[grouped_df['pp'] >
                       grouped_df['pp'].quantile(cutoff), 'from'] = 'pp'
        top_pp_plans = grouped_df[grouped_df['pp']
                                  > grouped_df['pp'].quantile(cutoff)].copy()
        grouped_df.loc[grouped_df['ch'] >
                       grouped_df['ch'].quantile(cutoff), 'from'] = 'ch'
        top_ch_plans = grouped_df[grouped_df['ch']
                                  > grouped_df['ch'].quantile(cutoff)].copy()
        grouped_df.loc[grouped_df['reock'] >
                       grouped_df['reock'].quantile(cutoff), 'from'] = 'reock'
        top_reock_plans = grouped_df[grouped_df['reock']
                                     > grouped_df['reock'].quantile(cutoff)].copy()
        grouped_top_df = [top_hc_plans, top_pp_plans,
                          top_ch_plans, top_reock_plans]
    return grouped_top_df


def _get_lowest_sd_plans(grouped_df):
    cutoff = 0.05
    grouped_df.loc[grouped_df['sd'] <
                   grouped_df['sd'].quantile(cutoff), 'from'] = 'sd'
    return grouped_df[grouped_df['sd']
                      < grouped_df['sd'].quantile(cutoff)].copy()


dfs = []
grouped_dfs = []
top_dfs = []
lowest_sds = []

states = []

for district in num_districts:
    states.append(state_names[district])
    dfa = pd.read_csv(f'{LOAD_PATH}/{district}_df.csv')
    grouped_df = (dfa.groupby('plan').sum())
    grouped_df = grouped_df.div(num_districts[district])
    grouped_df = grouped_df.reset_index()
    grouped_dfs.append(grouped_df)
    top_dfs.append(_get_best_and_worst_plans(grouped_df))
    lowest_sds.append(_get_lowest_sd_plans(grouped_df))
    dfs.append(dfa)


# First check if any particular compactness measure tracks spatial diversity
# better than the rest

print("Plotting all district plans' SDs...")
fig, ax = plt.subplots(figsize=(10, 10))
for grouped_df in grouped_dfs:
    # print(grouped_df[['sd']].describe())
    print(grouped_df.loc[:, 'sd'])
    g = sns.kdeplot(grouped_df.loc[:, 'sd'], shade=True, ax=ax, legend=False)

ax.set(ylim=(0, 100))
ax.legend(states)
fig.savefig(f'all_plans_sd.png')

print("Plotting all individual district SDs...")
fig, ax = plt.subplots(figsize=(10, 10))
for df in dfs:
    # print(df[['sd']].describe())
    print(df.loc[:, 'sd'])
    g = sns.kdeplot(df.loc[:, 'sd'], shade=True, ax=ax, legend=False)
ax.set(xlim=(0.4, 1.2))
ax.legend(states)
fig.savefig(f'all_districts_sd.png')

df = pd.concat(dfs)
fig, ax = plt.subplots(figsize=(10, 10))
g = sns.kdeplot(df.loc[:, 'sd'], shade=True, ax=ax, legend=True)
ax.set(xlim=(0.4, 1.2))
fig.savefig(f'all_districts_concat_sd.png')

for idx, top_df in enumerate(top_dfs):
    measures = ['hc', 'pp', 'reock', 'ch']
    print(idx, states[idx])
    for i in range(4):
        print(measures[i])
        print(ttest_ind(top_df[i][['sd']], dfs[idx][['sd']]))
        # print(top_df[i][['sd']].describe())

# assert(False)

df = pd.concat(dfs)
gdf = pd.concat(grouped_dfs)
l_sd_df = pd.concat(lowest_sds)
print(df)
print(df[['sd', 'hc', 'pp', 'reock', 'ch']].corr())
print(gdf)
print(gdf[['sd', 'hc', 'pp', 'reock', 'ch']].corr())

# print(top_dfs[0])
top_plans = []

for i in range(4):
    top_plans.append(pd.concat([d[i] for d in top_dfs]))

# These are top plans for HC, PP, CH, Reock
# print(top_plans)
# We should check if within these top plans, which has the best (lowest) spatial
# diversity mean

for top_plan in top_plans:
    print(top_plan[['sd']].describe())

print(gdf[['sd']].describe())
print(l_sd_df[['sd']].describe())

# Testing that top plans have significantly lower SD than the mean

print(top_plans[0][['sd']].mean())  # human compactness
print(top_plans[1][['sd']].mean())  # human compactness
print(top_plans[2][['sd']].mean())  # human compactness
print(top_plans[3][['sd']].mean())  # human compactness
print(df[['sd']].mean())  # human compactness

print(ttest_ind(top_plans[0][['sd']], df[['sd']]))
print(ttest_ind(top_plans[1][['sd']], df[['sd']]))
print(ttest_ind(top_plans[2][['sd']], df[['sd']]))
print(ttest_ind(top_plans[3][['sd']], df[['sd']]))

# Little difference in spatial diversity means: all geometric measures 0.64,
# human compactness does a little better at 0.0635
# Is this difference statistically significant?
# Yes --- but the difference in magnitude is tiny.
# Mean is 0.64 with 0.08 std, but we only observe a tiny difference: 0.635 vs 0.64

# Checking that human compactness top plans have significantly lower SD than top plans according to other compactness metrics
print(top_plans[0][['sd']].mean())  # human compactness
print(top_plans[1][['sd']].mean())  # human compactness
print(top_plans[2][['sd']].mean())  # human compactness
print(top_plans[3][['sd']].mean())  # human compactness
print(ttest_ind(top_plans[0][['sd']], top_plans[1][['sd']]))
print(ttest_ind(top_plans[0][['sd']], top_plans[2][['sd']]))
print(ttest_ind(top_plans[0][['sd']], top_plans[3][['sd']]))

# Next check whether it's the case that human compactness does poorly on cities

# df['area_binned'] = pd.cut(df['log_area'], bins=[0, 21, 23, 99],
#                            labels=['small', 'medium', 'large'])

'''
# We have the cities.
df_c = df[df['log_area'] < 21].copy()
df_nc = df[df['log_area'] > 21].copy()

print(df_c[['sd', 'hc', 'pp', 'reock', 'ch']].corr())
print(df_nc)
print(df_nc[['sd', 'hc', 'pp', 'reock', 'ch']].corr())
'''
