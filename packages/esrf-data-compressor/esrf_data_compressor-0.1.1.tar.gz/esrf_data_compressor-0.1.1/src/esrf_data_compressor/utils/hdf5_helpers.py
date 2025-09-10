import sys
import h5py


def exit_with_error(msg: str):
    """
    Print an error message to stderr and exit(1).
    """
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def copy_attrs(src: "h5py.AttributeManager", dst: "h5py.AttributeManager"):
    """
    Copy all attributes from src to dst.
    """
    for key, val in src.items():
        dst[key] = val
