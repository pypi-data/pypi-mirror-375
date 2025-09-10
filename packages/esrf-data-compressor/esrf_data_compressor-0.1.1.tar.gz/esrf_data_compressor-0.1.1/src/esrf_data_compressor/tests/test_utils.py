import pytest

from esrf_data_compressor.utils.utils import parse_report


def write_report(tmp_path, content: str) -> str:
    """Helper to write report content to a temp file and return its path."""
    report_path = tmp_path / "report.txt"
    report_path.write_text(content)
    return str(report_path)


def test_parse_report_basic(tmp_path):
    content = """
## SOME HEADER ##
foo
## TO COMPRESS ##
/path/to/file1.h5 details1
/path/to/file2.h5    extra info

## REMAINING ##
/path/to/file3.h5
"""
    report = write_report(tmp_path, content)
    result = parse_report(report)
    assert result == ["/path/to/file1.h5", "/path/to/file2.h5"]


def test_parse_report_with_comments_and_blank_lines(tmp_path):
    content = """
## TO COMPRESS ##
# this is a comment
/path/fileA.h5 (commented)
(path) should skip
/path/fileB.h5    (meta)

other line
## REMAINING ##
/path/fileC.h5
"""
    report = write_report(tmp_path, content)
    result = parse_report(report)
    # Should include only lines under TO COMPRESS without parentheses
    assert result == ["/path/fileA.h5", "/path/fileB.h5"]


def test_parse_report_missing_section(tmp_path):
    content = """
## REMAINING ##
/path/x.h5
## OTHER SECTION ##
/data/y.h5
"""
    report = write_report(tmp_path, content)
    result = parse_report(report)
    assert result == []


def test_parse_report_malformed_file(tmp_path):
    # Nonexistent file should raise RuntimeError
    bad_path = tmp_path / "no_exist.txt"
    with pytest.raises(RuntimeError) as exc:
        parse_report(str(bad_path))
    assert "Failed to parse report" in str(exc.value)
