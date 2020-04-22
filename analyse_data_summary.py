from scipy.stats import ttest_ind
import pandas as pd
import numpy as np
from statsmodels.formula.api import ols

import matplotlib.pyplot as plt
import seaborn as sns
from plotnine import *

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

def _get_best_and_worst_plans_2(grouped_df, cutoff):
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

def _get_best_and_worst_plans(grouped_df):
    # cutoffs = [0.01]
    # cutoffs = [0.90]
    # cutoffs = [0.95]
    cutoffs = [0.95]
    # cutoffs = [0.90]
    # cutoffs = [0.75]
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


def _plot_point_plot(gdf):
    theme_set(theme_classic())
    reg_plot = (ggplot(gdf, aes(x='hc', y='sd')) +
                geom_point(aes(color='factor(state)')) +
                geom_smooth()
                )
    reg_plot.save('./30_results/grouped_regressions.png', height=20, width=20)

    reg_plot = (ggplot(gdf, aes(x='hc', y='sd', color='factor(state)')) +
                geom_point() +
                geom_smooth()
                )
    reg_plot.save('./30_results/individual_regressions.png',
                  height=20, width=20)


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
    grouped_df['state'] = district
    grouped_dfs.append(grouped_df)
    top_dfs.append(_get_best_and_worst_plans(grouped_df))
    lowest_sds.append(_get_lowest_sd_plans(grouped_df))
    dfs.append(dfa)



# First check if any particular compactness measure tracks spatial diversity
# better than the rest

'''
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
'''

# Look at the top DFs and find the difference in means

state_percentiles = []
for idx, top_df in enumerate(top_dfs):
    measures = ['hc', 'pp', 'reock', 'ch']
    print(idx, states[idx])
    des = (grouped_dfs[idx][['sd']])
    print(des.describe())
    state_percentiles.append([])
    from scipy import stats
    for i in range(4):
        print(measures[i])
        top_mean = top_df[i][['sd']].mean().values[0]
        diff_mean = (top_df[i][['sd']].mean() -
                     grouped_dfs[idx][['sd']].mean())

        state_percentiles[-1].append(stats.percentileofscore(des, top_mean))
        '''
        print(f'Difference in means: {diff_mean}')
        print(
            f"Difference in means between {measures[i]} and all: {diff_mean}")

        print(f"Total variance: {des.max() - des.min()}")
        print(
            f"Percentage of variance: {100* diff_mean / (des.max() - des.min()) }")
        '''

        values = [(diff_mean),
                  (des.max()-des.min()),
                  (100*diff_mean / (des.max()-des.min()))
                  ]
        # print(values)
        x = (ttest_ind(top_df[i][['sd']],
                       grouped_dfs[idx][['sd']], equal_var=False))
        # print(x)
        # print(top_df[i][['sd']].describe())

state_percentiles = pd.DataFrame(state_percentiles)
state_percentiles = state_percentiles.rename(
    columns={0: 'hc', 1: 'pp', 2: 'reock', 3: 'ch'},
)

print(state_percentiles.to_latex())
print(state_percentiles)
print(state_percentiles.mean())

# assert(False)

df = pd.concat(dfs)
gdf = pd.concat(grouped_dfs)
print(gdf)
gdf.to_csv('grouped_data.csv')

# assert(False)

# Find a Pearson's correlation to see how closely the metrics track one another

print(gdf[['sd', 'hc', 'pp', 'reock', 'ch']].corr())

# Run a regression between spatial diversity and compactness with country
# dummies

# fit = ols('sd ~ hc', data=grouped_df).fit()
for metric in ['hc', 'pp', 'reock', 'ch']:
    fit = ols(
        f'sd ~ {metric} + C(state) -1', data=gdf).fit()
    print(fit.summary().as_latex())

# Results: I find that only human compactness has a negative coefficient on
# spatial diversity.
#
# HC: -0.0404, t-value -40.632
# PP: +0.0251, t-value 29.841
# Reock: +0.0209, t-value 27.645
# CH: -0.0016, t-value -1.801


# Plot an overall correlation plot between spatial diversity and compactness
_plot_point_plot(gdf)

top_plans = []

for i in range(4):
    top_plans.append(pd.concat([d[i] for d in top_dfs]))

# Run the same OLS regression for the top 10% of plans on each metric

for idx, metric in enumerate(['hc', 'pp', 'reock', 'ch']):
    fit = ols(
        f'sd ~ {metric} + C(state) - 1', data=top_plans[idx]).fit()
    print(fit.summary())
    print(fit.summary().as_latex())

for cutoff in [0.10, 0.25, 0.5, 0.75, 0.9]:
    top_dfs = []
    for district in num_districts:
        states.append(state_names[district])
        dfa = pd.read_csv(f'{LOAD_PATH}/{district}_df.csv')
        grouped_df = (dfa.groupby('plan').sum())
        grouped_df = grouped_df.div(num_districts[district])
        grouped_df = grouped_df.reset_index()
        grouped_df['state'] = district
        top_dfs.append(_get_best_and_worst_plans_2(grouped_df, cutoff))
        grouped_dfs.append(grouped_df)
    top_plans = []
    for i in range(4):
        top_plans.append(pd.concat([d[i] for d in top_dfs]))
    for idx, top_plan in enumerate(top_plans):
        print(top_plan[['sd']].describe())
        top_plan.to_csv(f'top_plan_{cutoff}_{idx}.csv')

assert(False)

# These are top plans for HC, PP, CH, Reock
# print(top_plans)
# We should check if within these top plans, which has the best (lowest) spatial
# diversity mean




print(gdf[['sd']].describe())

# Plot KDE plot of spatial diversity of all grouped plots

fig, ax = plt.subplots(figsize=(10, 10))
g = sns.kdeplot(gdf.loc[:, 'sd'], shade=True, ax=ax)
fig.savefig(f'./30_results/kde_all_dfs')

# Testing that top plans have significantly lower SD than the mean



print(top_plans[0][['sd']].mean())  # human compactness
print(top_plans[1][['sd']].mean())  # human compactness
print(top_plans[2][['sd']].mean())  # human compactness
print(top_plans[3][['sd']].mean())  # human compactness
print(gdf[['sd']].mean())  # human compactness

print(ttest_ind(top_plans[0][['sd']], gdf[['sd']], equal_var=False))
print(ttest_ind(top_plans[1][['sd']], gdf[['sd']], equal_var=False))
print(ttest_ind(top_plans[2][['sd']], gdf[['sd']], equal_var=False))
print(ttest_ind(top_plans[3][['sd']], gdf[['sd']], equal_var=False))

# Little difference in spatial diversity means: all geometric measures 0.64,
# human compactness does a little better at 0.0635
# Is this difference statistically significant?
# Yes --- but the difference in magnitude is tiny.
# Mean is 0.64 with 0.08 std, but we only observe a tiny difference: 0.635 vs 0.64

# Checking that human compactness top plans have significantly lower SD than
# top plans according to other compactness metrics

print(
    f"Mean SD of top plans under Human Compactness: {top_plans[0][['sd']].mean()}")
print(
    f"Mean SD of top plans under Polsby-Popper: {top_plans[1][['sd']].mean()}")
print(f"Mean SD of top plans under Reock: {top_plans[2][['sd']].mean()}")
print(f"Mean SD of top plans under Convex Hull: {top_plans[3][['sd']].mean()}")

# Performing t-test of human-compactness against PP, Reock and CH

print(ttest_ind(top_plans[0][['sd']], top_plans[1][['sd']], equal_var=False))
print(ttest_ind(top_plans[0][['sd']], top_plans[2][['sd']], equal_var=False))
print(ttest_ind(top_plans[0][['sd']], top_plans[3][['sd']], equal_var=False))

# Performing t-test of PP against Reock and CH
print(ttest_ind(top_plans[1][['sd']], top_plans[2][['sd']], equal_var=False))
print(ttest_ind(top_plans[1][['sd']], top_plans[3][['sd']], equal_var=False))
