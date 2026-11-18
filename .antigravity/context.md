# Persistent Project Context for Antigravity

Project: JunksCleaner

Product: Lightweight, cross-platform system maintenance and monitoring desktop app for Windows and Linux.

Chosen direction:
- Python + PySide6 for GUI.
- C++ native implementation with a stable C ABI.
- CMake for native builds.
- pytest and GoogleTest for testing.
- Windows and Linux platform adapters.
- Unprivileged GUI by default.
- Scan -> preview -> confirmation -> revalidation -> execution for destructive cleanup.

Reference repositories:
- https://github.com/VadaPavMan/JunksCleaner-v2.0
- https://github.com/VadaPavMan/Junks-Cleaner-CLI
- https://github.com/henrypp/memreduct
- https://github.com/IgorMundstein/WinMemoryCleaner

Important:
- Existing repositories are references, not automatically trusted code.
- Review source before migrating.
- Do not copy third-party code without license review.
- Do not make guaranteed performance or battery claims.
- Linux drop_caches is not a routine performance optimization.
- Undocumented Windows Native API calls are not the default design.
- No feature is complete without implementation, tests, error handling, and truthful UI.

Always read root AGENTS.md and relevant docs before coding. Follow ROADMAP.md in milestone order.
