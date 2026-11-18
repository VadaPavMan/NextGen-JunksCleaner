# Definition of Done

A feature is complete only when all applicable checks pass:

## Product
- [ ] User problem and expected behaviour documented.
- [ ] Unsupported cases clearly defined.
- [ ] User-facing language is accurate.

## Architecture
- [ ] Correct layer owns the behaviour.
- [ ] Platform-specific code is isolated.
- [ ] ABI remains compatible or versioned appropriately.
- [ ] No GUI-thread blocking.

## Safety
- [ ] Inputs validated.
- [ ] Permissions handled.
- [ ] Destructive effects previewed and confirmed.
- [ ] Failure and cancellation are safe.
- [ ] No sensitive data unnecessarily logged.

## Quality
- [ ] Unit tests.
- [ ] Integration tests where relevant.
- [ ] Platform tests where relevant.
- [ ] Formatting/static checks.
- [ ] Build verified on supported configurations.

## Delivery
- [ ] Documentation updated.
- [ ] Changelog updated.
- [ ] Roadmap status updated.
- [ ] Exact verification results reported.
