#if defined(__linux__)

#include "platform/platform_memory.h"
#include <unistd.h>
#include <fcntl.h>
#include <fstream>

namespace junkscleaner::platform {

bool is_process_elevated() {
    return geteuid() == 0;
}

jc_status_t execute_platform_memory_clean(
    uint32_t operations_mask,
    MemoryCleanDetail& detail
) {
    if (operations_mask == JC_MEM_OP_NONE) {
        return JC_ERROR_INVALID_ARGUMENT;
    }

    detail = MemoryCleanDetail{};

    // 1. Process Working Sets: Unsupported on Linux without killing processes
    if (operations_mask & JC_MEM_OP_WORKING_SETS) {
        detail.operations_attempted |= JC_MEM_OP_WORKING_SETS;
        detail.operations_failed |= JC_MEM_OP_WORKING_SETS;
    }

    // 2 & 3. Page Cache / Standby / Inactive Cache: drop_caches (requires root)
    if ((operations_mask & JC_MEM_OP_SYSTEM_CACHE) || (operations_mask & JC_MEM_OP_STANDBY_LIST)) {
        if (operations_mask & JC_MEM_OP_SYSTEM_CACHE) detail.operations_attempted |= JC_MEM_OP_SYSTEM_CACHE;
        if (operations_mask & JC_MEM_OP_STANDBY_LIST) detail.operations_attempted |= JC_MEM_OP_STANDBY_LIST;

        if (geteuid() == 0) {
            sync(); // Flush dirty pages to disk first
            std::ofstream drop_file("/proc/sys/vm/drop_caches");
            if (drop_file.is_open()) {
                drop_file << "3" << std::endl;
                drop_file.close();
                if (operations_mask & JC_MEM_OP_SYSTEM_CACHE) detail.operations_succeeded |= JC_MEM_OP_SYSTEM_CACHE;
                if (operations_mask & JC_MEM_OP_STANDBY_LIST) detail.operations_succeeded |= JC_MEM_OP_STANDBY_LIST;
            } else {
                if (operations_mask & JC_MEM_OP_SYSTEM_CACHE) detail.operations_failed |= JC_MEM_OP_SYSTEM_CACHE;
                if (operations_mask & JC_MEM_OP_STANDBY_LIST) detail.operations_failed |= JC_MEM_OP_STANDBY_LIST;
            }
        } else {
            if (operations_mask & JC_MEM_OP_SYSTEM_CACHE) detail.operations_failed |= JC_MEM_OP_SYSTEM_CACHE;
            if (operations_mask & JC_MEM_OP_STANDBY_LIST) detail.operations_failed |= JC_MEM_OP_STANDBY_LIST;
        }
    }

    // 4. Modified Page List: On Linux sync() flushes dirty pages
    if (operations_mask & JC_MEM_OP_MODIFIED_LIST) {
        detail.operations_attempted |= JC_MEM_OP_MODIFIED_LIST;
        sync();
        detail.operations_succeeded |= JC_MEM_OP_MODIFIED_LIST;
    }

    if (detail.operations_succeeded == detail.operations_attempted) {
        return JC_OK;
    }
    if (detail.operations_succeeded > 0) {
        return JC_ERROR_PARTIAL_SUCCESS;
    }

    // Process working sets is explicitly unsupported on Linux
    if (operations_mask == JC_MEM_OP_WORKING_SETS) {
        return JC_ERROR_UNSUPPORTED;
    }

    if (geteuid() != 0) {
        return JC_ERROR_PERMISSION_DENIED;
    }

    return JC_ERROR_UNSUPPORTED;
}

} // namespace junkscleaner::platform

#endif // __linux__
