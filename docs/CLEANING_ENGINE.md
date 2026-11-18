# Cleaning Engine Specification

## 1. Purpose
The cleaning engine discovers eligible disposable files, presents a stable preview, and deletes only user-approved items after policy revalidation.

## 2. Pipeline
`Target registry -> discovery -> candidate validation -> metadata aggregation -> preview -> user approval -> revalidation -> deletion -> report`

## 3. Cleanup target definition
Each target should declare:
- stable target ID;
- display name and description;
- supported OS and version constraints;
- approved root resolver;
- filename/path matching policy;
- exclusions;
- risk classification;
- whether application closure is recommended/required;
- permission requirement;
- estimated scan cost;
- cleanup method;
- retention/age policy if relevant;
- documentation link or rationale.

Never hardcode a user's absolute profile path. Resolve per-user locations through supported OS APIs/environment facilities and validate them.

## 4. Risk levels
- Low: known disposable temp files with conservative policy.
- Medium: app cache where regeneration and application state are understood.
- High: anything that could affect user state; disabled by default and requires additional confirmation.
- Prohibited: documents, downloads, browser credentials/cookies/session data, application databases, system-critical files, arbitrary folders.

## 5. Preview model
For each candidate show target, safe display path, size, last modified time, and reason. Avoid opening file contents. Preview must identify files that may be skipped because they are locked or inaccessible.

## 6. Execution
- Revalidate root and file identity before deletion.
- Delete files individually or through safe bounded operations.
- Do not use shell `rm`, `del`, or command strings for core deletion.
- Handle partial failures and continue only where policy permits.
- Cancellation stops new work and safely completes/aborts the current operation.
- Report bytes actually deleted, not merely scanned/selected bytes.

## 7. Reporting
Report selected count, deleted count, skipped count, failed count, actual bytes deleted, duration, and categorized errors. Do not report estimated size as freed space.

## 8. Testing
Use temporary test roots and generated fixtures. Tests must never target real system temp folders or a developer's home directory. Inject filesystem interfaces where practical.
