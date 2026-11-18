#include "junkscleaner/jc_api.h"
#include "platform/platform_info.h"

JC_API jc_status_t jc_get_system_snapshot(jc_system_snapshot_t* out_snapshot) {
    if (!out_snapshot) {
        return JC_ERROR_INVALID_ARGUMENT;
    }
    if (out_snapshot->struct_size != sizeof(jc_system_snapshot_t)) {
        return JC_ERROR_INVALID_ARGUMENT;
    }
    if (out_snapshot->abi_version != JC_CURRENT_ABI_VERSION) {
        return JC_ERROR_ABI_MISMATCH;
    }

    try {
        if (!junkscleaner::platform::capture_system_snapshot(out_snapshot)) {
            return JC_ERROR_INTERNAL;
        }
        return JC_OK;
    } catch (...) {
        return JC_ERROR_INTERNAL;
    }
}
