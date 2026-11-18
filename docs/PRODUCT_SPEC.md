# Product Specification

## 1. Product vision
JunksCleaner is a lightweight desktop utility for Windows and Linux that gives users safe, understandable control over selected maintenance tasks and useful visibility into system resource usage.

It is not intended to be a magical one-click performance booster. The product should show what it will do, why it is safe, what permissions are required, and what changed.

## 2. Target users
- Everyday desktop and laptop users who need to inspect and remove clearly disposable temporary data.
- Technical users who want system resource monitoring and storage analysis.
- Developers and power users who value logs, predictable behaviour, and transparent native operations.

## 3. Product goals
1. Safe, accurate junk-file discovery and cleanup.
2. Low idle CPU and memory footprint.
3. Useful live CPU, memory, disk and process information.
4. Clearly explained, opt-in memory maintenance where supported.
5. A consistent GUI on Windows and Linux.
6. Modular architecture that permits new cleaners and platform adapters.
7. Robust handling of permissions, locked files, partial failures, and cancellation.

## 4. Non-goals for initial releases
- Registry cleaning or registry repair.
- Driver updates.
- Antivirus or malware removal.
- Automatic deletion of downloads, documents, photos, browser profiles, or user-created content.
- Automatic service disabling or startup optimization.
- Guaranteed FPS, battery-life, boot-time, or performance improvements.
- Kernel drivers, kernel modules, or undocumented system hooks.
- Cloud account, telemetry, or remote device management.
- Unattended aggressive RAM cleaning.

## 5. Core user journeys
### Scan and clean
1. User opens Junk Cleaner.
2. App discovers only enabled, known cleanup targets.
3. App displays category, path, item count, estimated size, and risk.
4. User reviews individual categories and can deselect items.
5. User confirms the operation.
6. Engine revalidates paths and target policy immediately before deletion.
7. User sees per-target progress and skipped/error counts.
8. A report is recorded without storing unnecessary sensitive file contents.

### Monitor system
1. User opens dashboard.
2. App samples metrics at a modest configurable interval.
3. UI shows timestamped values and indicates unavailable metrics.
4. Monitoring stops or slows when the app is minimized, according to settings.

### Memory operation
1. User selects an explicitly described operation.
2. App explains its effect, platform requirement, and possible downside.
3. User confirms.
4. The native backend performs only that operation.
5. Before/after measurements are shown without claiming that all freed cache equals improved performance.

## 6. UX principles
- Clear labels; no ambiguous "Boost" button.
- Show units and timestamps.
- Distinguish used, available, cached, committed, and swap/pagefile metrics.
- Explain why a file is eligible for deletion.
- Preview is mandatory for destructive cleanup.
- Partial success must be visible.
- Permission requests must be scoped and explained.
- Keyboard navigation, accessible labels, scalable layouts, and localization readiness.

## 7. Performance goals (initial engineering targets)
These are targets to measure, not claims:
- Idle GUI CPU use should normally remain near zero between refreshes.
- Monitoring cadence configurable; default around 2 seconds, subject to profiling.
- No unbounded history buffers.
- No full filesystem scans on the GUI thread.
- Large scans and cleanup operations must be cancellable.
- Memory footprint should be measured on a clean packaged build and recorded in release QA.

## 8. Supported platforms
Initial target: 64-bit Windows 10/11 and mainstream 64-bit Linux distributions using supported desktop environments. Exact minimum versions and distributions must be declared after CI/build verification. Unsupported operations must return `UNSUPPORTED`, not silently substitute a different operation.

## 9. Product terminology
Prefer "temporary files", "cached data", "available memory", "standby/cache", and "memory operation". Avoid "boost RAM", "free all RAM", "repair PC", and unsubstantiated speed claims.
