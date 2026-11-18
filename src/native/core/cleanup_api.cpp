#include "junkscleaner/jc_api.h"
#include "cleanup_engine.h"
#include <cstdlib>
#include <cstring>
#include <vector>

JC_API jc_status_t jc_scan_cleanup_targets(
    const jc_scan_options_t* options,
    jc_scan_result_t** out_result
) {
    if (!options || !out_result) {
        return JC_ERROR_INVALID_ARGUMENT;
    }
    if (options->struct_size != sizeof(jc_scan_options_t)) {
        return JC_ERROR_INVALID_ARGUMENT;
    }
    if (options->abi_version != JC_CURRENT_ABI_VERSION) {
        return JC_ERROR_ABI_MISMATCH;
    }

    *out_result = nullptr;

    try {
        std::vector<jc_cleanup_item_t> items;
        uint64_t total_bytes = 0;
        jc_status_t status = junkscleaner::cleanup::scan_target(options, items, total_bytes);
        if (status != JC_OK) {
            return status;
        }

        auto* res = static_cast<jc_scan_result_t*>(std::malloc(sizeof(jc_scan_result_t)));
        if (!res) {
            return JC_ERROR_INTERNAL;
        }

        res->struct_size = sizeof(jc_scan_result_t);
        res->abi_version = JC_CURRENT_ABI_VERSION;
        res->total_candidates_count = items.size();
        res->total_estimated_bytes = total_bytes;
        res->item_count = static_cast<uint32_t>(items.size());
        res->reserved = 0;
        res->items = nullptr;

        if (!items.empty()) {
            size_t items_size = sizeof(jc_cleanup_item_t) * items.size();
            res->items = static_cast<jc_cleanup_item_t*>(std::malloc(items_size));
            if (!res->items) {
                std::free(res);
                return JC_ERROR_INTERNAL;
            }
            std::memcpy(res->items, items.data(), items_size);
        }

        *out_result = res;
        return JC_OK;
    } catch (...) {
        return JC_ERROR_INTERNAL;
    }
}

JC_API void jc_free_scan_result(jc_scan_result_t* result) {
    if (!result) {
        return;
    }
    if (result->items) {
        std::free(result->items);
        result->items = nullptr;
    }
    std::free(result);
}

JC_API jc_status_t jc_execute_cleanup(
    const jc_cleanup_options_t* options,
    jc_cleanup_report_t* out_report
) {
    if (!options || !out_report) {
        return JC_ERROR_INVALID_ARGUMENT;
    }
    if (options->struct_size != sizeof(jc_cleanup_options_t) ||
        out_report->struct_size != sizeof(jc_cleanup_report_t)) {
        return JC_ERROR_INVALID_ARGUMENT;
    }
    if (options->abi_version != JC_CURRENT_ABI_VERSION ||
        out_report->abi_version != JC_CURRENT_ABI_VERSION) {
        return JC_ERROR_ABI_MISMATCH;
    }

    try {
        return junkscleaner::cleanup::execute_cleanup(options, out_report);
    } catch (...) {
        return JC_ERROR_INTERNAL;
    }
}
