import pytest
from pathlib import Path

import esrf_data_compressor.checker.run_check as rs


@pytest.fixture(autouse=True)
def sync_parallel(monkeypatch):
    """Force ProcessPoolExecutor to run tasks synchronously and disable tqdm output."""

    class DummyExecutor:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def submit(self, fn, *args, **kwargs):
            class Fut:
                def __init__(self, fn, args):
                    self._fn, self._args = fn, args

                def result(self):
                    return self._fn(*self._args)

            return Fut(fn, args)

    monkeypatch.setattr(rs, "ProcessPoolExecutor", DummyExecutor)
    monkeypatch.setattr(rs, "as_completed", lambda futures: list(futures))
    # monkeypatch tqdm so it just returns the iterable
    monkeypatch.setattr(rs, "tqdm", lambda it, **kw: it)
    rs.tqdm.write = lambda *a, **k: None


def _read_report(report_path):
    return Path(report_path).read_text().splitlines()


def test_missing_files_only(tmp_path, monkeypatch):
    raw = tmp_path / "raw1.h5"
    raw.write_text("dummy")
    report = tmp_path / "report.txt"

    # ensure compute_ssim is never actually called
    monkeypatch.setattr(
        rs,
        "compute_ssim_for_file_pair",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("should not run")),
    )

    rs.run_ssim_check([str(raw)], method="m", report_path=str(report))
    lines = _read_report(report)

    assert lines[0] == "=== NOT COMPRESSED FILES ==="
    assert f"{raw} :: NO COMPRESSED DATASET FOUND" in lines
    # after a blank line it should say no pairs
    assert any("No file pairs to check" in line for line in lines)


def test_successful_ssim_report(tmp_path, monkeypatch):
    raw = tmp_path / "data1.h5"
    comp = tmp_path / "data1_method.h5"
    raw.write_text("r")
    comp.write_text("c")
    report = tmp_path / "report.txt"

    expected_basename = "data1"
    expected_lines = ["dataset1: 0.99", "dataset2: 0.98"]

    def fake_ssim(o, c):
        assert o == str(raw) and c == str(comp)
        return expected_basename, expected_lines

    monkeypatch.setattr(rs, "compute_ssim_for_file_pair", fake_ssim)

    rs.run_ssim_check([str(raw)], method="method", report_path=str(report))
    lines = _read_report(report)

    # header and file paths
    assert lines[0] == f"=== {expected_basename} ==="
    assert lines[1] == f"Uncompressed file: {raw}"
    assert lines[2] == f"Compressed file: {comp}"
    # SSIM detail lines
    assert lines[3:] == expected_lines + [""]  # trailing blank


def test_ssim_error_handling(tmp_path, monkeypatch):
    raw = tmp_path / "d2.h5"
    comp = tmp_path / "d2_method.h5"
    raw.write_text("r2")
    comp.write_text("c2")
    report = tmp_path / "report.txt"

    def Error(o, c):
        raise RuntimeError("Error")

    monkeypatch.setattr(rs, "compute_ssim_for_file_pair", Error)

    rs.run_ssim_check([str(raw)], method="method", report_path=str(report))
    lines = _read_report(report)

    # should include an ERROR line mentioning the exception message
    assert any("ERROR processing file pair" in line for line in lines)
    assert any("Error" in line for line in lines)
