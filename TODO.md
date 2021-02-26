# TODO

Last updated 27th Feb 2021

- [??] Refactor `_12_Process_Ensembles.py`: clean up somehow...
    - [??] Refactor `init_data` to be able to initialise different TractWiseMatrix and PointWiseSumMatrix.
- [Lieu] Once I've refactored `_12_Process_Ensembles.py`, add in ED human compactness
- [Gabe] Figure out what is up with the `calculate_metrics` function:
  why is the loop so strange? It should be looping 10,000 times,
  why is the inner for loop looping 10,000 times?
- [Gabe] Double-check `generate_pointwise_sum_matrix` function inside `ed_human_compactness.py`:
    - inside `test_human_compactness.py`, run the function with 
      a small subset of `points_downsampled` and inspect the matrix visually
- [Lieu] Improve `_get_sum_ED_from_voter_to_knn_` inside `EDHumanCompactness`:
  we have a "Schlemiel the Painter's Algorithm" going on here where we 
    - keep querying the k-nearest points while increasing k 
      when we could simply query the k-nearest points once;
    - do a naive sum of the k-nearest points while increasing k (thus doing n^2 additions) 
      when we could simply add the next nearest point to the sum (thus doing O(K) additions)
 - [Lieu] Take a look at `tract_generation` and `spatial_diversity_utils`,
 and remove unneeded functions.
 - [Lieu] Write a technical summary of the code: what files are important,
 what files are not important
 - [Lieu] `human_compactness_utils.py` should now be deprecated: double-check
    and remove all references to it.