# src/esrf_data_compressor/tests/test_jp2k_improved.py
import numpy as np
import h5py
import pytest

from esrf_data_compressor.compressors.jp2k import JP2KCompressor
from esrf_data_compressor.checker.ssim import compute_ssim_for_dataset_pair


def create_constant_3d_h5(path: str, shape=(3, 16, 16), value=1000):
    """Create an HDF5 file with dataset '/entry_0000/ESRF-ID11/marana/data'."""
    with h5py.File(path, "w") as f:
        grp = f.require_group("entry_0000/ESRF-ID11/marana")
        data = np.full(shape, value, dtype=np.uint16)
        grp.create_dataset("data", data=data)


def fake_identity_compress(self, raw_path, comp_path, cratio):
    """Copy raw HDF5 to comp HDF5 without changes."""
    with h5py.File(raw_path, "r") as fr, h5py.File(comp_path, "w") as fw:

        def copy_group(src, dst):
            for name, item in src.items():
                if isinstance(item, h5py.Group):
                    newg = dst.create_group(name)
                    copy_group(item, newg)
                else:
                    dst.create_dataset(name, data=item[()])

        copy_group(fr, fw)


def fake_noise_compress(self, raw_path, comp_path, cratio):
    """Copy raw HDF5 to comp HDF5, adding deterministic noise to simulate lossy compression."""
    with h5py.File(raw_path, "r") as fr, h5py.File(comp_path, "w") as fw:
        # Read full 3D volume
        raw_arr = fr["entry_0000/ESRF-ID11/marana/data"][()]
        # Add small Gaussian noise
        rng = np.random.RandomState(0)
        noise = rng.normal(loc=0, scale=1.0, size=raw_arr.shape)
        noisy = (raw_arr.astype(np.float32) + noise).clip(0, np.iinfo(np.uint16).max)
        noisy = noisy.astype(np.uint16)
        grp = fw.require_group("entry_0000/ESRF-ID11/marana")
        grp.create_dataset("data", data=noisy)


def test_jp2k_compression_preserves_ssim(tmp_path, monkeypatch):
    # Stub compress_file to be identity copy
    monkeypatch.setattr(JP2KCompressor, "compress_file", fake_identity_compress)

    raw = tmp_path / "raw.h5"
    comp = tmp_path / "raw_jp2k.h5"
    create_constant_3d_h5(str(raw), shape=(3, 16, 16), value=1234)

    compressor = JP2KCompressor()
    compressor.compress_file(str(raw), str(comp), cratio=5)

    s_raw, s_comp = compute_ssim_for_dataset_pair(
        str(raw), str(comp), "entry_0000/ESRF-ID11/marana/data"
    )
    # SSIM of identical volumes must be ≈1
    assert pytest.approx(1.0, rel=1e-9) == s_raw
    assert pytest.approx(1.0, rel=1e-9) == s_comp


def test_jp2k_compression_different_values(tmp_path, monkeypatch):
    # Stub compress_file to simulate noisy compression
    monkeypatch.setattr(JP2KCompressor, "compress_file", fake_noise_compress)

    raw = tmp_path / "raw.h5"
    comp = tmp_path / "raw_jp2k.h5"
    # Create a gradient volume so SSIM can detect structural differences
    with h5py.File(str(raw), "w") as f:
        grp = f.require_group("entry_0000/ESRF-ID11/marana")
        # Use a gradient across the volume
        data = np.linspace(0, 100, num=4 * 4 * 4, dtype=np.uint16).reshape((4, 4, 4))
        grp.create_dataset("data", data=data)

    compressor = JP2KCompressor()
    compressor.compress_file(str(raw), str(comp), cratio=2)

    s0, s1 = compute_ssim_for_dataset_pair(
        str(raw), str(comp), "entry_0000/ESRF-ID11/marana/data"
    )
    # SSIM should reflect added noise and be strictly less than 1
    assert 0.0 < s0 < 1.0, f"Expected 0 < s0 < 1 but got {s0}"
    assert 0.0 < s1 < 1.0, f"Expected 0 < s1 < 1 but got {s1}"
