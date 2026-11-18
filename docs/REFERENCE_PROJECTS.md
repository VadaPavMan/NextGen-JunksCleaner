# Reference Projects and Competitive Research

This document records lessons, not instructions to copy source code. Recheck upstream repositories before making implementation decisions.

## User's prior projects
### JunksCleaner-v2.0
Repository: https://github.com/VadaPavMan/JunksCleaner-v2.0
Public repository metadata showed a Python/CustomTkinter Windows cleaner with `main.py`, `test.py`, and icon assets. Its README was effectively empty at the time of review. Treat as a GUI concept/reference, not an established architecture.

### Junks-Cleaner-CLI
Repository: https://github.com/VadaPavMan/Junks-Cleaner-CLI
C++17/CMake project. Its README describes temporary-file cleanup, memory operations on Windows/Linux, system diagnostics, and ADB log tracking. The documented source layout includes main, utility, logging, and memory-cleaner modules. It is the strongest candidate for selective code review and migration.

Important caveat: the README describes aggressive operations and makes performance/battery claims that must not be assumed correct. Verify source implementation, API usage, error handling, and behaviour before reuse. The browser-based review did not constitute a complete source-code audit.

## Mem Reduct
Repository: https://github.com/henrypp/memreduct
Describes lightweight real-time memory monitoring and cleaning. README states it uses undocumented internal Native API features for some system cache operations and requires administrator rights for correct operation. Useful reference for compact monitoring UX and operation selection, but undocumented API usage is not a default design recommendation.

## WinMemoryCleaner
Repository: https://github.com/IgorMundstein/WinMemoryCleaner
Documents memory areas and Windows-version availability, including standby list, modified page list, working set, system file cache, and registry cache. Useful reference for explicit operation descriptions, supported-version matrix, service/tray/automation concepts, and transparency.

## CCleaner
Commercial system utility reference. Study broad categories and interaction patterns such as scan/preview/clean, but do not copy branding, assets, UI, proprietary implementation, or imply feature parity.

## Lessons
- Separate cleanup categories and memory operations.
- Show user exactly what is selected.
- Prefer documented OS interfaces.
- Make privilege requirements visible.
- Measure actual results.
- Distinguish cached memory from application memory.
- Build a capability matrix per OS/version.
- Avoid claiming performance improvements without reproducible evidence.

## Licensing and attribution
Before adapting any source code, inspect the exact license file and relevant dependencies. Mem Reduct and WinMemoryCleaner identify GPL-3.0 licensing in their repositories; the user's CLI identifies MIT. These licenses have different obligations. Do not copy code from a GPL project into a differently licensed product without a deliberate compatibility decision and appropriate compliance. Recheck current upstream license files and notices.
