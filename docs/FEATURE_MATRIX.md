# Feature Matrix

Legend: `P0` initial foundation, `P1` next milestone, `P2` later, `Research` requires design/verification. Nothing here means implemented.

| Feature | Windows | Linux | Priority | Notes |
|---|---|---|---|---|
| Temporary-file scan | Yes | Yes | P0 | Allow-listed targets only |
| Temporary-file cleanup | Yes | Yes | P0 | Preview, confirmation, revalidation |
| Cleanup history | Yes | Yes | P0 | Privacy-minimal metadata |
| CPU monitoring | Yes | Yes | P0 | Platform adapter |
| Memory monitoring | Yes | Yes | P0 | Different OS metric semantics |
| Disk usage monitoring | Yes | Yes | P0 | Per-volume |
| Process list/basic metrics | Yes | Yes | P1 | Permission-limited fields |
| Storage analyzer | Yes | Yes | P1 | Respect filesystem boundaries |
| Recycle bin/trash cleanup | Research | Research | P1 | Use platform-supported APIs |
| Browser cache cleanup | Research | Research | P1 | Browser must be closed; never remove profiles |
| App-specific cache cleanup | Research | Research | P1 | Per-app rules and version tests |
| Windows standby-list operation | Research | N/A | P2 | Explain trade-offs; supported API only |
| Windows working-set trim | Research | N/A | P2 | No blanket claims; per-process effects |
| Linux drop-caches operation | N/A | Research | P2 | Advanced opt-in only; likely not routine feature |
| Startup app management | Research | Research | P2 | No automatic disabling |
| Service management | Research | Research | P2 | High risk; defer |
| Scheduled cleanup | Yes | Yes | P2 | User-configured and opt-in |
| Tray integration | Yes | Yes | P2 | Must be low overhead |
| CLI/headless mode | Yes | Yes | P2 | Reuse same application services |

## Release gates
A feature may be marked "Supported" only after:
- implementation exists for the named OS/version/architecture;
- positive and negative tests pass;
- permission and unsupported cases are tested;
- operation is documented;
- user-facing description is accurate;
- packaged build is verified.
