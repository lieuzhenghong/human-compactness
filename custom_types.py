from typing import List, Dict, TypedDict, Any
from nptyping import NDArray

DistrictID = int
TractID = int
TractIDStr = str
GeoID = str
PointID = int
DurationDict = Dict[TractIDStr, Dict[TractIDStr, float]]
# A PointWiseMatrix is a matrix where M[i][j] denotes the distance from point i to point j.
PointWiseMatrix = NDArray[(Any, Any), float]
# A TractWiseMatrix is a matrix where M[i][j] denotes the sum of all distances from
# all points in tract i and all points in tract j
TractWiseMatrix = NDArray[(Any, Any), float]
# A PointWiseSumMatrix is a matrix where M[i][j] denotes the sum of all distances from
# point i to its jth nearest neighbours
PointWiseSumMatrix = NDArray[(Any, Any), float]


class TractEntry(TypedDict):
    geoid: GeoID
    pop: int
    pfs: List[float]  # Principal factors (for PCA)
    vrps: List[PointID]
