# Changelog

All notable changes to JunksCleaner will be documented here.

The project is currently at the documentation/architecture baseline. No application feature should be listed as released until implemented and verified.

## Unreleased
- Completed Milestone M2 (Safe cleanup MVP):
  - Added C ABI types in `jc_types.h`: `jc_risk_level_t`, `jc_cleanup_item_t`, `jc_scan_options_t`, `jc_scan_result_t`, `jc_cleanup_options_t`, and `jc_cleanup_report_t`.
  - Exported C ABI functions in `jc_api.h`: `jc_scan_cleanup_targets`, `jc_free_scan_result`, and `jc_execute_cleanup`.
  - Implemented `junkscleaner::safety` module enforcing strict canonical path containment, drive/home/system root rejection, and symlink/reparse-point escape detection.
  - Implemented `junkscleaner::cleanup` engine with target registry (`user_temp`), bounded recursion depth, file age policy, database/lock exclusions, and TOCTOU pre-deletion revalidation.
  - Implemented standalone native test suite `test_safe_cleanup` verifying path traversal rejection, symlink escape defense, dry-run simulation, and cancellation.
  - Implemented Python FFI bindings and `JunkCleanerService` orchestrating scan, preview model with deselection, explicit confirmation gate, dry-run, and audit history.
  - Added Pytest integration and safety suite verifying end-to-end cleanup pipeline and adversary attack containment.
- Completed Milestone M1 (Native platform and monitoring foundation):
  - Defined C ABI system snapshot types in `jc_types.h`: `jc_system_snapshot_t`, `jc_disk_info_t`, and `jc_snapshot_validity_flags_t`.
  - Added `jc_get_system_snapshot` exported C ABI function in `jc_api.h`.
  - Implemented Windows monitoring adapter using documented Win32 APIs: `GetSystemTimes`, `GlobalMemoryStatusEx`, `GetPerformanceInfo`, and `GetDiskFreeSpaceExW`.
  - Implemented Linux monitoring adapter reading `/proc/stat`, `/proc/meminfo`, and `statvfs`.
  - Added native GoogleTest/standalone test executable `test_system_snapshot` verifying telemetry ranges and validity bitmasks.
  - Implemented Python FFI snapshot binding with typed structures and formatting helpers.
  - Implemented `SystemMonitorService` providing background worker thread sampling, bounded history tracking, subscriber callbacks, and pause/resume lifecycle.
  - Added Pytest integration test suite covering snapshot retrieval, unavailable metrics fallback, and background thread lifecycle.
- Completed Milestone M0 (Repository and engineering foundation):
  - Created `.gitignore`, `pyproject.toml`, `CMakeLists.txt`, and `CMakePresets.json`.
  - Defined versioned C ABI contract headers: `jc_api.h`, `jc_types.h`, `jc_version.h`, and `jc_export.h`.
  - Implemented native core library `junkscleaner_native` with ABI version reporting and platform capability discovery for Windows and Linux.
  - Implemented standalone native test suite and registered with CTest.
  - Implemented Python FFI layer (`junkscleaner.native`) with ctypes bindings and ABI mismatch verification.
  - Added Pytest integration test suite and safe temporary directory fixtures.
  - Configured Ruff linter and GitHub Actions CI workflow skeleton.
- Established initial product, architecture, security, API, testing, and roadmap documentation.
- Defined Python/PySide6 frontend and C-compatible native-core direction.
- Defined preview-first cleanup and least-privilege principles.
