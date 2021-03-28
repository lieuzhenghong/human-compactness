import config
import json
import numpy as np


def _dicts_are_approx_equal_(d1, d2) -> bool:
    a1 = np.array(list(d1.items()), dtype=float)
    a2 = np.array(list(d2.items()), dtype=float)
    return np.allclose(a1, a2)


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


def verify_correctness():
    for STATE_FIPS in config.FIPS_LIST:
        # Verify the correctness of old and new files
        for i in range(100, 10100, 100):
            verify_correctness_step(STATE_FIPS, i)


if __name__ == "__main__":
    verify_correctness()
    print(
        f"Newly-calculated DD HCs identical to previously calculated DD HCs for states: {config.FIPS_LIST}"
    )
