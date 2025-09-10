import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

from esrf_data_compressor.compressors.jp2k import JP2KCompressorWrapper


class Compressor:
    """
    Abstract base class. Subclasses must implement compress_file().
    """

    def compress_file(self, input_path: str, output_path: str, **kwargs):
        raise NotImplementedError


class CompressorManager:
    """
    Manages parallel compression and overwrite.

    Each worker process is given up to 4 Blosc2 threads (or fewer if the machine
    has fewer than 4 cores).  The number of worker processes is then
    total_cores // threads_per_worker (at least 1).  If the user explicitly
    passes `workers`, we cap it to `total_cores`, then recompute threads_per_worker
    = min(4, total_cores // workers).

    Usage:
        mgr = CompressorManager(cratio=10, method='jp2k')
        mgr.compress_files([...])
        mgr.overwrite_files([...])
    """

    def __init__(
        self, workers: int | None = None, cratio: int = 10, method: str = "jp2k"
    ):
        total_cores = os.cpu_count() or 1

        # Determine default threads per worker (4, or fewer if total_cores < 4)
        if total_cores >= 4:
            default_nthreads = 4
        else:
            default_nthreads = 1

        # Default worker count
        default_workers = max(1, total_cores // default_nthreads)

        if workers is None:
            # Use default workers and default_nthreads
            w = default_workers
            nthreads = default_nthreads
        else:
            # Cap workers to total_cores
            w = min(workers, total_cores)
            # Recompute threads per worker so that (w * nthreads) ≤ total_cores, up to 4
            possible = total_cores // w
            nthreads = min(possible, 4) if possible >= 1 else 1

        self.workers = max(1, w)
        self.nthreads = max(1, nthreads)
        self.cratio = cratio
        self.method = method

        # Instantiate compressor based on method
        if self.method == "jp2k":
            self.compressor = JP2KCompressorWrapper(
                cratio=cratio, nthreads=self.nthreads
            )
        else:
            raise ValueError(f"Unsupported compression method: {self.method}")

        print(f"Compression method: {self.method}")
        print(f"Total CPU cores: {total_cores}")
        print(f"Worker processes: {self.workers}")
        print(f"Threads per worker: {self.nthreads}")
        print(f"Total threads: {self.workers * self.nthreads}")

    def _compress_worker(self, ipath: str) -> tuple[str, str]:
        """
        Worker function for ProcessPoolExecutor: compress a single HDF5:
        <ipath>.h5 → <same_dir>/<basename>_<method>.h5
        """
        base, _ = os.path.splitext(ipath)
        outp = f"{base}_{self.method}.h5"
        self.compressor.compress_file(
            ipath, outp, cratio=self.cratio, nthreads=self.nthreads
        )
        return ipath, "success"

    def compress_files(self, file_list: list[str]) -> None:
        """
        Compress each .h5 in file_list in parallel, producing <basename>_<method>.h5
        next to each source file. Does not overwrite originals. At the end, prints
        total elapsed time and data rate in MB/s.
        """
        valid = [p for p in file_list if p.lower().endswith(".h5")]
        if not valid:
            print("No valid .h5 files to compress.")
            return

        total_bytes = 0
        for f in valid:
            try:
                total_bytes += os.path.getsize(f)
            except OSError:
                pass

        import time

        t0 = time.time()

        with ProcessPoolExecutor(max_workers=self.workers) as executor:
            futures = {executor.submit(self._compress_worker, p): p for p in valid}
            for fut in tqdm(
                as_completed(futures),
                total=len(futures),
                desc=f"Compressing HDF5 files ({self.method})",
                unit="file",
            ):
                pth = futures[fut]
                try:
                    fut.result()
                except Exception as e:
                    print(f"Failed to compress '{pth}': {e}")

        t1 = time.time()
        elapsed = t1 - t0
        total_mb = total_bytes / (1024 * 1024)
        rate_mb_s = total_mb / elapsed if elapsed > 0 else float("inf")
        print(f"\nTotal elapsed time: {elapsed:.3f}s")
        print(f"Data processed: {total_mb:.2f} MB  ({rate_mb_s:.2f} MB/s)\n")

    def overwrite_files(self, file_list: list[str]) -> None:
        """
        Overwrites files only if they have a compressed sibling:

          1) Rename <file>.h5 → <file>.h5.bak
          2) Rename <file>_<method>.h5 → <file>.h5

        After processing all files, removes the backup .h5.bak files.
        """
        backups = []
        for ipath in file_list:
            if not ipath.lower().endswith(".h5"):
                continue

            base, _ = os.path.splitext(ipath)
            compressed_path = f"{base}_{self.method}.h5"

            if os.path.exists(compressed_path):
                backup = ipath + ".bak"
                try:
                    os.replace(ipath, backup)
                    os.replace(compressed_path, ipath)
                    backups.append(backup)
                    print(f"Overwritten '{ipath}' (backup at '{backup}').")
                except Exception as e:
                    print(f"ERROR overwriting '{ipath}': {e}")
            else:
                print(f"SKIP (no compressed file): {ipath}")

        # Remove all backup files
        for backup in backups:
            try:
                os.remove(backup)
                print(f"Deleted backup '{backup}'.")
            except Exception as e:
                print(f"ERROR deleting backup '{backup}': {e}")
