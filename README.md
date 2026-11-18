# JunksCleaner

**A lightweight, transparent system maintenance and monitoring application for Windows and Linux.**

JunksCleaner is planned as a modular desktop application with a Python/PySide6 interface and a native C/C++ system core. Its goals are safe junk-file cleanup, system monitoring, storage visibility, and carefully scoped platform-specific maintenance.

> **Development status:** Architecture and requirements baseline. Features must not be described as implemented until code, tests, and supported-platform verification exist.

## Project principles
- Safety before aggressive optimization.
- Preview before deletion.
- No misleading RAM-boost or performance promises.
- Native operations with documented platform behaviour.
- Minimal background resource usage.
- Explicit permission boundaries.
- Cross-platform core contracts with platform-specific implementations.
- Observable, testable, reversible configuration changes where feasible.

## Planned modules
- Junk Cleaner
- Memory Manager
- System Monitor
- Storage Analyzer
- System Tools
- Activity & Reports

See [`docs/PRODUCT_SPEC.md`](docs/PRODUCT_SPEC.md), [`docs/FEATURE_MATRIX.md`](docs/FEATURE_MATRIX.md), and [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Technology direction
- Python + PySide6 for desktop UI.
- C++17 or newer for internal native implementation.
- C-compatible ABI for Python/native boundary.
- CMake for native builds.
- pytest and GoogleTest for tests.
- GitHub Actions for CI.

Versions and dependencies must be pinned/verified in the build configuration before release.

## Repository layout
See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the authoritative proposed structure.

## Safety
JunksCleaner must never delete files outside approved targets, follow arbitrary symlinks/reparse points during cleanup, or run broad cleanup without a preview and explicit user approval. Memory operations must explain what they do and their trade-offs. See [`docs/SECURITY.md`](docs/SECURITY.md).

## Development
Start with [`AGENTS.md`](AGENTS.md). Then follow [`docs/DEVELOPMENT_SETUP.md`](docs/DEVELOPMENT_SETUP.md) and [`docs/TESTING.md`](docs/TESTING.md).

## Reference projects
The prior JunksCleaner GUI and CLI, CCleaner, Mem Reduct, and WinMemoryCleaner are research references, not code specifications. See [`docs/REFERENCE_PROJECTS.md`](docs/REFERENCE_PROJECTS.md). Review licenses before copying or adapting any source.

## License
License selection is pending. Do not add a license declaration or copy code from third-party projects until the owner has selected a license and compatibility has been reviewed.
