import pandas as pd
import numpy as np
import config
import json
from typing import List
from statsmodels.formula.api import ols

"""
What do we want to do here?
Let's try a clean room implementation. 
We want to check the SDs of the top plans of each metric.

First thing to do: 
- Read all the plans in and just aggregate them up.
- Filter them by the top scores.
- Find the relationship between the top compact plans and spatial diversity:
    (for each individual cutoff)
    - Do highly compact plans have higher or lower spatial diversity?
    - Do highly homogenous (low SD) plans also score well on compactness?

Second step:
- Let's try and find plans where the delta between ED and DD HC is large negative and large positive.
- Is there a bias? We should hope for cases where by DD > ED and SD is small,
  or ED > DD and SD is large.
"""


def form_dataframe_from_results(metrics: List[str], STATE_FIPS: str):
    """
    Reads in the data in 22_intermediate_files_new_run and forms a dataframe
    """
    results = {metric: [] for metric in metrics}
    results["spatial_diversity"] = []
    print(results)

    for i in range(100, 10100, 100):
        tentative_file = f"22_intermediate_files_new_run/{STATE_FIPS}/data{i}.json"
        with open(tentative_file, "r") as newfile:
            newjson = json.load(newfile)
            for index, newstep in enumerate(newjson):
                for metric in metrics:
                    results[metric].append(np.mean(list(newstep[metric].values())))
                results["spatial_diversity"].append(newstep["spatial_diversity"][0])

    df = pd.DataFrame.from_dict(results, orient="index").transpose()
    return df


def get_top_plans_under_metric(df, metric: str, cutoff: float):
    print(f"Now looking at the top {cutoff} plans under {metric}")
    return df.loc[df[metric] > df[metric].quantile(cutoff)]


if __name__ == "__main__":
    metrics = [
        "human_compactness_ed",
        "human_compactness_dd",
        "polsby_compactness",
        "convex_hull_compactness",
        "reock_compactness",
    ]

    for STATE_FIPS in config.FIPS_LIST:
        print(STATE_FIPS, config.STATE_NAMES[STATE_FIPS])
        df = form_dataframe_from_results(metrics, STATE_FIPS)

        # Part 1: check the top plans under each compactness measure,
        # and see if spatial diversity is significantly lower
        # cutoffs = [0.1, 0.25, 0.5, 0.75, 0.9]
        cutoffs = [0.90]
        for cutoff in cutoffs:
            for metric in metrics:
                # Here we're checking in
                filtered = get_top_plans_under_metric(df, metric, cutoff)
                print(len(filtered))
                print(f"SD: {round(np.mean(filtered['spatial_diversity']), 4)}")

                # TODO do a significance test here to check if
                # the differences are statistically significant

                # We should do one with dummy variable state
                # fit = ols(f"sd ~ {metric} + C(state) -1", data=filtered).fit()
                # fit = ols(f"spatial_diversity ~ {metric}", data=filtered).fit()
                # print(fit.summary())
                # print(fit.summary().as_latex())

        # We should next check if the
