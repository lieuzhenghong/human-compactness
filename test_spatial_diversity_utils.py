import spatial_diversity_utils as sd_utils
import config
from spatial_diversity_test_data import *


def test_get_all_tract_geoids():
    state_code = "09"
    tract_dict, geoid_to_id_mapping = sd_utils.get_all_tract_geoids(state_code)
    assert geoid_to_id_mapping == geoid_to_id_test_mapping_09
    assert tract_dict == tract_dict_test_data_09


def test_fill_tract_dict_with_spatial_diversity_info():
    state_code = "09"
    tract_dict, geoid_to_id_mapping = sd_utils.get_all_tract_geoids(state_code)

    tract_dict = sd_utils.fill_tract_dict_with_spatial_diversity_info(
        tract_dict=tract_dict,
        geoid_to_id_mapping=geoid_to_id_mapping,
        tract_spatial_diversity_scores=config.TRACT_SPATIAL_DIVERSITY_SCORES,
    )

    assert tract_dict_spatial_diversity_test_data_09 == tract_dict
