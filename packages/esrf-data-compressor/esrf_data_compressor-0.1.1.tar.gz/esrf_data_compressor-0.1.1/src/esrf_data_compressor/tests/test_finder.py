# src/esrf_data_compressor/tests/test_finder_improved.py
import h5py
import pytest

from esrf_data_compressor.finder.finder import discover_datasets, find_vds_files


@pytest.fixture
def tmp_project(tmp_path):
    """
    Build a fake RAW_DATA structure:
    tmp/RAW_DATA/sampleA/ds1/file1.h5 + scan0001/
    tmp/RAW_DATA/sampleB/ds2/file2.h5 + scan0002/
    """
    raw = tmp_path / "RAW_DATA"
    for sample, ds, fname in [
        ("sampleA", "ds1", "file1.h5"),
        ("sampleB", "ds2", "file2.h5"),
    ]:
        ds_dir = raw / sample / ds
        ds_dir.mkdir(parents=True)
        with h5py.File(ds_dir / fname, "w"):
            (ds_dir / "scan0001").mkdir()
    return tmp_path


def test_discover_datasets_success(tmp_project):
    paths = discover_datasets([], str(tmp_project))
    assert len(paths) == 2
    assert paths[0].endswith("file1.h5")
    assert paths[1].endswith("file2.h5")


def test_discover_datasets_missing_raw(tmp_path):
    with pytest.raises(SystemExit) as ei:
        discover_datasets([], str(tmp_path / "nonexistent"))
    assert "RAW_DATA path not found" in str(ei.value)


def test_discover_datasets_multiple_h5(tmp_path):
    base = tmp_path / "RAW_DATA" / "sampleX" / "dsX"
    base.mkdir(parents=True)
    h5py.File(base / "a.h5", "w").close()
    h5py.File(base / "b.h5", "w").close()
    (base / "scan0001").mkdir()
    with pytest.raises(SystemExit) as ei:
        discover_datasets([], str(tmp_path))
    assert "Multiple .h5" in str(ei.value)


def test_discover_datasets_no_datasets(tmp_path):
    (tmp_path / "RAW_DATA").mkdir()
    with pytest.raises(SystemExit) as ei:
        discover_datasets([], str(tmp_path))
    assert "No datasets found" in str(ei.value)


def test_find_vds_invalid_filter(tmp_path):
    with pytest.raises(SystemExit):
        find_vds_files([], str(tmp_path), filter_expr="no_colon_filter")


def test_find_vds_no_sources(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "esrf_data_compressor.finder.finder.discover_datasets",
        lambda *args, **kwargs: [],
    )
    with pytest.raises(SystemExit) as ei:
        find_vds_files([], str(tmp_path), filter_expr=None)
    assert "No VDS sources found" in str(ei.value)
