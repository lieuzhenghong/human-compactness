import json
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
import config
import os


if __name__ == "__main__":
    for STATE_FIPS in config.FIPS_LIST:
        all_hcs_ed = []
        all_hcs_dd = []
        all_polsby = []
        all_ch = []
        all_reock = []
        all_sds = []
        for i in range(100, 10100, 100):
            tentative_file = f"22_intermediate_files_new_run/{STATE_FIPS}/data{i}.json"
            with open(tentative_file, "r") as newfile:
                newjson = json.load(newfile)
                for index, newstep in enumerate(newjson):
                    all_hcs_ed.append(newstep["human_compactness_ed"])
                    all_hcs_dd.append(newstep["human_compactness_dd"])
                    all_polsby.append(newstep["polsby_compactness"])
                    all_ch.append(newstep["convex_hull_compactness"])
                    all_reock.append(newstep["reock_compactness"])
                    all_sds.append(newstep["spatial_diversity"][0])

        print(len(all_hcs_ed))
        print(len(all_hcs_dd))

        def _blob_score(d):
            return np.mean(list(d.values()))

        agg_ed = [_blob_score(e) for e in all_hcs_ed]
        agg_dd = [_blob_score(e) for e in all_hcs_dd]
        agg_pp = [_blob_score(e) for e in all_polsby]
        agg_ch = [_blob_score(e) for e in all_ch]
        agg_rk = [_blob_score(e) for e in all_reock]

        metrics = [
            ("ed", agg_ed),
            ("dd", agg_dd),
            ("polsby", agg_pp),
            ("ch", agg_ch),
            ("reock", agg_rk),
        ]

        correlations = [(e0, scipy.stats.pearsonr(e1, all_sds)) for e0, e1 in metrics]
        print(
            f"Correlations for {STATE_FIPS}, {config.STATE_NAMES[STATE_FIPS]}: {correlations}"
        )

    """
    plt.hist(agg_ed, bins=20, label="ed")
    plt.hist(agg_dd, bins=20, label="dd")
    plt.legend()
    plt.savefig("agg_total.png")
    plt.show()

    print(gdf[["sd", "hc", "pp", "reock", "ch"]].corr())
    """