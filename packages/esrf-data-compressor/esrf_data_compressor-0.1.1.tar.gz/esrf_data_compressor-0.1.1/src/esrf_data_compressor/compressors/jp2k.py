# src/esrf_data_compressor/compressors/jp2k.py

import os
import time
import numpy as np
import h5py
import blosc2
import blosc2_grok
import hdf5plugin

from esrf_data_compressor.utils.hdf5_helpers import copy_attrs

hdf5plugin.register(filters=("blosc2",), force=True)

BASE_CPARAMS = {
    "codec": blosc2.Codec.GROK,
    "filters": [],
    "splitmode": blosc2.SplitMode.NEVER_SPLIT,
    "nthreads": 1,
}


class JP2KCompressorWrapper:
    """
    Wraps JP2KCompressor so we can pass `cratio` and `nthreads` from higher‐level code.
    """

    def __init__(self, cratio: int = 10, nthreads: int | None = None):
        self.cratio = cratio
        self.nthreads = nthreads
        self.inner = JP2KCompressor()

    def compress_file(self, input_path: str, output_path: str, **kwargs):
        cr = kwargs.get("cratio", self.cratio)
        nt = kwargs.get("nthreads", self.nthreads)
        self.inner.compress_file(input_path, output_path, cratio=cr, nthreads=nt)


class JP2KCompressor:
    """
    Uses Blosc2+Grok (JPEG2000) to compress each z‐slice of a 3D HDF5 dataset.
    """

    def __init__(self):
        pass

    def _setup_blosc2(self, cratio: int, nthreads: int):
        BASE_CPARAMS["nthreads"] = nthreads
        blosc2_grok.set_params_defaults(
            cod_format=blosc2_grok.GrkFileFmt.GRK_FMT_JP2,
            num_threads=nthreads,
            quality_mode="rates",
            quality_layers=np.array([cratio], dtype=np.float64),
        )

    def _compress_3d(self, name: str, src_dset: h5py.Dataset, dst_grp: h5py.Group):
        data = src_dset[()]
        Z, Y, X = data.shape

        dst_dset = dst_grp.create_dataset(
            name,
            shape=(Z, Y, X),
            dtype=src_dset.dtype,
            chunks=(1, Y, X),
            compression=32026,
        )

        t_comp = 0.0
        t_write = 0.0
        t0 = time.perf_counter()

        for z in range(Z):
            plane = data[z, :, :]
            t1 = time.perf_counter()
            b2im = blosc2.asarray(
                plane[np.newaxis, ...],
                chunks=(1, Y, X),
                blocks=(1, Y, X),
                cparams=BASE_CPARAMS,
            )
            cframe = b2im.schunk.to_cframe()
            t2 = time.perf_counter()
            t_comp += t2 - t1

            t3 = time.perf_counter()
            dst_dset.id.write_direct_chunk((z, 0, 0), cframe, filter_mask=0)
            t4 = time.perf_counter()
            t_write += t4 - t3

        t5 = time.perf_counter()
        print(
            f"    • '{name}': read {Z}×{Y}×{X} in {t5 - t0:.3f}s "
            f"(comp {t_comp:.3f}s, write {t_write:.3f}s)"
        )

        copy_attrs(src_dset.attrs, dst_dset.attrs)

    def _passthrough(self, name: str, src_dset: h5py.Dataset, dst_grp: h5py.Group):
        data = src_dset[()]
        newd = dst_grp.create_dataset(name, data=data)
        copy_attrs(src_dset.attrs, newd.attrs)

    def _copy_group(self, src_grp: h5py.Group, dst_grp: h5py.Group):
        for name, link in src_grp.items():
            # SoftLink / ExternalLink
            if isinstance(src_grp.get(name, getlink=True), h5py.SoftLink):
                dst_grp[name] = h5py.SoftLink(src_grp.get(name, getlink=True).path)
            elif isinstance(src_grp.get(name, getlink=True), h5py.ExternalLink):
                el = src_grp.get(name, getlink=True)
                dst_grp[name] = h5py.ExternalLink(el.filename, el.path)
            else:
                obj = src_grp[name]
                if isinstance(obj, h5py.Group):
                    newg = dst_grp.create_group(name)
                    copy_attrs(obj.attrs, newg.attrs)
                    self._copy_group(obj, newg)
                elif isinstance(obj, h5py.Dataset):
                    if obj.ndim == 3:
                        self._compress_3d(name, obj, dst_grp)
                    else:
                        self._passthrough(name, obj, dst_grp)

    def compress_file(
        self,
        input_path: str,
        output_path: str,
        cratio: int = 10,
        nthreads: int | None = None,
    ) -> None:
        if cratio < 1:
            raise ValueError("cratio must be ≥ 1")

        total_cores = os.cpu_count() or 1
        if nthreads is None:
            nthreads = total_cores
        nthreads = min(nthreads, total_cores)
        nthreads = max(nthreads, 1)

        self._setup_blosc2(cratio, nthreads)

        t_start = time.perf_counter()
        with h5py.File(input_path, "r") as fin, h5py.File(output_path, "w") as fout:
            copy_attrs(fin.attrs, fout.attrs)
            self._copy_group(fin, fout)
        t_end = time.perf_counter()
        print(
            f"[done] Compressed '{os.path.basename(input_path)}' → "
            f"'{os.path.basename(output_path)}' in {t_end - t_start:.3f}s\n"
        )
