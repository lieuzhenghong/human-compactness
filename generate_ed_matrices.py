import config
import ed_human_compactness as edhc
from gerrychain import GeographicPartition, Graph
import _12_Process_Ensembles
import tract_generation
import os.path


def generate_ed_matrices(state_fips) -> None:
    """
    Generates and saves ed_matrices
    """
    tractwise_matrix_path = f"./20_intermediate_files/{state_fips}_{config.STATE_NAMES[state_fips]}_tractwise_matrix.npy"
    pointwise_sum_matrix_path = f"./20_intermediate_files/{state_fips}_{config.STATE_NAMES[state_fips]}_pointwise_sum_matrix.npy"

    if os.path.isfile(tractwise_matrix_path) and os.path.isfile(
        pointwise_sum_matrix_path
    ):
        print("Files already exist, returning...")
        return

    datadir = f"./Tract_Ensembles/2000/{state_fips}/"
    graph = Graph.from_json(datadir + "starting_plan.json")
    print("Graph created!")
    tract_dict = tract_generation.create_tract_dict(
        state_fips,
        config.STATE_NAMES[state_fips],
        config.NUM_DISTRICTS[state_fips],
        config.SAMPLE_RICHNESS,
    )
    _12_Process_Ensembles._update_graph_with_tract_dict_info_(
        graph,
        tract_dict,
    )
    print(f"Graph: {graph}")

    initial_partition = GeographicPartition(
        graph,
        assignment="New_Seed",
    )
    print(initial_partition)

    points_downsampled = tract_generation._read_and_process_vrp_shapefile(
        state_fips,
        config.STATE_NAMES[state_fips],
        config.NUM_DISTRICTS[state_fips],
        config.SAMPLE_RICHNESS,
    )

    ed_hc = edhc.EDHumanCompactness(graph, points_downsampled, tract_dict, None, None)

    tractwise_matrix_path = f"./20_intermediate_files/{state_fips}_{config.STATE_NAMES[state_fips]}_tractwise_matrix.npy"
    pointwise_sum_matrix_path = f"./20_intermediate_files/{state_fips}_{config.STATE_NAMES[state_fips]}_pointwise_sum_matrix.npy"
    if not os.path.isfile(tractwise_matrix_path):
        print("Generating and saving Euclidean distance tractwise matrix...")
        ed_hc.save_ed_tractwise_matrix(tract_dict, tractwise_matrix_path)

    if not os.path.isfile(pointwise_sum_matrix_path):
        print("Generating and saving Euclidean distance pointwise sum matrix...")
        ed_hc.save_ed_pointwise_sum_matrix(pointwise_sum_matrix_path)

    print("Generated and saved Euclidean distance matrices!")


if __name__ == "__main__":
    generate_ed_matrices("22")
    generate_ed_matrices("23")
    generate_ed_matrices("24")
    generate_ed_matrices("33")
    generate_ed_matrices("44")
    generate_ed_matrices("49")
    generate_ed_matrices("55")
