import numpy as np
import h5py
import pytest

from esrf_data_compressor.checker.ssim import compute_ssim_for_dataset_pair

# Fix the RNG seed for reproducibility
RNG = np.random.default_rng(12345)


def create_h5_pair(
    tmp_path, data_orig: np.ndarray, data_comp: np.ndarray, dataset_path: str
):
    """
    Helper: create two HDF5 files under tmp_path with the same internal group hierarchy,
    and a single dataset at `dataset_path` containing data_orig and data_comp respectively.
    """
    orig_path = tmp_path / "orig.h5"
    comp_path = tmp_path / "comp.h5"

    # Create orig.h5
    with h5py.File(orig_path, "w") as f:
        grp = f
        # Ensure nested groups exist
        for part in dataset_path.split("/")[:-1]:
            grp = grp.create_group(part)
        grp.create_dataset(dataset_path.split("/")[-1], data=data_orig)

    # Create comp.h5
    with h5py.File(comp_path, "w") as f:
        grp = f
        for part in dataset_path.split("/")[:-1]:
            grp = grp.create_group(part)
        grp.create_dataset(dataset_path.split("/")[-1], data=data_comp)

    return str(orig_path), str(comp_path)


def test_identical_volume(tmp_path):
    """
    If orig and comp volumes are identical, SSIM should be exactly 1.0 for both slices.
    """
    data = RNG.integers(0, 256, size=(3, 4, 4), dtype=np.uint16)
    orig, comp = create_h5_pair(
        tmp_path, data, data.copy(), "entry_0000/ESRF-ID11/marana/data"
    )

    s0, s1 = compute_ssim_for_dataset_pair(
        orig, comp, "entry_0000/ESRF-ID11/marana/data"
    )
    assert pytest.approx(1.0, rel=1e-9) == s0
    assert pytest.approx(1.0, rel=1e-9) == s1


def test_small_noise_volume(tmp_path):
    """
    Introduce small uniform noise (±1) across all slices. SSIM should remain high (> 0.90).
    """
    data_orig = RNG.integers(0, 256, size=(3, 4, 4), dtype=np.uint16)
    noise = RNG.integers(-1, 2, size=data_orig.shape, dtype=np.int16)
    data_noisy = np.clip(data_orig.astype(np.int16) + noise, 0, 65535).astype(np.uint16)

    orig, comp = create_h5_pair(
        tmp_path, data_orig, data_noisy, "entry_0000/ESRF-ID11/marana/data"
    )

    s0, s1 = compute_ssim_for_dataset_pair(
        orig, comp, "entry_0000/ESRF-ID11/marana/data"
    )
    assert 0.90 < s0 <= 1.0
    assert 0.90 < s1 <= 1.0


def test_nonexistent_dataset(tmp_path):
    """
    If the dataset path does not exist, we expect a KeyError.
    """
    data = RNG.integers(0, 256, size=(3, 4, 4), dtype=np.uint16)
    orig, comp = create_h5_pair(
        tmp_path, data, data.copy(), "entry_0000/ESRF-ID11/marana/data"
    )

    with pytest.raises(KeyError):
        compute_ssim_for_dataset_pair(
            orig, comp, "entry_0000/ESRF-ID11/marana/nonexistent"
        )


def test_wrong_dimension_dataset(tmp_path):
    """
    If the named dataset exists but is not 3D, an indexing error should be raised.
    """
    data2d = np.ones((4, 4), dtype=np.uint16)
    orig_path = tmp_path / "orig2d.h5"
    comp_path = tmp_path / "comp2d.h5"
    with h5py.File(orig_path, "w") as f:
        grp = f.create_group("entry_0000/ESRF-ID11/marana")
        grp.create_dataset("data2d", data=data2d)
    with h5py.File(comp_path, "w") as f:
        grp = f.create_group("entry_0000/ESRF-ID11/marana")
        grp.create_dataset("data2d", data=data2d)

    with pytest.raises(IndexError):
        compute_ssim_for_dataset_pair(
            str(orig_path), str(comp_path), "entry_0000/ESRF-ID11/marana/data2d"
        )
