import pytest
from esrf_data_compressor.utils.hdf5_helpers import exit_with_error


def test_exit_with_error(capsys):
    with pytest.raises(SystemExit):
        exit_with_error("something bad")
    captured = capsys.readouterr()
    assert "ERROR: something bad" in captured.err
