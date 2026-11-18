# Build, Packaging, and Release

## Build principles
- Reproducible build configuration.
- Separate native and Python build stages.
- Correct OS/architecture pairing.
- No development paths or debug secrets in release packages.
- Include license notices for bundled dependencies.
- Verify that native library is loaded from the expected application directory.

## Windows
Choose portable ZIP and/or installer after evaluating update/uninstall needs. Consider signing release executables. Test UAC behaviour and non-admin operation. Do not require admin at application startup.

## Linux
Choose AppImage, Flatpak, or distribution packages based on dependency and integration needs. AppImage is not automatically the best fit for every desktop integration. Test on declared distributions.

## Release pipeline
1. Tag source commit.
2. Build in CI on clean runners.
3. Run tests and static analysis.
4. Package per platform/architecture.
5. Smoke-test artifacts.
6. Generate SHA-256 checksums.
7. Publish release notes and support matrix.
8. Sign artifacts when available.
9. Preserve build logs and QA evidence.

## Release notes
Separate added features, changes, fixes, known limitations, security changes, and platform-specific notes. Never list roadmap items as released features.
