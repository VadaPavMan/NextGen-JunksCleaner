# Antigravity Task Workflow

## Session start
1. Read `AGENTS.md`.
2. Read the relevant product/architecture/security docs.
3. Inspect repository state and recent changes.
4. Identify the current roadmap milestone and unfinished tasks.
5. Ask for clarification only when an ambiguity changes architecture, safety, or user-visible behaviour.

## Task sizing
Prefer one deliverable per task:
- create a C ABI header and ABI version test;
- implement one metrics provider;
- add one cleanup target discovery rule;
- implement preview model;
- add one GUI page backed by an existing service.

Avoid requests such as "finish the whole cleaner" that encourage unreviewable bulk generation.

## Before editing
Provide:
- goal;
- affected files/modules;
- design choice;
- risks;
- tests to add/run.

## After editing
Provide:
- files changed;
- behaviour implemented;
- commands actually run;
- test/build results;
- known gaps;
- docs updated;
- next smallest task.

## Agent restrictions
- Do not create fake implementations or placeholder success responses.
- Do not mark a feature complete when only UI is implemented.
- Do not invent OS API support or platform compatibility.
- Do not delete or overwrite user data.
- Do not run cleanup against host machine directories.
- Do not silently alter this contract.
