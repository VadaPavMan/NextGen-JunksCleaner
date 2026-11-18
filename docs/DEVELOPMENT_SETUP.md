# Development Setup

## Prerequisites
Install a supported Python 3 version, C/C++ compiler toolchain, CMake, Git, and Qt/PySide6 development dependencies appropriate to the host OS. Exact minimum versions must be selected and pinned by the maintainers.

## Python environment
Create a virtual environment and install project dependencies from the repository's pinned dependency metadata. Do not use global Python packages for development.

## Native build
Use CMake presets for platform/compiler configurations. Build out of source in a dedicated build directory. Keep generated binaries out of source control unless a specific release artifact policy says otherwise.

Typical workflow (adapt preset names to the actual CMakePresets.json):
```bash
cmake --preset <developer-preset>
cmake --build --preset <developer-preset>
ctest --preset <developer-preset>
```

## Python checks
```bash
python -m pytest
python -m ruff check .
```
Commands are examples until matching config files and presets are committed.

## Run
Launch the Python package using its documented development entry point. Ensure the matching native library is discoverable and ABI-compatible.

## Platform notes
Windows and Linux builds are separate. Never copy a Windows DLL into a Linux package or vice versa. Confirm architecture compatibility.
