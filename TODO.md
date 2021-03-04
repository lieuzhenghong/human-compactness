# TODO

Last updated 27th Feb 2021

- [??] Refactor `_12_Process_Ensembles.py`: clean up somehow...
    - [??] Refactor `init_data` to be able to initialise different TractWiseMatrix and PointWiseSumMatrix.
- [Lieu] Once I've refactored `_12_Process_Ensembles.py`, add in ED human compactness
- [Gabe] Figure out what is up with the `calculate_metrics` function:
    - why is the loop so strange? It should be looping 10,000 times
    - why is the inner for loop looping 10,000 times?
    - A: `Tract_Ensembles/2000/09/` has only one json: `flips_10000.json`. In it is a list of 10k deltas to the assignment vector. Since `max_steps = step_size` our `ts` list has just one element (10,000) so the outer for loop just runs once. Then, for each delta in our `flips_10000.json` we run `calculate_metrics_step()` on that delta. It looks like other states (FIPS 08) have `flips_20000.json` up to 100k, where we would set `max_steps = 100000` and then this function would run 10x as long and `ts` would be nontrivial.
- [Gabe] Double-check `generate_pointwise_sum_matrix` function inside `ed_human_compactness.py`:
    - inside `test_human_compactness.py`, run the function with 
      a small subset of `points_downsampled` and inspect the matrix visually
    - A: Yes, the matrix was originally being created with columns `[0, 2, 3, ..., K]`. This is because `kd_tree.query()` fails with `k = 1`. I don't think this matters once the ddf is converted to a `numpy` array, but I changed it to make the first column of ddf indexed at 1, which conceptually aligns with the fact that a VRP is its own nearest neighbor (k=1). I also added a test in `test_human_compactness` to check that the returned `dmx` has `K` columns.
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
