# Coding Standards

## General
- Prefer simple, explicit, testable code.
- Avoid premature abstraction and giant classes.
- Keep functions focused and error paths visible.
- Document non-obvious platform behaviour.
- Use descriptive names; avoid ambiguous abbreviations.
- No dead code, commented-out implementation blocks, or unexplained TODOs.

## C++
- C++17 baseline unless an ADR approves a newer standard.
- RAII for resource ownership.
- Avoid raw owning pointers.
- Use `std::filesystem` carefully with explicit symlink/error handling.
- Catch exceptions at API boundaries.
- No exceptions across C ABI.
- Enable strong compiler warnings.
- Keep platform headers out of public portable headers.
- Format with clang-format.

## C ABI
Follow `API_CONTRACT.md`; public ABI is C-compatible and versioned.

## Python
- Type hints for public functions and service boundaries.
- Use dataclasses or typed models for structured data.
- Keep Qt widgets thin.
- Use signals/slots for worker-to-UI communication.
- No `shell=True` with user-controlled data.
- Avoid blocking I/O on GUI thread.
- Format/lint consistently with Ruff.

## Error messages
Errors must say what failed and, where possible, what the user can do. Do not leak sensitive paths or raw internal details unnecessarily.

## Dependencies
Every dependency requires purpose, license, update activity, binary size impact, and security consideration. Pin versions for reproducible builds.
