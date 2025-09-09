import numpy as np
from collections import defaultdict

def filter_rows_by_y_alignment(centroids, tolerance=5, min_per_row=5):
    row_map = defaultdict(list)
    for x, y in centroids:
        y_rounded = int(round(y / tolerance) * tolerance)
        row_map[y_rounded].append((x, y))
    filtered_centroids = []
    for _, points in row_map.items():
        if len(points) >= min_per_row:
            filtered_centroids.extend(points)
    return filtered_centroids

def cluster_centroids_into_rows(centroids, row_thresh=30, min_row_spacing=15):
    centroids = sorted(centroids, key=lambda c: (c[1], c[0]))
    clustered, current = [], []
    last_row_y = None
    for c in centroids:
        if not current:
            current = [c]; last_row_y = c[1]
        elif abs(c[1] - last_row_y) < row_thresh:
            current.append(c)
        elif abs(c[1] - last_row_y) >= min_row_spacing:
            clustered.append(sorted(current, key=lambda x: x[0]))
            current = [c]; last_row_y = c[1]
    if current:
        clustered.append(sorted(current, key=lambda x: x[0]))
    return [c for row in clustered for c in row]

def estimate_missing(row, col_data, y_ref, row_tolerance=10):
    expected_xs = [np.mean(xs) for xs in col_data.values()]
    new_row = row.copy()
    probable_wells = []
    existing_xs = [x for x, _ in row]
    for expected_x in expected_xs:
        found = any(abs(x - expected_x) < row_tolerance for x in existing_xs)
        if not found:
            probable_wells.append((expected_x, y_ref))
            new_row.append((expected_x, y_ref))
    new_row = sorted(new_row, key=lambda p: p[0])
    return new_row, probable_wells

def finalize_wells(
    centroids,
    row_locations,
    comb_size=9,
    combs_per_row=2,
    row_tolerance=10,
    LADDER=True,
    VERBOSE=1,
    USER_PROBABLE=None,          # <--- NEW
):
    """
    USER_PROBABLE: optional list of (x, y) floats supplied by the GUI.
    These points are merged into the rows before 'missing' estimation.
    """
    final_centroids = []
    ladder_centroids = []
    probable_centroids = []

    if USER_PROBABLE:
        # normalize to float tuples
        USER_PROBABLE = [(float(x), float(y)) for (x, y) in USER_PROBABLE]
        probable_centroids.extend(USER_PROBABLE)

    col_data = dict()
    # build column means (same as before)
    for y_ref in row_locations:
        row = [pt for pt in centroids if abs(pt[1] - y_ref) <= row_tolerance]
        row = sorted(row, key=lambda x: x[0])
        if len(row) >= comb_size * combs_per_row:
            for i in range(len(row)):
                col_data.setdefault(i, []).append(row[i][0])

    for y_ref in row_locations:
        row = [pt for pt in centroids if abs(pt[1] - y_ref) <= row_tolerance]
        row = sorted(row, key=lambda x: x[0])

        # --- inject user probable points for this row (if any) ---
        if USER_PROBABLE:
            inject = [(x, y) for (x, y) in USER_PROBABLE if abs(y - y_ref) <= row_tolerance]
            # avoid duplicates (same x within tolerance)
            existing_xs = [x for x, _ in row]
            for (ux, uy) in inject:
                if not any(abs(ux - ex) < row_tolerance for ex in existing_xs):
                    row.append((ux, uy))
            row = sorted(row, key=lambda p: p[0])

        # Estimate and add remaining missing points as before
        missing = comb_size * combs_per_row - len(row)
        if missing > 0 and len(row) > 1:
            new_row, new_probable = estimate_missing(row, col_data, y_ref, row_tolerance=row_tolerance)
            row = new_row
            probable_centroids.extend(new_probable)

        # Extract ladder comb positions (unchanged)
        try:
            for x in reversed(range(1, (combs_per_row * comb_size) + 1, comb_size)):
                if LADDER:
                    ladder_centroids.append(row.pop(x - 1))
        except IndexError:
            print("Warning: IndexError for a row, will not process for this row")

        final_centroids.extend(row)

    if VERBOSE:
        print(f"\nFinalized Well Centroids: {len(final_centroids)} Total count")
        print(f"\nLadder Well Centroids:{len(ladder_centroids)} Total count")

    return final_centroids, ladder_centroids, probable_centroids

def estimate_row_locations(sorted_centroids, threshold=20, verbose=1):
    row_ys = [y for _, y in sorted_centroids]
    unique_ys = []
    for y in sorted(row_ys):
        if not unique_ys or abs(y - unique_ys[-1]) > threshold:
            unique_ys.append(y)
    if verbose:
        print("\nEstimated Y coordinates of valid rows:")
        print(unique_ys)
    return unique_ys
