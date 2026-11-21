#ifndef JUNKS_CLEANER_PLATFORM_MEMORY_H
#define JUNKS_CLEANER_PLATFORM_MEMORY_H

#include "junkscleaner/jc_types.h"

namespace junkscleaner::platform {

struct MemoryCleanDetail {
    uint32_t operations_attempted{0};
    uint32_t operations_succeeded{0};
    uint32_t operations_failed{0};
    uint32_t processes_trimmed{0};
    uint32_t processes_failed{0};
};

/**
 * Platform-specific implementation for executing memory optimization operations.
 *
 * @param operations_mask Bitmask of jc_memory_operation_flags_t.
 * @param detail Output detail struct tracking per-operation and process success/failure.
 * @return jc_status_t status code representing execution outcome.
 */
jc_status_t execute_platform_memory_clean(
    uint32_t operations_mask,
    MemoryCleanDetail& detail
);

/**
 * Query whether the current process is running with administrative (Windows) or root (Linux) privileges.
 */
bool is_process_elevated();

} // namespace junkscleaner::platform

#endif // JUNKS_CLEANER_PLATFORM_MEMORY_H
