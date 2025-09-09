import numpy as np
from skimage import exposure, filters, morphology, measure, transform

def load_and_preprocess_image(img, *, gamma=1.0, target_width=700):
    # Resize
    scale = target_width / img.shape[1]
    new_height = int(img.shape[0] * scale)
    img_resized = transform.resize(img, (new_height, target_width), preserve_range=True, anti_aliasing=True)

    # Mild contrast enhance
    p2, p98 = np.percentile(img_resized, (2, 98))
    img_contrast = exposure.rescale_intensity(img_resized, in_range=(p2, p98))

    # Gamma correction
    img_corrected = exposure.adjust_gamma(img_contrast, gamma=gamma)

    # Inverse vignette
    rows, cols = img_corrected.shape
    Y, X = np.ogrid[:rows, :cols]
    center_y, center_x = rows / 2, cols / 2
    radius = np.sqrt((X - center_x) ** 2 + (Y - center_y) ** 2)
    max_radius = np.sqrt(center_x ** 2 + center_y ** 2)
    vignette = 1 + 0.4 * (1 - (radius / max_radius))
    vignette = np.clip(vignette, 1, 1.4)

    return np.clip(img_corrected / vignette, 0, 1)

def threshold_image(img_corrected, method="local"):
    if method == "local":
        block_size = 51
        offset = 0.01
        thr = filters.threshold_local(img_corrected, block_size=block_size, offset=offset)
        binary = img_corrected < thr
    elif method == "multiotsu":
        thr_vals = filters.threshold_multiotsu(img_corrected, classes=3)
        binary = img_corrected < thr_vals[0]
    elif method == "sauvola":
        thr = filters.threshold_sauvola(img_corrected, window_size=51)
        binary = img_corrected < thr
    elif method == "niblack":
        thr = filters.threshold_niblack(img_corrected, window_size=51)
        binary = img_corrected < thr
    else:
        raise ValueError("Unknown thresholding method")
    return binary

def clean_binary_image(binary):
    binary = morphology.binary_opening(binary, morphology.disk(1))
    cleaned = morphology.remove_small_objects(binary, min_size=5)
    cleaned = morphology.remove_small_holes(cleaned, area_threshold=5)
    return cleaned

def extract_valid_centroids(cleaned, img_corrected,
                            *, min_width=16, max_width=30, min_height=6, max_height=200,
                            max_mean_intensity=0.6):
    label_image = measure.label(cleaned)
    props = measure.regionprops(label_image, intensity_image=img_corrected)
    centroids = []
    for prop in props:
        minr, minc, maxr, maxc = prop.bbox
        h = maxr - minr
        w = maxc - minc
        if (min_width <= w <= max_width and
            min_height <= h <= max_height and
            prop.mean_intensity < max_mean_intensity):
            centroids.append(prop.centroid[::-1])  # (x, y)
    return centroids
