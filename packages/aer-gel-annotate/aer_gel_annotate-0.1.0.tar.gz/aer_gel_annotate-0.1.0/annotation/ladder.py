import numpy as np
import matplotlib.pyplot as plt

def ladder_reader(img_corrected, ladder_wells, max_width=100, min_row_spacing=115,
                  ax=None, gradient_thresh=0.05, min_prominence=0.02, smoothing_sigma=1,
                  draw_trace_on_image=False, use_smoothed=True):
    from scipy.ndimage import gaussian_filter1d
    from scipy.signal import find_peaks

    ladder_bands = []

    for idx, (x, y) in enumerate(ladder_wells, start=1):
        x1 = int(x - max_width / 2)
        x2 = int(x + max_width / 2)
        y1 = int(y + 5)
        y2 = int(y + min_row_spacing)
        x1, x2 = max(0, x1), min(img_corrected.shape[1], x2)
        y1, y2 = max(0, y1), min(img_corrected.shape[0], y2)

        strip = img_corrected[y1:y2, int(x - max_width / 2):int(x + max_width / 2)]
        vertical_profile = strip.mean(axis=1)
        smoothed = gaussian_filter1d(vertical_profile, sigma=smoothing_sigma)
        trace = smoothed if use_smoothed else vertical_profile

        grad = np.gradient(smoothed)
        peaks, _ = find_peaks(grad, height=gradient_thresh, prominence=min_prominence)
        band_positions = [y1 + peak for peak in peaks]

        ladder_bands.append({
            'x': x,
            'y': y,
            'top': band_positions[0] if band_positions else None,
            'bottom': band_positions[-1] if band_positions else None,
            'bands': band_positions
        })

        if ax is not None:
            ax.add_patch(plt.Rectangle((x1, y1), x2 - x1, y2 - y1,
                                       edgecolor='blue', facecolor='none', linewidth=1))
            for band in band_positions:
                ax.plot([x1, x2], [band, band], color='yellow', linewidth=1)

            if draw_trace_on_image:
                trace_norm = (trace - trace.min()) / (trace.max() - trace.min() + 1e-8)
                trace_scaled = x1 + trace_norm * (x2 - x1)
                y_range = np.arange(y1, y2)
                ax.plot(trace_scaled, y_range, color='blue', linewidth=1)
                for peak in peaks:
                    peak_y = y1 + peak
                    peak_x = trace_scaled[peak]
                    ax.plot(peak_x, peak_y, 'ro', markersize=3)

    return ladder_bands
