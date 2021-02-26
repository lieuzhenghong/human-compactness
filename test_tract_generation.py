import tract_generation
import config
from tract_generation_test_data import *


def test_generate_tracts_with_vrps():
    state_code = "09"
    data = tract_generation.generate_tracts_with_vrps(
        state_code=state_code,
        state_name=(config.STATE_NAMES[state_code]).lower(),
        num_districts=config.NUM_DISTRICTS[state_code],
        sample_richness=1000,
    )

    assert data == generate_tracts_with_vrps_test_data_09


def test_create_tract_dict():
    """
    Regression testing to refactor generate_tract_with_vrps function
    """
    state_code = "09"
    data = tract_generation.create_tract_dict(
        state_code=state_code,
        state_name=(config.STATE_NAMES[state_code]).lower(),
        num_districts=config.NUM_DISTRICTS[state_code],
        sample_richness=1000,
    )

    assert data == generate_tracts_with_vrps_test_data_09
