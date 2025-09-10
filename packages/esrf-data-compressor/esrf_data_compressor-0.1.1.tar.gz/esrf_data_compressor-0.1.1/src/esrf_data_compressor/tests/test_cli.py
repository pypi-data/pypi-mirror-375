import sys
import pytest

import esrf_data_compressor.cli as cli
from types import SimpleNamespace
from esrf_data_compressor.compressors.jp2k import JP2KCompressorWrapper


@pytest.fixture(autouse=True)
def fake_exit(monkeypatch):
    """Catch calls to exit_with_error and turn them into SystemExit."""

    def _exit(msg):
        raise SystemExit(msg)

    monkeypatch.setattr(cli, "exit_with_error", _exit)
    return _exit


@pytest.fixture
def argv_runner(tmp_path, monkeypatch):
    """Helper to call cli_main with a given list of args."""

    def _run(args):
        monkeypatch.chdir(str(tmp_path))
        sys.argv = ["compress-hdf5"] + args
        return cli.main()

    return _run


def test_get_path_components_minimal():
    args = SimpleNamespace(experiment="E", beamline=None, session=None)
    assert cli.get_path_components(args) == ["E"]


def test_get_path_components_full():
    args = SimpleNamespace(experiment="E", beamline="BL", session="S")
    assert cli.get_path_components(args) == ["E", "BL", "S"]


# ----------------------
# Error path tests
# ----------------------


@pytest.mark.parametrize(
    "cmd,setup,expect_msg",
    [
        (
            "list",
            lambda m: m.setattr(
                cli,
                "find_vds_files",
                lambda *a, **k: (_ for _ in ()).throw(SystemExit("fail")),
            ),
            "fail",
        ),
        (
            "compress",
            lambda m: None,
            "The --input report file must be specified for compress",
        ),
    ],
)
def test_error_paths(argv_runner, fake_exit, monkeypatch, cmd, setup, expect_msg):
    setup(monkeypatch)
    with pytest.raises(SystemExit) as exc:
        if cmd == "list":
            argv_runner([cmd, "exp", "bl", "sess"])
        else:
            argv_runner([cmd, "-i", ""])
    assert expect_msg in str(exc.value)


# ----------------------
# Command execution tests using real CompressorManager
# ----------------------


@pytest.mark.parametrize(
    "cmd,msg_start",
    [
        ("compress", "Compressing"),
        ("overwrite", "Overwriting"),
    ],
)
def test_commands_with_non_empty_list(
    argv_runner, monkeypatch, capsys, cmd, msg_start, tmp_path
):
    # Prepare dummy .h5 files in temp directory
    files = ["f1.h5", "f2.h5"]
    for fname in files:
        (tmp_path / fname).write_text("data")
    # For overwrite, also create compressed sibling only for f1
    if cmd == "overwrite":
        (tmp_path / "f1_jp2k.h5").write_text("comp")
    # patch parse_report → absolute paths
    monkeypatch.setattr(
        cli, "parse_report", lambda rpt: [str(tmp_path / f) for f in files]
    )
    # stub JP2KCompressorWrapper.compress_file to no-op
    monkeypatch.setattr(
        JP2KCompressorWrapper,
        "compress_file",
        lambda self, inp, out, **kw: open(out, "w").close(),
    )

    # Run command
    argv = [cmd, "-i", "report.txt"]
    if cmd == "compress":
        argv += ["--cratio", "5", "--method", "jp2k"]
    argv_runner(argv)
    out = capsys.readouterr().out
    assert msg_start in out

    # For compress, verify compressed files created
    if cmd == "compress":
        for f in files:
            comp = tmp_path / f.replace(".h5", "_jp2k.h5")
            assert comp.exists()
    # For overwrite, verify original replaced and backup removed
    if cmd == "overwrite":
        # f1 was overwritten, f2 was skipped
        assert (tmp_path / "f1.h5").exists()
        # no backup remains
        assert not (tmp_path / "f1.h5.bak").exists()


def test_list_success_and_output_file(argv_runner, monkeypatch, capsys, tmp_path):
    # patch finder & writer
    monkeypatch.setattr(
        cli, "find_vds_files", lambda comps, base_root, filter_expr: (["A"], ["B"])
    )
    recorded = {}
    monkeypatch.setattr(
        cli, "write_report", lambda a, b, p: recorded.update({"a": a, "b": b, "p": p})
    )
    out_file = tmp_path / "out.txt"
    argv_runner(
        ["list", "exp", "bl", "sess", "--root", "/data", "--output", str(out_file)]
    )
    out = capsys.readouterr().out
    assert "Report written to" in out
    assert recorded["p"] == str(out_file)


@pytest.mark.parametrize(
    "cmd,empty_msg",
    [
        ("compress", "Nothing to compress"),
        ("check", "Nothing to check"),
        ("overwrite", "Nothing to overwrite"),
    ],
)
def test_empty_reports(argv_runner, monkeypatch, capsys, cmd, empty_msg, tmp_path):
    monkeypatch.setattr(cli, "parse_report", lambda rpt: [])
    extra = []
    if cmd == "compress":
        extra = ["--cratio", "3", "--method", "jp2k"]
    argv_runner([cmd, "-i", str(tmp_path / "rpt.txt")] + extra)
    assert empty_msg in capsys.readouterr().out


def test_check_success_writes_report(argv_runner, monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(cli, "parse_report", lambda rpt: ["f"])

    def run(files, method, out):
        with open(out, "w") as f:
            f.write("ok")

    monkeypatch.setattr(cli, "run_ssim_check", run)
    report = tmp_path / "rpt.txt"
    argv_runner(["check", "-i", str(report), "--method", "jp2k"])
    out = capsys.readouterr().out
    assert "SSIM report written to" in out
