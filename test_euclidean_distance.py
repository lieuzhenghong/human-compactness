import euclidean_distance
import tract_generation
import _12_Process_Ensembles


def test_build_knn_sum_duration_matrix():
    state_fips = "09"
    state_name = _12_Process_Ensembles.state_names[state_fips]
    num_districts = _12_Process_Ensembles.num_districts[state_fips]
    sample_richness = _12_Process_Ensembles.sample_richness

    points_downsampled = tract_generation._read_and_process_vrp_shapefile(
        state_fips, state_name, num_districts, sample_richness
    )
    M = euclidean_distance._build_knn_sum_duration_matrix_(100, points_downsampled)
    print(M)
    assert M.shape == (num_districts * sample_richness, 100)
