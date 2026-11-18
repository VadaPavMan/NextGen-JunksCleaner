# Changelog

All notable changes to JunksCleaner will be documented here.

The project is currently at the documentation/architecture baseline. No application feature should be listed as released until implemented and verified.

## Unreleased
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
