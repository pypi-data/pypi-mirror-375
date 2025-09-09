import matplotlib
matplotlib.use("Agg")  # IMPORTANT: keep Matplotlib headless inside PyQt

import os
import json
import csv
import numpy as np
import matplotlib.pyplot as plt
from skimage import io, color

from .utils import (
    load_and_preprocess_image,
    threshold_image,
    clean_binary_image,
    extract_valid_centroids,
)
from .wells import (
    filter_rows_by_y_alignment,
    cluster_centroids_into_rows,
    estimate_row_locations,
    finalize_wells,
)
from .ladder import ladder_reader
from .bands import detect_pcr_bands



def _np_default(o):
    # Convert numpy scalars/arrays to native types
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (np.ndarray,)):
        return o.tolist()
    # Let json handle other types (or raise)
    raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")


def get_annotated_image(fig):
    fig.canvas.draw()
    import numpy as np
    # New API: buffer_rgba() → RGBA array
    buf = np.asarray(fig.canvas.buffer_rgba())  # (H, W, 4) uint8
    rgb = buf[..., :3].copy()
    return rgb


def run_detection_pipeline(
    image_path,
    *,
    comb_size=9,
    combs_per_row=2,
    detect_bars=True,
    manual_no=None,
    manual_yes=None,
    verbose=1,
    ladder=True,
    # tunables
    target_width=700,
    min_width=16,
    max_width=30,
    min_height=6,
    max_height=200,
    min_row_spacing=107,
    threshold_method="local",
    expected_samples_per_row=5,
    max_mean_intensity=0.6,
    row_thresh=20,
    gamma=1.0,
    # plot toggles
    draw_ladder_trace=False,
    draw_band_trace=False,
    user_probable_wells=None,
):
    if manual_no is None: manual_no = []
    if manual_yes is None: manual_yes = []

    # 1) Load & preprocess
    img = io.imread(image_path, as_gray=True)
    img_corrected = load_and_preprocess_image(img, gamma=gamma, target_width=target_width)

    # 2) Threshold & cleanup
    binary = threshold_image(img_corrected, method=threshold_method)
    cleaned = clean_binary_image(binary)

    # 3) Candidate centroids
    centroids = extract_valid_centroids(
        cleaned, img_corrected,
        min_width=min_width, max_width=max_width,
        min_height=min_height, max_height=max_height,
        max_mean_intensity=max_mean_intensity
    )

    # 4) Rows
    filtered1 = filter_rows_by_y_alignment(centroids, tolerance=5, min_per_row=expected_samples_per_row)
    sorted1 = cluster_centroids_into_rows(filtered1, row_thresh=row_thresh, min_row_spacing=min_row_spacing)
    sorted_centroids = filter_rows_by_y_alignment(sorted1, tolerance=5, min_per_row=expected_samples_per_row)
    unique_ys = estimate_row_locations(sorted_centroids, threshold=20, verbose=verbose)

    # 5) Wells (split ladder/sample)
    final_wells, ladder_wells, probable_wells = finalize_wells(
        sorted_centroids, unique_ys,
        comb_size=comb_size, combs_per_row=combs_per_row,
        row_tolerance=row_thresh, LADDER=ladder, VERBOSE=verbose,
        USER_PROBABLE=user_probable_wells
    )

    # 6) Plot overlays
    output_rgb = color.gray2rgb(img_corrected)
    fig, ax = plt.subplots(figsize=(15, 10))
    ax.imshow(output_rgb)
    for idx, (x, y) in enumerate(final_wells, start=1):
        if (x, y) not in probable_wells:
            ax.plot(x, y, 'ro'); ax.text(x, y - 5, str(idx), color='RED', fontsize=10)
        else:
            ax.plot(x, y, 'or'); ax.text(x, y - 5, str(idx), color='orange', fontsize=10)
    for (x, y) in ladder_wells:
        ax.plot(x, y, 'bo'); ax.text(x, y - 5, "L", color='blue', fontsize=8)

    # 7) Ladder & bands
    ladder_info = []
    if ladder and ladder_wells:
        ladder_info = ladder_reader(
            img_corrected, ladder_wells,
            max_width=max_width, min_row_spacing=min_row_spacing,
            ax=ax, gradient_thresh=0.003, min_prominence=0.02, smoothing_sigma=1,
            draw_trace_on_image=draw_ladder_trace, use_smoothed=False
        )

    band_calls = []
    if detect_bars:
        band_calls = detect_pcr_bands(
            img_corrected, final_wells,
            max_width=max_width, min_row_spacing=min_row_spacing,
            gradient_thresh=0.03, min_prominence=0.01, smoothing_sigma=1,
            ax=ax, manual_no=manual_no, manual_yes=manual_yes,
            draw_trace_on_image=draw_band_trace, use_smoothed=True,
            return_results=True
        )

    ax.set_title(f"Well Detection ({threshold_method})")
    ax.axis("off")
    plt.tight_layout()

    # Collect compact results
    result = {
        "final_wells": [{"index": i + 1, "x": float(x), "y": float(y)} for i, (x, y) in enumerate(final_wells)],
        "ladder_wells": [{"x": float(x), "y": float(y)} for (x, y) in ladder_wells],
        "probable_wells": [{"x": float(x), "y": float(y)} for (x, y) in probable_wells],
        "band_calls": list(map(bool, band_calls)) if band_calls else [],
        "ladder_info": ladder_info,
        "meta": {
            "threshold_method": threshold_method,
            "gamma": gamma,
            "target_width": target_width,
            "comb_size": comb_size,
            "combs_per_row": combs_per_row,
            "detect_bars": bool(detect_bars),
            "ladder": bool(ladder),
        }
    }
    return fig, result


def run_full_annotation(image_path, output_path=None, **kwargs):
    """Run pipeline, save annotated PNG, return (png_path, result)."""
    fig, result = run_detection_pipeline(image_path, **kwargs)

    if output_path is None:
        root, _ = os.path.splitext(image_path)
        output_path = root + "_annotated.png"

    fig.savefig(output_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return output_path, result


def save_results_csv(image_path, result, out_path=None):
    """CSV: well_index, x, y, is_ladder, probable, has_band, ladder_top, ladder_bottom, ladder_bands"""
    if out_path is None:
        root, _ = os.path.splitext(image_path)
        out_path = root + "_results.csv"

    # Map ladder wells (for quick lookup)
    ladder_set = {(round(d["x"], 3), round(d["y"], 3)) for d in result.get("ladder_wells", [])}
    probable_set = {(round(d["x"], 3), round(d["y"], 3)) for d in result.get("probable_wells", [])}

    # Ladder info keyed by nearest (x,y)
    ladder_info = result.get("ladder_info", [])
    ladder_lines = {}
    for d in ladder_info:
        key = (round(float(d["x"]), 3), round(float(d["y"]), 3))
        ladder_lines[key] = {
            "top": d.get("top"), "bottom": d.get("bottom"),
            "bands": d.get("bands", [])
        }

    band_calls = result.get("band_calls", [])
    wells = result.get("final_wells", [])

    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["well_index","x","y","is_ladder","probable","has_band","ladder_top","ladder_bottom","ladder_bands"])
        # sample wells
        for i, wll in enumerate(wells):
            key = (round(wll["x"], 3), round(wll["y"], 3))
            is_ladder = key in ladder_set
            probable = key in probable_set
            has_band = band_calls[i] if i < len(band_calls) else ""
            w.writerow([wll["index"], wll["x"], wll["y"], int(is_ladder), int(probable), int(bool(has_band)), "", "", ""])
        # ladder wells
        for lw in result.get("ladder_wells", []):
            key = (round(lw["x"], 3), round(lw["y"], 3))
            info = ladder_lines.get(key, {})
            bands_str = "|".join(map(str, info.get("bands", []))) if info else ""
            w.writerow(["", lw["x"], lw["y"], 1, 0, "", info.get("top",""), info.get("bottom",""), bands_str])

    return out_path


def save_results_json(image_path, result, out_path=None):
    if out_path is None:
        root, _ = os.path.splitext(image_path)
        out_path = root + "_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=_np_default)
    return out_path

import json

def load_results_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)