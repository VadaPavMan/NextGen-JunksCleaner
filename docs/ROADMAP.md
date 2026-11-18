# Development Roadmap

Roadmap is milestone-based. Do not begin later milestones by building UI placeholders that imply working functionality.

## M0 — Repository and engineering foundation
- [x] Establish repository structure and license decision.
- [x] Add AGENTS.md and architecture docs.
- [x] Set up CMake and Python packaging.
- [x] Add formatting, lint, and CI skeleton.
- [x] Create native ABI version and capability discovery.
- [x] Add test harness and safe temporary fixture utilities.

**Exit:** Clean builds on Windows and Linux CI; ABI smoke test passes. [PASSED]

## M1 — Native platform and monitoring foundation
- [x] OS/architecture detection.
- [x] System snapshot API.
- [x] CPU, memory, disk metrics.
- [x] Python native wrapper.
- [x] Dashboard with metric unavailable states.
- [x] Unit and integration tests.

**Exit:** Accurate, labelled metrics on declared supported platforms. [PASSED]

## M2 — Safe cleanup MVP
- [x] Cleanup target registry.
- [x] Conservative temp-file discovery.
- [x] Candidate validation and path containment.
- [x] Preview model.
- [x] User confirmation.
- [x] Safe deletion and partial-result reporting.
- [x] Cancellation and audit history.

**Exit:** Safety tests pass; no out-of-scope deletion possible in test suite. [PASSED]

## M3 — GUI product foundation
- [x] Main window and navigation.
- [x] Dashboard, cleaner and activity pages.
- [x] Settings persistence.
- [x] Theme and accessibility pass.
- [x] Background workers and graceful shutdown.

**Exit:** Complete end-to-end scan/preview/clean flow on Windows and Linux. [PASSED]

## M4 — Storage analyzer and process visibility
- [ ] Volume overview.
- [ ] Directory size scan with exclusions and cancellation.
- [ ] Process list/basic metrics with permission handling.

**Exit:** Bounded resource usage and tested filesystem boundary handling.

## M5 — Advanced memory operations research
- [ ] Research each Windows operation and API support.
- [ ] Research Linux semantics; do not assume drop_caches is beneficial.
- [ ] Define operation-specific risk, privilege and UX.
- [ ] Benchmark on controlled workloads.
- [ ] Implement only justified, safe, testable operations.

**Exit:** Evidence-based feature decision; unsupported operations remain unavailable.

## M6 — Packaging and release
- [ ] Windows portable/package build.
- [ ] Linux AppImage or distribution packages.
- [ ] Clean VM install/upgrade/uninstall tests.
- [ ] Code signing strategy and checksums.
- [ ] Release QA report and support matrix.

## M7 — Optional later features
- [ ] Tray mode.
- [ ] Scheduled cleanup.
- [ ] Browser/app cache cleaners with explicit per-app rules.
- [ ] Startup manager (read-only first).
- [ ] CLI mode using shared services.
