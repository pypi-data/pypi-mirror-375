import os
import sys
import re
import h5py
import h5py.h5d as h5d
from typing import List, Tuple, Optional, Set, Dict
from concurrent.futures import ProcessPoolExecutor, as_completed

try:
    from tqdm.auto import tqdm
except Exception:

    def tqdm(iterable=None, **kwargs):
        return iterable if iterable is not None else range(0)


JP2K_FILTER_ID = 32026
DATASET_CHECK_PATH = "/entry_0000/measurement/data"


def discover_datasets(path_components: List[str], base_root: str) -> List[str]:
    raw_root = os.path.join(base_root, *path_components, "RAW_DATA")
    if not os.path.isdir(raw_root):
        sys.exit(f"ERROR: RAW_DATA path not found: {raw_root}")

    scan_re = re.compile(r"^scan\d{4}$", re.IGNORECASE)
    datasets: List[str] = []

    for sample in sorted(os.listdir(raw_root)):
        sample_dir = os.path.join(raw_root, sample)
        if not os.path.isdir(sample_dir):
            continue
        for ds in sorted(os.listdir(sample_dir)):
            ds_dir = os.path.join(sample_dir, ds)
            if not os.path.isdir(ds_dir):
                continue

            h5s = [f for f in os.listdir(ds_dir) if f.lower().endswith(".h5")]
            if len(h5s) != 1:
                if len(h5s) > 1:
                    sys.exit(f"ERROR: Multiple .h5 in {ds_dir}: {h5s}")
                continue

            if not any(
                scan_re.match(d) and os.path.isdir(os.path.join(ds_dir, d))
                for d in os.listdir(ds_dir)
            ):
                continue

            datasets.append(os.path.join(ds_dir, h5s[0]))

    if not datasets:
        sys.exit(f"ERROR: No datasets found under {raw_root}")

    return sorted(datasets)


def _file_has_jp2k_filter(file_path: str) -> bool:
    try:
        with h5py.File(file_path, "r", locking=False) as src:
            obj = src.get(DATASET_CHECK_PATH)
            if not isinstance(obj, h5py.Dataset):
                return False
            plist = obj.id.get_create_plist()
            for j in range(plist.get_nfilters()):
                if plist.get_filter(j)[0] == JP2K_FILTER_ID:
                    return True
            return False
    except Exception:
        return False


def find_vds_files(
    path_components: List[str],
    base_root: str,
    filter_expr: Optional[str],
    *,
    max_workers: Optional[int] = None,
) -> Tuple[List[Tuple[str, str]], List[Tuple[str, str]]]:
    """
    Discover each dataset HDF5, then for each top-level group (e.g. "1.1"):
      - treat each filter key "A/B/C" as a dataset path under that group,
        i.e. grp["A"]["B"]["C"][()].
      - if any filter's desired substring is found in the dataset's value,
        classify that group's VDS sources into TO COMPRESS, reason="grp/A/B/C contains 'val'".
      - otherwise into REMAINING, reason="grp/A/B/C=<actual>".

    Adds a check for datasets already compressed with the JP2KCompressor's Blosc2/Grok filter
    (ID 32026) and classifies those files as REMAINING with reason "<already compressed>".

    Returns two lists of (vds_source_path, reason).
    """
    filters: List[Tuple[List[str], str]] = []
    if filter_expr:
        for tok in filter_expr.split(","):
            tok = tok.strip()
            if ":" not in tok:
                sys.exit(f"ERROR: Invalid filter token '{tok}'")
            key, val = tok.split(":", 1)
            parts = [p.strip() for p in key.split("/") if p.strip()]
            if not parts:
                sys.exit(f"ERROR: Empty filter key in '{tok}'")
            filters.append((parts, val.strip()))

    to_compress: List[Tuple[str, str]] = []
    remaining: List[Tuple[str, str]] = []

    datasets = discover_datasets(path_components, base_root)

    unique_files: Set[str] = set()
    occurrences: List[Tuple[str, bool, str]] = []

    for cont_path in tqdm(datasets, desc="Scan datasets", unit="file"):
        cont_dir = os.path.dirname(cont_path)
        with h5py.File(cont_path, "r", locking=False) as f:
            for grp_name, grp in f.items():
                if not isinstance(grp, h5py.Group):
                    continue

                group_matched = False
                reason = ""
                for parts, desired in filters:
                    obj = grp
                    for p in parts:
                        obj = obj.get(p)
                        if obj is None:
                            break
                    actual = obj[()] if isinstance(obj, h5py.Dataset) else None
                    if actual is not None and desired in str(actual):
                        reason = f"{grp_name}/{'/'.join(parts)} contains '{desired}'"
                        group_matched = True
                        break
                    else:
                        reason = f"{grp_name}/{'/'.join(parts)}={actual!r}"
                if not filters:
                    reason = f"{grp_name}/<no filter>"

                def visitor(name, obj):
                    if not isinstance(obj, h5py.Dataset):
                        return
                    plist = obj.id.get_create_plist()
                    if plist.get_layout() != h5d.VIRTUAL:
                        return
                    for i in range(plist.get_virtual_count()):
                        fn = plist.get_virtual_filename(i)
                        if isinstance(fn, bytes):
                            fn = fn.decode("utf-8", "ignore")
                        if not os.path.isabs(fn):
                            fn = os.path.abspath(os.path.join(cont_dir, fn))
                        unique_files.add(fn)
                        occurrences.append((fn, group_matched, reason))

                grp.visititems(visitor)

    if not occurrences:
        sys.exit(f"ERROR: No VDS sources found under {base_root}/{path_components}")

    fps = sorted(unique_files)
    if max_workers is None:
        cpu = os.cpu_count() or 8
        max_workers = min(16, max(4, cpu))

    compressed_map: Dict[str, bool] = {}
    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        futs = {ex.submit(_file_has_jp2k_filter, fp): fp for fp in fps}
        for fut in tqdm(
            as_completed(futs), total=len(fps), desc="Check compression", unit="file"
        ):
            fp = futs[fut]
            try:
                compressed_map[fp] = bool(fut.result())
            except Exception:
                compressed_map[fp] = False

    for fp, matched, reason in occurrences:
        if compressed_map.get(fp, False):
            remaining.append((fp, "<already compressed>"))
        else:
            if matched:
                to_compress.append((fp, reason))
            else:
                remaining.append((fp, reason))

    return to_compress, remaining


def write_report(
    to_list: List[Tuple[str, str]], rem_list: List[Tuple[str, str]], output_path: str
):
    with open(output_path, "w") as rpt:
        rpt.write("## TO COMPRESS ##\n")
        if to_list:
            for p, r in to_list:
                rpt.write(f"{p}    # {r}\n")
        else:
            rpt.write("(none)\n")

        rpt.write("\n## REMAINING ##\n")
        if rem_list:
            for p, r in rem_list:
                rpt.write(f"{p}    # {r}\n")
        else:
            rpt.write("(none)\n")
