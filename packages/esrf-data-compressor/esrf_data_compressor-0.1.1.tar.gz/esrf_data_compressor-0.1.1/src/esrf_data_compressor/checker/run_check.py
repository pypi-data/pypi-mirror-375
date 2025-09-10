import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

from esrf_data_compressor.checker.ssim import compute_ssim_for_file_pair


def run_ssim_check(raw_files: list[str], method: str, report_path: str) -> None:
    """
    Given a list of raw HDF5 file paths, partitions into:
      to_check → those with a sibling <stem>_<method>.h5
      missing  → those without one

    Writes a report to `report_path`:
      - '=== NOT COMPRESSED FILES ===' listing each missing
      - then for each to_check pair, computes SSIM in parallel and appends
        per‐dataset SSIM lines under '=== <stem> ===' with full paths
    """
    to_check: list[tuple[str, str]] = []
    missing: list[str] = []

    # partition
    for orig in raw_files:
        dirname, fname = os.path.dirname(orig), os.path.basename(orig)
        stem, _ = os.path.splitext(fname)
        comp_path = os.path.join(dirname, f"{stem}_{method}.h5")
        if os.path.exists(comp_path):
            to_check.append((orig, comp_path))
        else:
            missing.append(orig)
    print(
        f"Found {len(to_check)} file pairs to check, {len(missing)} missing compressed files."
    )

    # write report
    with open(report_path, "w") as rpt:
        if missing:
            rpt.write("=== NOT COMPRESSED FILES ===\n")
            for orig in missing:
                rpt.write(f"{orig} :: NO COMPRESSED DATASET FOUND\n")
            rpt.write("\n")

        if not to_check:
            rpt.write("No file pairs to check (no compressed siblings found).\n")
            return

        # run SSIM in parallel
        n_workers = min(len(to_check), os.cpu_count() or 1)
        with ProcessPoolExecutor(max_workers=n_workers) as exe:
            futures = {
                exe.submit(compute_ssim_for_file_pair, orig, comp): (orig, comp)
                for orig, comp in to_check
            }

            for fut in tqdm(
                as_completed(futures),
                total=len(futures),
                desc="Checking SSIM (files)",
                unit="file",
            ):
                orig, comp = futures[fut]
                fname = os.path.basename(orig)
                comp_name = os.path.basename(comp)
                tqdm.write(f"Checking file: {fname} ↔ {comp_name}")
                try:
                    # get results
                    basename, lines = fut.result()
                    # write section with both file paths
                    rpt.write(f"=== {basename} ===\n")
                    rpt.write(f"Uncompressed file: {orig}\n")
                    rpt.write(f"Compressed file: {comp}\n")
                    for line in lines:
                        rpt.write(line + "\n")
                    rpt.write("\n")
                except Exception as e:
                    rpt.write(f"{orig} :: ERROR processing file pair: {e}\n\n")
