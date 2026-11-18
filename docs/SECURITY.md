# Security and Safety Policy

## 1. Core safety promise
JunksCleaner must not destroy user data or change system configuration without clear user intent. The safest implementation is the default.

## 2. Cleanup threat model
Threats include path traversal, symlink/reparse-point escapes, time-of-check/time-of-use races, malicious filenames, hard links, mount-point traversal, concurrent file replacement, locked files, permission changes, and incorrect cleanup rules.

## 3. Mandatory deletion safeguards
- Use a strict allow-list of known cleanup roots and file patterns.
- Never accept arbitrary deletion paths from the UI or external input.
- Normalize and validate paths against approved roots.
- Reject root directories, home directories, profile roots, drive roots, and ambiguous paths.
- Do not follow symlinks, Windows reparse points, or mount boundaries by default.
- Revalidate each item immediately before deletion.
- Prefer handle-based operations and OS APIs that reduce TOCTOU exposure.
- Do not recursively delete a directory just because its name resembles a cache/temp folder.
- Exclude active application databases, browser profiles, cookies, sessions, credentials, downloads, and user documents.
- Skip files in use rather than force-killing their owning process.
- Do not silently change permissions to force deletion.
- Provide dry-run/preview and explicit confirmation.
- Record skipped and failed items without exposing sensitive contents.

## 4. Memory operations
- No "free all RAM" claims.
- Do not terminate processes to free memory.
- Do not alter process priority or kill services as a cleaning shortcut.
- Document exact operation and expected side effects.
- Require explicit opt-in for advanced operations.
- Measure before/after using clearly named metrics.
- Never imply cache reclamation is equivalent to improved performance.

## 5. Privileges
- Run GUI unprivileged by default.
- Request elevation only when an operation requires it.
- Explain why and what operation needs elevation.
- Do not store credentials.
- If a privileged helper is introduced, use a strict allow-listed protocol, authenticated local IPC, input validation, replay protection where applicable, and independent security review.

## 6. Native boundary
- Validate pointers, lengths, enum values, flags, and structure sizes.
- Use fixed-width integer types.
- Catch all C++ exceptions before crossing C ABI.
- Never expose raw internal pointers without a documented lifetime.
- Avoid unsafe deserialization and shell command construction.
- Do not execute commands assembled from user-controlled strings.

## 7. Privacy
- No telemetry by default.
- Do not upload filenames, paths, process lists, or system inventory.
- Logs should avoid sensitive paths where possible and support redaction.
- Configuration and logs stay local unless the user explicitly exports them.
- Document all data written by the app.

## 8. Supply chain
- Pin dependencies.
- Review licenses and known vulnerabilities.
- Build release artifacts in CI from tagged source.
- Publish SHA-256 checksums.
- Sign Windows artifacts when feasible.
- Protect release workflow permissions and secrets.
- Do not bundle opaque binaries.

## 9. Security tests
Test path traversal, symlink escape, reparse points, mount boundary, malformed names, Unicode names, permission denied, locked files, race conditions, empty paths, root paths, and cancellation.
