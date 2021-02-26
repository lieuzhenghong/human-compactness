## Introduction

First, some background.
The main data structure is a Gerrychain `Partition`.
A `Partition` of a state has a _graph_ and 
an _assignment_ of graph nodes to Congressional districts.

We run 10,000 steps for each partition.
At each step we mutate the partition _assignment_:
that is, changing the assignment of graph nodes to districts.
We then calculate several _metrics_ of that new assignment.
In particular, we are interested in _compactness metrics_.
These metrics include
Polsby-Popper, Reock, Convex Hull, and human compactness 
(both euclidean distance and driving durations).
We also calculate a quantity of interest called
_spatial diversity_ for each assignment.

The codebase here implements spatial diversity and compactness metrics,
and also includes driver code to initialise the partition,
load in the partition assignments,
mutate the partition assignment,
and calculate the metrics for each of the assignments.
The main driver file is `_12_Process_Ensembles.py` 
which should be the entry point of the code.
`main_old` first initialises some required data 
(`init_data`, `init_metrics`, various other functions).
It then calls `calculate_metrics`,
which calculates the various metrics for 10,000 steps
using `calculate_metrics_step`.
`calculate_metrics` also saves its progress in `.json` files.

These are the rest of the files in alphabetical order,
along with a short description of each:

- `config.py`: stores global variables
- `custom_types.py`: custom type definitions
- `dd_human_compactness.py`: implements a class `DDHumanCompactness`
  that inherits from `HumanCompactness`.
  Has methods for e.g. precomputing various required data structures
  and calculating driving-distance human compactness.
- `ed_human_compactness.py`: implements euclidean-distance human compactness.
- `generate_ed_matrices.py`: Precomputes and saves `TractWiseMatrix` 
   and `PointWiseSumMatrix` for use in `EDHumanCompactness`.
- `human_compactness_utils.py`: **DEPRECATED**. Implements human compactness.
- `human_compactness.py`: implements the `HumanCompactness` abstract base class.
- `reock.py`: calculates Reock and Convex Hull compactness metrics.
- `smallest_enclosing_circle`: dependency for `reock.py`.
- `spatial_diversity_test_data.py`: test data for testing spatial diversity functions.
- `spatial_diversity_utils.py`: functions to read/load and 
   add spatial diversity data to the Graph
- `tract_generation_test_data.py`: test data
- `tract_generation.py`: functions to generate `TractDict`

## Some questions I have

- Should I put the `TractDict` data into the `Graph` 
and just call `graph.nodes[tract_id].property` instead?
Then I wouldn't have to pass `TractDict` around.
I actually do this already, but am inconsistent:
I use the graph data directly for spatial diversity
(see lines 142 and 143 for `spatial_diversity_utils`),
but I pass in `TractDict` to the human compactness functions. 
What are the pros and cons of each approach?
- In the same vein, I don't store the precomputed `TractWiseMatrix`
and `PointWiseSumMatrix` inside the various `HumanCompactness` instances,
which again means I have to pass them around in the various class methods.
Should I or shouldn't I?
- (I know this is very vague) I don't like the way that `_12_Process_Ensembles`
is set up. I will have to rewrite it to include the euclidean human compactness metric.
How would you improve it? How would you test it? I have a test file already.
- In general, would welcome comments on how to structure the codebase,
 how to improve in general. 

## Miscellany

- To get a list of all tracts: do `partition.graph.nodes`
- To get an assignment of tracts to districts: do 
`dict(partition.assignment)`
- To get an assignment of tracts to points: you're looking for a TractDict