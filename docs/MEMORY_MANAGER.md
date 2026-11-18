# Memory Manager Specification

## 1. Purpose
Provide accurate memory visibility and a small set of clearly explained, optional maintenance actions. Monitoring is the primary feature; optimization is secondary.

## 2. Metrics
Use platform-specific sources and label them correctly:
- Physical memory total.
- Physical memory used/in use.
- Available memory.
- Cached/standby memory where exposed.
- Committed memory and commit limit where exposed.
- Swap/pagefile use and capacity.
- Per-process working set/resident set when available.

Do not merge unlike metrics into one "RAM used" value without explanation.

## 3. Windows operations
Potential future operations include supported standby-list or working-set-related actions. Each requires API research, minimum OS version, privilege requirements, expected effect, and testing. Prefer documented APIs. Do not copy undocumented Native API calls as a default.

## 4. Linux operations
Monitoring should use kernel-provided memory statistics with documented parsing and fallback. Do not routinely invoke `drop_caches`. It can evict useful page cache and cause additional disk I/O. Any future advanced action must be disabled by default, require confirmation, and clearly explain that it is not a general performance improvement.

## 5. UX language
Use names such as "Available memory", "Cached memory", and "Optimize standby cache" only where semantically correct. Avoid "Boost", "instant speed", "guaranteed FPS", or "battery saver" unless independently demonstrated.

## 6. Measurement
Capture before/after snapshots using the same metric source and sampling method. Show deltas and note that normal OS activity can change results. Never promise a percentage improvement.

## 7. Automation
Automatic memory optimization is deferred. If later introduced, require explicit opt-in, conservative thresholds, cooldowns, minimum interval, event logging, and an easy disable control.
