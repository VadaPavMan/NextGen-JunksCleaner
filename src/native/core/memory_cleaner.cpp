#include "junkscleaner/jc_api.h"
#include "platform/platform_memory.h"
#include <exception>

extern "C" {

JC_API jc_status_t jc_execute_memory_clean(
    const jc_memory_clean_params_t* params,
    jc_memory_clean_result_t* out_result
) {
    if (!params || !out_result) {
        return JC_ERROR_INVALID_ARGUMENT;
    }

    if (params->struct_size != sizeof(jc_memory_clean_params_t)) {
        return JC_ERROR_INVALID_ARGUMENT;
    }

    if (params->abi_version != JC_CURRENT_ABI_VERSION) {
        return JC_ERROR_ABI_MISMATCH;
    }

    if (out_result->struct_size != sizeof(jc_memory_clean_result_t)) {
        return JC_ERROR_INVALID_ARGUMENT;
    }

    if (out_result->abi_version != JC_CURRENT_ABI_VERSION) {
        return JC_ERROR_ABI_MISMATCH;
    }

    if (params->operations_mask == JC_MEM_OP_NONE) {
        return JC_ERROR_INVALID_ARGUMENT;
    }

    try {
        // Reset output metrics while keeping struct header
        out_result->before_used_bytes = 0;
        out_result->after_used_bytes = 0;
        out_result->bytes_reclaimed = 0;
        out_result->operations_attempted = 0;
        out_result->operations_succeeded = 0;
        out_result->operations_failed = 0;
        out_result->processes_trimmed = 0;
        out_result->processes_failed = 0;
        out_result->reserved = 0;

        // Capture memory metrics before execution
        jc_system_snapshot_t snap_before{};
        snap_before.struct_size = sizeof(jc_system_snapshot_t);
        snap_before.abi_version = JC_CURRENT_ABI_VERSION;
        if (jc_get_system_snapshot(&snap_before) == JC_OK) {
            out_result->before_used_bytes = snap_before.memory_used_bytes;
        }

        // Execute platform-specific memory operations
        junkscleaner::platform::MemoryCleanDetail detail{};
        jc_status_t status = junkscleaner::platform::execute_platform_memory_clean(
            params->operations_mask,
            detail
        );

        // Capture memory metrics after execution
        jc_system_snapshot_t snap_after{};
        snap_after.struct_size = sizeof(jc_system_snapshot_t);
        snap_after.abi_version = JC_CURRENT_ABI_VERSION;
        if (jc_get_system_snapshot(&snap_after) == JC_OK) {
            out_result->after_used_bytes = snap_after.memory_used_bytes;
        }

        // Calculate bytes reclaimed (safely avoiding underflow)
        if (out_result->before_used_bytes > out_result->after_used_bytes) {
            out_result->bytes_reclaimed = out_result->before_used_bytes - out_result->after_used_bytes;
        } else {
            out_result->bytes_reclaimed = 0;
        }

        out_result->operations_attempted = detail.operations_attempted;
        out_result->operations_succeeded = detail.operations_succeeded;
        out_result->operations_failed = detail.operations_failed;
        out_result->processes_trimmed = detail.processes_trimmed;
        out_result->processes_failed = detail.processes_failed;

        return status;
    } catch (...) {
        return JC_ERROR_INTERNAL;
    }
}

} // extern "C"
