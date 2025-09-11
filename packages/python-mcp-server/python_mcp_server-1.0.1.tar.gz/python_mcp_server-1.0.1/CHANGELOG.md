# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2025-09-10

Breaking
- Replaced the multi-tool surface with a single unified `notebook` tool for cell execution, datasets, and export.
- Removed rarely used tools (completion/inspect/sessions/etc.) from the public surface; kept `run_python_code`, `list_files`, `read_file`, `write_file`, `delete_file`, `install_dependencies`, and `restart_kernel`.

Added
- DuckDB-backed datasets: `datasets.register/list/describe/drop/sql` under the `notebook` tool, with safe SQL and robust artifact capture.
- Per-cell manifests + index.json written to `outputs/notebooks/<id>/` for reliable artifact retrieval.
- Concurrency and memory controls: per-notebook locks, global semaphore, soft/hard memory watermarks.
- Interpreter/venv flags: `--python`, `--venv`, `--pythonpath` for both stdio and http transports.

Fixed/Improved
- More robust rich-display capture and JSON result parsing.
- Integration tests covering notebook runs, dataset flows, and export.

[0.6.x]: historical changes prior to the 1.0.0 release.
## [1.0.1] - 2025-09-10

Fixed
- Increase dataset/state operation timeout to 60s to stabilize Python 3.10 CI during first-time DuckDB initialization.

