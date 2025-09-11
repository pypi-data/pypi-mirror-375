import numpy as np
import matplotlib.pyplot as plt

def detect_pcr_bands(img_corrected, wells, max_width=100, min_row_spacing=115,
                     ax=None, return_results=False,
                     gradient_thresh=0.05, min_prominence=0.02, smoothing_sigma=1,
                     manual_yes=None, manual_no=None,
                     draw_trace_on_image=False, use_smoothed=True):
    if manual_no is None:
        manual_no = []
    if manual_yes is None:
        manual_yes = []

    from scipy.ndimage import gaussian_filter1d
    from scipy.signal import find_peaks

    if ax is None:
        fig, ax = plt.subplots(figsize=(15, 10))
        ax.imshow(img_corrected, cmap='gray')

    results = []

    for idx, (x, y) in enumerate(wells, start=1):
        x1 = int(x - max_width / 2)
        x2 = int(x + max_width / 2)
        y1 = int(y + 5)
        y2 = int(y + min_row_spacing)

        x1 = max(0, x1); x2 = min(img_corrected.shape[1], x2)
        y1 = max(0, y1); y2 = min(img_corrected.shape[0], y2)

        narrow_x1 = max(x1, int(x - 5))
        narrow_x2 = min(x2, int(x + 5))

        strip = img_corrected[y1:y2, narrow_x1:narrow_x2]
        vertical_profile = strip.mean(axis=1)

        smoothed = gaussian_filter1d(vertical_profile, sigma=smoothing_sigma)
        trace = smoothed if use_smoothed else vertical_profile

        grad = np.gradient(trace)
        peaks, _ = find_peaks(grad, height=gradient_thresh, prominence=min_prominence)
        has_band = len(peaks) > 0
        results.append(has_band)

        if manual_yes and idx in manual_yes:
            color = 'lime'
        elif manual_no and idx in manual_no:
            color = 'red'
        else:
            color = 'lime' if has_band else 'red'

        ax.add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1,
                                   edgecolor=color, facecolor='none', linewidth=1))
        if draw_trace_on_image:
            trace_norm = (trace - trace.min()) / (trace.max() - trace.min() + 1e-8)
            trace_scaled = x1 + trace_norm * (x2 - x1)
            y_range = np.arange(y1, y2)
            ax.plot(trace_scaled, y_range, color='blue', linewidth=1)
            for peak in peaks:
                peak_y = y1 + peak
                peak_x = trace_scaled[peak]
                ax.plot(peak_x, peak_y, 'ro', markersize=3)

    if return_results:
        return results
