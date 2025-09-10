# ESRF Data Compressor

**ESRF Data Compressor** is a command-line tool and Python library designed to compress large ESRF HDF5 datasets (3D volumes) and verify data consistency via SSIM. The default compression backend uses Blosc2 + Grok (JPEG2000).

---

## Features

* **Discover raw HDF5 dataset files** under an experiment’s `RAW_DATA`

  * Goes through the HDF5 Virtual Datasets to find the data to compress
  * Allows to filter down scan by scan based on the value of a key

* **Slice-by-slice compression**

  * Uses Blosc2 + Grok (JPEG2000) on every slice of each 3D dataset (axis 0)
  * User-configurable compression ratio (e.g. `--cratio 10`)

* **Parallel execution**

  * Automatically factors CPU cores into worker processes × per-process threads
  * By default, each worker runs up to 4 Blosc2 threads (or falls back to 1 thread if < 4 cores)

* **Non-destructive workflow**

  1. `compress` writes a sibling file `<basename>_<compression_method>.h5` next to each original
  2. `check` computes SSIM (first and last frames) and writes a report
  3. `overwrite` (optional) swaps out the raw frame file (irreversible)

* **Four simple CLI subcommands**

  * `compress-hdf5 list`  Show all raw HDF5 files to be processed
  * `compress-hdf5 compress` Generate compressed siblings
  * `compress-hdf5 check`  Produce a per-dataset SSIM report between raw & compressed
  * `compress-hdf5 overwrite` Atomically replace each raw frame file (irreversible)

---

## Installation

### From PyPI

```bash
pip install esrf-data-compressor
```

Once installed, the `compress-hdf5` command will be available in your `PATH`.

### From Source (for development)

```bash
git clone https://gitlab.esrf.fr/dau/esrf-data-compressor.git
cd esrf-data-compressor

# (Optional) Create & activate a virtual environment
python -m venv venv
source venv/bin/activate

# Install build dependencies & the package itself
pip install .
```

---

## Documentation

Full documentation is available online:
[ESRF Data Compressor Docs](https://esrf-data-compressor.readthedocs.io/en/latest/index.html)

## Contributing & Development

* **Clone** the repository:

  ```bash
  git clone https://gitlab.esrf.fr/dau/esrf-data-compressor.git
  cd esrf-data-compressor
  ```

* **Install** dependencies (in a virtual environment):

  ```bash
  python -m venv venv
  source venv/bin/activate
  pip install -e "[dev]"
  ```

* **Run tests** with coverage:

  ```bash
  pytest -v --cov=esrf_data_compressor --cov-report=term-missing
  ```

* **Style:**

  * `black .`
  * `flake8 .`
  * `ruff .`

* **Build docs** (Sphinx + pydata theme):

  ```bash
  sphinx-build doc build/html
  ```

---

## License

This project is licensed under the [MIT License](LICENSE). See `LICENSE` for full text.

---

## Changelog

All noteworthy changes are recorded in [CHANGELOG.md](CHANGELOG.md). Version 0.1.0 marks the first public release with:

* Initial implementation of Blosc2 + Grok (JPEG2000) compression for 3D HDF5 datasets.
* SSIM-based integrity check (first & last slice).
* Four-command CLI (`compress-hdf5 list`, `compress-hdf5 compress`, `compress-hdf5 check`, `compress-hdf5 overwrite`).
* Parallelism with worker×thread auto-factoring.

For more details, see the full history in [CHANGELOG.md](CHANGELOG.md).