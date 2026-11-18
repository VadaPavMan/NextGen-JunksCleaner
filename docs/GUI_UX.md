# GUI and UX Specification

## 1. Framework
Use PySide6. Keep widgets presentational and move business logic into application services/view models.

## 2. Proposed navigation
- Dashboard
- Junk Cleaner
- Memory
- System Monitor
- Storage
- Activity
- Settings / About

## 3. Dashboard
Show CPU, memory, disk and last cleanup summary. Avoid decorative real-time animations that waste resources. Show metric labels, units, timestamps, and unavailable states.

## 4. Scan and cleanup screens
States: idle, scanning, preview, awaiting confirmation, cleaning, cancelling, completed, partial success, failed.
The preview list must allow category/item deselection. The final confirmation must state what will be deleted and the approximate size.

## 5. Worker model
Use QThread, QtConcurrent, or a carefully chosen worker abstraction. Do not block the GUI thread. Ensure worker shutdown and application exit are deterministic. Do not update widgets directly from native callbacks; relay signals safely.

## 6. Visual and accessibility
- Consistent spacing and typography.
- Keyboard navigation and visible focus.
- High contrast and light/dark themes.
- Accessible names for controls.
- Responsive layouts and high-DPI support.
- Avoid excessive chart refresh rates.
- Respect system locale and number formatting.

## 7. Notifications and tray
Tray integration is a later milestone. Do not add persistent background monitoring by default. Clearly expose whether background monitoring is active.
