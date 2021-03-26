import json
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
import config
import os


def _dicts_are_approx_equal_(d1, d2) -> bool:
    a1 = np.array(list(d1.items()), dtype=float)
    a2 = np.array(list(d2.items()), dtype=float)
    return np.allclose(a1, a2)


def verify_correctness():
    for STATE_FIPS in config.FIPS_LIST:
        # Verify the correctness of old and new files
        for i in range(100, 10100, 100):
            verify_correctness_step(STATE_FIPS, i)


def verify_correctness_step(STATE_FIPS, i):
    old_file = f"20_intermediate_files/{STATE_FIPS}/data{i}.json"
    tentative_file = f"22_intermediate_files_new_run/{STATE_FIPS}/data{i}.json"
    with open(old_file, "r") as oldfile, open(tentative_file, "r") as newfile:
        print(f"Comparing {old_file} with {tentative_file}...")
        oldjson = json.load(oldfile)
        newjson = json.load(newfile)
        for index, oldstep in enumerate(oldjson):
            newstep = newjson[index]
            """
            print(
                index,
                "\n",
                oldstep["human_compactness"],
                "\n",
                newstep["human_compactness_dd"],
            )
            """
            assert _dicts_are_approx_equal_(
                oldstep["human_compactness"],
                newstep["human_compactness_dd"],
            )


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
        corred = scipy.stats.pearsonr(agg_ed, all_sds)
        corrdd = scipy.stats.pearsonr(agg_dd, all_sds)
        corrpp = scipy.stats.pearsonr(agg_pp, all_sds)
        corrch = scipy.stats.pearsonr(agg_ch, all_sds)
        corrrk = scipy.stats.pearsonr(agg_rk, all_sds)
        print(corred)
        print(corrdd)
        print(corrpp)
        print(corrch)
        print(corrrk)
    plt.hist(agg_ed, bins=20, label="ed"    )
    plt.hist(agg_dd, bins=20, label="dd")
    plt.legend()
    plt.savefig("agg_total.png")
    plt.show()

    print(gdf[["sd", "hc", "pp", "reock", "ch"]].corr())
    """