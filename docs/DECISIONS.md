# Architecture Decision Records

Record material decisions here. Newest decisions go first. Use status: Proposed, Accepted, Superseded, or Rejected.

## ADR-0001: Python GUI and native core
- Status: Proposed
- Context: Project requires a desktop GUI and native system operations across Windows/Linux.
- Decision: PySide6 UI with a C-compatible ABI over a C++ implementation.
- Consequences: Clear separation and testability; ABI and packaging complexity must be managed.

## ADR-0002: Unprivileged GUI by default
- Status: Proposed
- Context: Most UI and monitoring should not need elevated privileges.
- Decision: Run the GUI unprivileged. Request narrowly scoped elevation only for operations that require it.
- Consequences: Some features may be unavailable in normal mode; privileged helper design requires separate security review.

## ADR-0003: Preview before destructive cleanup
- Status: Proposed
- Context: Cleanup can destroy user data if target discovery is incorrect.
- Decision: Every destructive cleanup uses scan, preview, explicit approval, and execution-time revalidation.
- Consequences: More user interaction, substantially safer behaviour.

## ADR template
### ADR-NNNN: Title
- Status:
- Date:
- Context:
- Decision:
- Alternatives:
- Security implications:
- Performance implications:
- Compatibility implications:
- Consequences:
