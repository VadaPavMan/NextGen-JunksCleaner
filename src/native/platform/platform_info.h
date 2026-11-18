#pragma once

#include "junkscleaner/jc_types.h"
#include <string>

namespace junkscleaner::platform {

struct HostInfo {
    jc_os_family_t os_family{JC_OS_UNKNOWN};
    jc_architecture_t architecture{JC_ARCH_UNKNOWN};
    uint64_t supported_capabilities{JC_CAP_NONE};
    uint64_t elevated_capabilities{JC_CAP_NONE};
    std::string os_version_string;
};

HostInfo get_host_info();

/**
 * Platform-specific system snapshot sampler.
 * Must populate out_snapshot and set appropriate validity_flags.
 * Returns true on success, false on fatal failure.
 */
bool capture_system_snapshot(jc_system_snapshot_t* out_snapshot);

} // namespace junkscleaner::platform
