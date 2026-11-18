# Testing and Quality Strategy

## 1. Test pyramid
- Native unit tests: policy, path validation, parsing, metrics calculations.
- Python unit tests: services, state transitions, config, result mapping.
- Integration tests: Python-to-native ABI, cancellation, progress, errors.
- Platform tests: real OS APIs in disposable VMs.
- GUI tests: key workflows, accessibility smoke tests.
- Packaging tests: launch, native library loading, clean uninstall/upgrade.

## 2. Safety-first test rules
Never run cleanup tests against real user or system directories. All deletion tests use temporary fixture roots. Tests must assert that files outside the approved root remain unchanged. Include symlink/reparse-point escape tests.

## 3. Required cases
- Success, empty scan, partial failure, permission denied, unsupported OS.
- Invalid/malformed path and Unicode filenames.
- Locked/in-use files.
- Cancellation during scan and deletion.
- Large directory and long path.
- Native library missing, ABI mismatch, architecture mismatch.
- Application shutdown while worker active.
- Corrupt/unknown config version.
- Monitoring source unavailable or malformed.
- No-admin/non-root mode.

## 4. Tooling
Native: GoogleTest or another maintained C++ test framework.
Python: pytest; pytest-qt for GUI tests where appropriate.
Static checks: clang-format, clang-tidy, compiler warnings, ruff, mypy where practical.
Security: dependency and static analysis scans in CI.

## 5. CI matrix
Build/test Windows and Linux separately. Test supported architectures. CI must not run privileged destructive operations. Use mocked adapters for unit tests and controlled VM integration tests for OS-specific behaviour.

## 6. Release acceptance
- All required CI jobs green.
- No known critical/high security issue unresolved.
- No unexplained test skips.
- Smoke-tested packaged app on clean VM.
- Native library and GUI versions match.
- Checksums and release notes generated.
- Feature support claims match actual tested matrix.
