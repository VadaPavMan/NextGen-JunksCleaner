# AGENTS.md — JunksCleaner Development Contract

## Mission
Build JunksCleaner as a lightweight, reliable, transparent, cross-platform desktop system-maintenance application for Windows and Linux. Python/PySide6 owns the GUI. A native C/C++ core owns privileged and performance-sensitive system operations. A stable C ABI separates them.

## Authority and precedence
Read these files before changing code:
1. `docs/PRODUCT_SPEC.md`
2. `docs/ARCHITECTURE.md`
3. `docs/SECURITY.md`
4. `docs/PLATFORM_CAPABILITIES.md`
5. `docs/API_CONTRACT.md`
6. `docs/CODING_STANDARDS.md`
7. `docs/TESTING.md`
8. `docs/ROADMAP.md`

If documents conflict, stop and report the conflict. Do not silently choose an interpretation. `SECURITY.md` takes precedence for safety decisions.

## Mandatory agent behaviour
- Inspect the existing repository, build files, current branch, and tests before editing.
- Do not assume a feature exists because it appears in a README or roadmap.
- Do not claim a build, test, benchmark, or runtime check passed unless it was actually executed.
- Work in small, reviewable increments. State the plan before broad structural changes.
- Preserve working behaviour unless the task explicitly changes it.
- Do not rewrite the project or replace a library/framework without approval.
- Do not add dependencies without explaining why, license, maintenance status, size impact, and alternatives.
- Do not use undocumented OS interfaces as a default implementation.
- Never run destructive operations against the developer's real machine as a test.
- Never run cleanup against real user directories during automated tests.
- Never elevate the entire GUI process just to perform one privileged operation.
- Never silently delete files, modify startup entries, stop processes, disable services, or change system configuration.
- Treat all paths, filenames, process names, environment variables, and filesystem contents as untrusted input.
- Keep Windows-specific and Linux-specific code behind platform adapters.
- Keep GUI code free of OS-specific cleanup implementation.
- Keep native core independent of Qt/PySide and Python runtime.
- Do not expose C++ classes, STL containers, exceptions, or compiler-specific types across the C ABI.
- Do not return pointers to temporary memory across the ABI.
- Do not swallow errors. Return structured status and diagnostic information.
- Update documentation and tests whenever behaviour, API, configuration, or supported platforms change.

## Required workflow for each task
1. Restate the requested outcome and acceptance criteria.
2. Identify affected modules and platform implications.
3. Inspect relevant source and tests.
4. Propose the smallest implementation plan.
5. Implement one coherent change at a time.
6. Add/update unit, integration, and safety tests.
7. Run formatting, static checks, build, and relevant tests.
8. Report exact commands run and results; distinguish unrun checks.
9. Update docs, changelog, and roadmap status where applicable.

## Definition of done
A feature is not done merely because the UI button exists. It must have:
- defined behaviour and supported-platform status;
- correct native implementation or an explicit unsupported result;
- input validation and permission handling;
- cancellation and progress semantics where applicable;
- structured errors and logs;
- tests including failure and permission-denied paths;
- UI states for loading, success, partial success, and failure;
- documentation and truthful user-facing explanation.

## Current baseline status
The repositories supplied as references are not automatically part of this new codebase. The previous CLI and GUI are reference implementations only until their code is independently reviewed and deliberately migrated. Never copy aggressive memory operations or undocumented behaviour without a safety review.
