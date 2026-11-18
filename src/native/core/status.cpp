#include "junkscleaner/jc_api.h"

JC_API const char* jc_status_to_string(jc_status_t status) {
    switch (status) {
        case JC_OK:
            return "Success";
        case JC_ERROR_INVALID_ARGUMENT:
            return "Invalid argument or null pointer";
        case JC_ERROR_UNSUPPORTED:
            return "Operation unsupported on this platform or configuration";
        case JC_ERROR_PERMISSION_DENIED:
            return "Access or permission denied";
        case JC_ERROR_CANCELLED:
            return "Operation was cancelled by user or timeout";
        case JC_ERROR_PARTIAL_SUCCESS:
            return "Operation completed with partial failures";
        case JC_ERROR_IO_ERROR:
            return "Input/output error";
        case JC_ERROR_INTERNAL:
            return "Internal native core error";
        case JC_ERROR_ABI_MISMATCH:
            return "ABI version mismatch between caller and native library";
        case JC_ERROR_BUFFER_TOO_SMALL:
            return "Provided buffer size is too small";
        default:
            return "Unknown status code";
    }
}
