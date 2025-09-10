# src/esrf_data_compressor/checker/ssim.py

import os
import numpy as np
import h5py
from skimage.metrics import structural_similarity as ssim


def _select_win_size(H: int, W: int) -> int:
    """
    Choose an odd, valid window size for SSIM given slice dimensions H×W.
    win_size = min(H, W, 7), made odd, at least 3.
    """
    win = min(H, W, 7)
    if win % 2 == 0:
        win -= 1
    return max(win, 3)


def compute_ssim_for_dataset_pair(
    orig_path: str, comp_path: str, dataset_relpath: str
) -> tuple[float, float]:
    """
    Given two HDF5 files and the relative 3D dataset path (e.g., 'entry_0000/ESRF-ID11/marana/data'),
    compute SSIM on the first (z=0) and last (z=Z-1) slices.
    Returns (ssim_first, ssim_last). If a slice is constant, SSIM = 1.0.
    """
    with h5py.File(orig_path, "r") as fo, h5py.File(comp_path, "r") as fc:
        ds_o = fo[dataset_relpath]
        ds_c = fc[dataset_relpath]

        # Ensure both datasets are 3D
        if ds_o.ndim != 3 or ds_c.ndim != 3:
            raise IndexError(
                f"Dataset '{dataset_relpath}' is not 3D (orig: {ds_o.ndim}D, comp: {ds_c.ndim}D)"
            )

        first_o = ds_o[0].astype(np.float64)
        last_o = ds_o[-1].astype(np.float64)
        first_c = ds_c[0].astype(np.float64)
        last_c = ds_c[-1].astype(np.float64)

        H, W = first_o.shape
        win = _select_win_size(H, W)

        def _slice_ssim(a: np.ndarray, b: np.ndarray) -> float:
            amin, amax = a.min(), a.max()
            if amax == amin:
                return 1.0
            dr = amax - amin
            return ssim(a, b, data_range=dr, win_size=win)

        s0 = _slice_ssim(first_o, first_c)
        s1 = _slice_ssim(last_o, last_c)
        return s0, s1


def compute_ssim_for_file_pair(orig_path: str, comp_path: str) -> tuple[str, list[str]]:
    """
    Compute SSIM for every 3D dataset under `orig_path` vs. `comp_path`.
    Returns (basename, [report_lines…]), where each line is either:
    "<dataset_relpath>: SSIM_first=… SSIM_last=…" or an error message.
    """
    basename = os.path.basename(orig_path)
    report_lines: list[str] = []

    with h5py.File(orig_path, "r") as fo:
        ds_paths: list[str] = []

        def visitor(name, obj):
            if isinstance(obj, h5py.Dataset) and obj.ndim == 3:
                ds_paths.append(name)

        fo.visititems(visitor)

    if not ds_paths:
        report_lines.append(f"No 3D datasets found in {basename}")
        return basename, report_lines

    for ds in ds_paths:
        try:
            s0, s1 = compute_ssim_for_dataset_pair(orig_path, comp_path, ds)
            report_lines.append(f"{ds}: SSIM_first={s0:.4f}  SSIM_last={s1:.4f}")
        except Exception as e:
            report_lines.append(f"{ds}: ERROR computing SSIM: {e}")

    return basename, report_lines
