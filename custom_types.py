from typing import List, Dict, TypedDict, Any, Optional, Tuple
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
    """
    A TractEntry gives information on a tract ID.
    This includes its GEOID,
    its population,
    its principal factors (for use in spatial diversity calculations),
    and the voter representative points (VRPs) that belong within it.
    """

    geoid: GeoID
    pop: int
    pfs: List[Optional[float]]  # Principal factors (for PCA)
    vrps: List[PointID]


TractDict = Dict[TractID, TractEntry]
GeoIDToIDMapping = Dict[GeoID, TractID]


class TractNotFoundError(Exception):
    pass