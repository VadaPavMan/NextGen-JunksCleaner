# Configuration and Logging

## Configuration
Use a versioned local configuration format. JSON is acceptable for the initial implementation. Validate on load; handle missing, malformed, and future-version files safely.

Store configuration in platform-appropriate per-user application data directories. Do not store secrets. Do not require administrator permissions for normal preferences.

Configuration should include only user preferences such as theme, monitoring interval, selected cleanup categories, and opt-in settings. Destructive or advanced options must default off.

## Logging
Use structured local logs with timestamp, severity, component, operation ID, event code, and safe diagnostic context.

Do not log file contents, credentials, browser data, or full sensitive paths by default. Rotate logs and cap storage. Provide a user-controlled export function with a privacy warning.

## Audit history
Record cleanup summary data: target IDs, counts, actual bytes removed, duration, and result. Avoid retaining a complete list of every deleted filename unless the user explicitly requests a detailed report and understands the privacy implications.
