
def calc_knn_sum_durations_by_tract(pttm, N, DM_PATH, SAVE_FILE_TO):
    '''Returns a dictionary and prints a file of
    {
        tractid: Float
    }
    where the value is the sum of k-nearest-neighbour driving durations for
    each point in the tract'''
    knn_sum_dd_by_tract = {}

    # First populate with tracts and initialise to 0

    for p in pttm:
        knn_sum_dd_by_tract[pttm[p]] = 0

    # I know I'm violating DRY here, but refactoring would take too much time
    with open(DM_PATH, 'rt') as fh:
        line = fh.readline()
        # This is currently looking at the durations from point i to all other points
        i = 0
        while line:
            # Get the distances from point i; two spaces is not a typo
            dist = [float(x) for x in line.split('  ')]

            # Very rarely, points may not lie within tracts. This is strange, but we'll ignore it
            if (i % 100 == 0):
                print(f'Now processing line {i}..')
            if i not in pttm:
                print(f'Point ID not in point_to_tract_mapping: {i}')
            else:
                # We want to get the nearest N neighbours, but at
                # the same time we want to make sure the tracts are in
                # the point-to-tract mapping.

                # So we sort, but maintain the index
                # enumerate gives a enumeration giving indexes and values
                # key=lambda i:i[1] sorts based on the original values

                sorted_dist = [i for i in sorted(
                    enumerate(dist), key=lambda a:a[1])]

                num_neighbours = 0
                j = 0

                while num_neighbours < N:
                    if j not in pttm:
                        print(f'Point ID not in point_to_tract_mapping: {j}')
                    else:
                        knn_sum_dd_by_tract[pttm[i]] += sorted_dist[j][1]
                        num_neighbours += 1
                    j += 1

                print(
                    f"Sum of KNN distances for point {i} in tract {pttm[i]}: {knn_sum_dd_by_tract[pttm[i]]}")
            i += 1
            line = fh.readline()

    with open(f'{SAVE_FILE_TO}', 'w') as f:
        f.write(json.dumps(knn_sum_dd_by_tract))

    return knn_sum_dd_by_tract
