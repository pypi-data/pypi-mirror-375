import os
import argparse
from esrf_data_compressor.finder.finder import find_vds_files, write_report
from esrf_data_compressor.compressors.base import CompressorManager
from esrf_data_compressor.checker.run_check import run_ssim_check
from esrf_data_compressor.utils.hdf5_helpers import exit_with_error
from esrf_data_compressor.utils.utils import parse_report


def get_path_components(args):
    comps = [args.experiment]
    if args.beamline:
        comps.append(args.beamline)
    if args.session:
        comps.append(args.session)
    return comps


def do_list(args):
    """
    1) Discover datasets under RAW_DATA/<components...>
    2) Apply dataset‑level filters (--filter key:val[,key2:val2...])
    3) Extract VDS source files from every dataset
    4) Write two‑section report:
         ## TO COMPRESS ##   (sources from matching datasets)
         ## REMAINING ##     (sources from non‑matching datasets)
    """
    comps = get_path_components(args)
    try:
        to_c, rem = find_vds_files(comps, base_root=args.root, filter_expr=args.filter)
    except SystemExit as e:
        exit_with_error(str(e))

    report_path = args.output or "file_list.txt"
    write_report(to_c, rem, report_path)
    print(f"Report written to {report_path}")


def do_compress(args):
    report = args.input
    if not report:
        exit_with_error("The --input report file must be specified for compress")
    try:
        files = parse_report(report)
    except Exception as e:
        exit_with_error(f"Failed to read report '{report}': {e}")

    if not files:
        print("Nothing to compress (TO COMPRESS list is empty).")
        return

    print(
        f"Compressing {len(files)} file(s) from '{report}' using '{args.method}' method and ratio {args.cratio} …"
    )
    mgr = CompressorManager(cratio=args.cratio, method=args.method)
    mgr.compress_files(files)
    print("Compression complete.\n")


def do_check(args):
    report = args.input or "file_list.txt"
    try:
        files = parse_report(report)
    except Exception as e:
        exit_with_error(f"Failed to read report '{report}': {e}")

    if not files:
        print("Nothing to check (TO COMPRESS list is empty).")
        return

    # We reuse run_ssim_check in its 3‑arg form (raw_files, method, report_path)
    report_fname = f"{os.path.splitext(report)[0]}_{args.method}_ssim_report.txt"
    report_path = os.path.abspath(report_fname)

    try:
        run_ssim_check(files, args.method, report_path)
    except SystemExit as e:
        exit_with_error(str(e))

    print(f"SSIM report written to {report_path}\n")


def do_overwrite(args):
    """
    Overwrite TO COMPRESS files with their original sources.
    """
    report = args.input or "file_list.txt"
    try:
        files = parse_report(report)
    except Exception as e:
        exit_with_error(f"Failed to read report '{report}': {e}")

    if not files:
        print("Nothing to overwrite (TO COMPRESS list is empty).")
        return

    print(f"Overwriting {len(files)} file(s) from '{report}' …")
    mgr = CompressorManager()
    mgr.overwrite_files(files)
    print("Overwrite complete.\n")


def main():
    parser = argparse.ArgumentParser(
        description="List, compress, check or overwrite ESRF HDF5 VDS sources."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # list
    p = sub.add_parser("list", help="Report VDS sources → TO COMPRESS vs REMAINING")
    p.add_argument("experiment", help="Experiment ID")
    p.add_argument("beamline", nargs="?", help="Optional beamline")
    p.add_argument("session", nargs="?", help="Optional session")
    p.add_argument("--root", default="/data/visitor", help="Base directory")
    p.add_argument(
        "--filter",
        metavar="KEY:VAL[,KEY2:VAL2...]",
        help="Dataset‑level attribute substring filters",
    )
    p.add_argument("--output", help="Report file (default = file_list.txt)")
    p.set_defaults(func=do_list)

    # compress
    p = sub.add_parser("compress", help="Compress only the TO COMPRESS files")
    p.add_argument(
        "--input",
        "-i",
        required=True,
        help="Report file to read (must be produced by `list`)",
    )
    p.add_argument("--cratio", type=int, default=10, help="Compression ratio")
    p.add_argument(
        "--method",
        choices=["jp2k"],
        default="jp2k",
        help="Compression method",
    )
    p.set_defaults(func=do_compress)

    # check
    p = sub.add_parser("check", help="Generate SSIM report for TO COMPRESS files")
    p.add_argument(
        "--input", "-i", help="Report file to read (default = file_list.txt)"
    )
    p.add_argument(
        "--method", choices=["jp2k"], default="jp2k", help="Compression method"
    )
    p.set_defaults(func=do_check)

    # overwrite
    p = sub.add_parser("overwrite", help="Overwrite only TO COMPRESS files")
    p.add_argument(
        "--input", "-i", help="Report file to read (default = file_list.txt)"
    )
    p.set_defaults(func=do_overwrite)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
