# Architecture

## 1. High-level design
Use a layered architecture:

`PySide6 UI -> Python application/services -> stable C ABI -> native C++ core -> OS adapters`

The GUI must not call platform APIs directly. The native core must not depend on Qt or Python. The C ABI is the only supported in-process boundary.

## 2. Proposed repository structure
```text
JunksCleaner/
├── AGENTS.md
├── README.md
├── CMakeLists.txt
├── pyproject.toml
├── CMakePresets.json
├── src/
│   └── native/
│       ├── CMakeLists.txt
│       ├── include/junkscleaner/
│       │   ├── jc_api.h
│       │   ├── jc_types.h
│       │   └── jc_version.h
│       ├── core/
│       │   ├── error/
│       │   ├── logging/
│       │   ├── cleanup/
│       │   ├── memory/
│       │   ├── monitoring/
│       │   └── storage/
│       ├── platform/
│       │   ├── windows/
│       │   └── linux/
│       └── tests/
├── app/
│   └── junkscleaner/
│       ├── main.py
│       ├── bootstrap/
│       ├── core/
│       ├── services/
│       ├── native/
│       ├── models/
│       ├── viewmodels/
│       ├── views/
│       ├── widgets/
│       ├── resources/
│       └── workers/
├── tests/
│   ├── python/
│   ├── integration/
│   ├── fixtures/
│   └── safety/
├── docs/
├── scripts/
├── packaging/
└── .github/workflows/
```

This is a proposal. Keep the actual initial implementation smaller if that improves delivery, but preserve module boundaries.

## 3. Layer responsibilities
### UI
Pages, dialogs, widgets, accessibility, theme, translations, and rendering. No filesystem deletion or OS calls in widgets.

### Python application layer
Use cases, orchestration, validation, task lifecycle, configuration, and mapping native results into UI models. It may use worker threads for blocking native calls.

### Native API facade
Python wrapper around the C ABI. Owns native library loading, ABI version checks, memory ownership rules, and conversion of native error codes.

### Native core
Platform-independent data types, policy checks, cleanup orchestration, progress callbacks, error model, and shared logic.

### Platform adapters
Windows/Linux implementations. They report capabilities and unsupported operations explicitly.

## 4. Concurrency
- Never perform filesystem scans, deletion, or long native operations on the GUI thread.
- Python worker orchestration must support cancellation and progress.
- Native callbacks must not call Qt directly.
- Define callback lifetime and thread affinity explicitly.
- Do not hold global locks while invoking user callbacks.
- Avoid detached native threads; task ownership and shutdown must be deterministic.

## 5. Process and privilege model
Default architecture is an unprivileged GUI process. Operations needing elevated access should use the narrowest feasible privilege mechanism. Do not elevate the whole application at startup. A privileged helper/service is a later design decision requiring a threat model, authenticated IPC, strict allow-listed commands, and separate review.

## 6. Error handling
Use explicit result types and error codes. Never use exceptions across the C ABI. Native exceptions must be caught internally. Preserve OS error codes and provide safe human-readable messages.

## 7. Dependency direction
UI -> application -> native wrapper -> native API -> core/platform.
Lower layers must not import higher layers. Platform adapters must not depend on GUI code.

## 8. Build boundaries
CMake builds native libraries and tests. Python packaging builds the UI application and bundles the matching native library. Build architecture (x64/ARM64) and platform must match. Do not assume one binary works on both Windows and Linux.

## 9. Design decisions to record
Use `docs/DECISIONS.md` for ADRs. Record changes to ABI, privilege model, dependency choices, data locations, supported platforms, and packaging.
