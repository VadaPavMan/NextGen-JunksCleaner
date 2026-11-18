# Risk Register

| Risk | Impact | Mitigation | Gate |
|---|---|---|---|
| Incorrect cleanup target deletes user data | Critical | Allow-list, preview, path revalidation, fixture tests | P0/P2 |
| Symlink/reparse escape | Critical | No-follow traversal, canonical checks, adversarial tests | P0 |
| TOCTOU file replacement | High | Handle-based checks and execution-time revalidation | P0 |
| Undocumented memory APIs break | High | Prefer documented APIs; runtime capability checks | P5 |
| Linux cache drop reduces performance | Medium/High | Not default; explicit opt-in and evidence | P5 |
| Privileged helper compromise | Critical | Defer; threat model and strict IPC | Before helper |
| GUI freezes during scan | Medium | Worker model, cancellation, profiling | P2 |
| ABI mismatch/crash | High | Version check, struct sizing, integration tests | P0 |
| Cross-platform semantic mismatch | High | Capability API and platform docs | P1 |
| False performance claims | High | Benchmark methodology and review | Every release |
| Supply-chain compromise | High | CI permissions, pinned dependencies, checksums/signing | Release |
| Privacy leakage in logs | Medium/High | Data minimization, redaction, export warning | P0 |
