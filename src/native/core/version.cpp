#include "junkscleaner/jc_api.h"
#include "platform/platform_info.h"
#include <algorithm>
#include <cstring>

JC_API jc_status_t jc_get_abi_version(jc_version_info_t* out_version) {
    if (!out_version) {
        return JC_ERROR_INVALID_ARGUMENT;
    }
    if (out_version->struct_size != sizeof(jc_version_info_t)) {
        return JC_ERROR_INVALID_ARGUMENT;
    }
    try {
        out_version->abi_version = JC_CURRENT_ABI_VERSION;
        out_version->major = JC_ABI_VERSION_MAJOR;
        out_version->minor = JC_ABI_VERSION_MINOR;
        out_version->patch = JC_ABI_VERSION_PATCH;
        out_version->reserved = 0;
        return JC_OK;
    } catch (...) {
        return JC_ERROR_INTERNAL;
    }
}

JC_API jc_status_t jc_get_library_version(jc_version_info_t* out_version) {
    if (!out_version) {
        return JC_ERROR_INVALID_ARGUMENT;
    }
    if (out_version->struct_size != sizeof(jc_version_info_t)) {
        return JC_ERROR_INVALID_ARGUMENT;
    }
    try {
        out_version->abi_version = JC_CURRENT_ABI_VERSION;
        out_version->major = JC_LIBRARY_VERSION_MAJOR;
        out_version->minor = JC_LIBRARY_VERSION_MINOR;
        out_version->patch = JC_LIBRARY_VERSION_PATCH;
        out_version->reserved = 0;
        return JC_OK;
    } catch (...) {
        return JC_ERROR_INTERNAL;
    }
}

JC_API jc_status_t jc_get_capabilities(jc_capabilities_t* out_caps) {
    if (!out_caps) {
        return JC_ERROR_INVALID_ARGUMENT;
    }
    if (out_caps->struct_size != sizeof(jc_capabilities_t)) {
        return JC_ERROR_INVALID_ARGUMENT;
    }
    if (out_caps->abi_version != JC_CURRENT_ABI_VERSION) {
        return JC_ERROR_ABI_MISMATCH;
    }
    try {
        auto host = junkscleaner::platform::get_host_info();
        out_caps->os_family = host.os_family;
        out_caps->architecture = host.architecture;
        out_caps->supported_capabilities = host.supported_capabilities;
        out_caps->elevated_capabilities = host.elevated_capabilities;

        std::memset(out_caps->os_version_string, 0, sizeof(out_caps->os_version_string));
        size_t copy_len = std::min(host.os_version_string.size(), sizeof(out_caps->os_version_string) - 1);
        std::memcpy(out_caps->os_version_string, host.os_version_string.data(), copy_len);

        return JC_OK;
    } catch (...) {
        return JC_ERROR_INTERNAL;
    }
}
