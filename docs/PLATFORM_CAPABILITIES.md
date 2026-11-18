# Platform Capabilities and Semantic Differences

## Rule
Cross-platform UI does not mean identical OS behaviour. The backend must expose capability discovery and semantic descriptions. Never pretend Windows and Linux operations are equivalent when they are not.

## Capability discovery
At startup, backend reports:
- OS family and version;
- architecture;
- native library version and ABI version;
- supported operations;
- required privilege level per operation;
- limitations and reason when unavailable.

## Windows
Use documented Win32 APIs and supported performance/memory interfaces where possible. Use least privilege. Handle UAC and access-denied outcomes explicitly. Distinguish physical memory, commit, pagefile, standby/cache, and working-set metrics. Windows memory APIs and availability vary by OS version; check at runtime.

## Linux
Prefer `/proc`, `/sys`, `statvfs`, and documented system interfaces with robust parsing and permission handling. Do not assume all distributions expose identical fields. Detect unavailable or restricted `/proc` metrics. `drop_caches` is a kernel control intended for testing/debugging and should not be marketed as a normal speed optimization. It can discard useful caches and make subsequent I/O slower. Do not write to `/proc/sys/vm/drop_caches` in the default cleaner workflow.

## Filesystem differences
- Windows: drive letters, volume mount points, ACLs, reparse points, junctions, hard links, locked files, long paths.
- Linux: mount namespaces, bind mounts, symlinks, permissions, hard links, special files, case-sensitive names.
- Treat mount boundaries and symlinks explicitly.
- Never recursively follow symlinks/reparse points during cleanup unless a narrowly reviewed feature explicitly requires it.
- Use canonical/normalized paths and revalidate at deletion time.

## Unsupported operations
Return an explicit unsupported capability and reason. Do not substitute a superficially similar operation without informing the user.

## Platform test matrix
Test Windows versions supported by the project on clean VMs and at least two Linux distribution families before declaring broad support. Include non-admin/non-root execution.
