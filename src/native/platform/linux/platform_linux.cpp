#if defined(__linux__)

#include "platform/platform_info.h"
#include <sys/utsname.h>
#include <sstream>

namespace junkscleaner::platform {

HostInfo get_host_info() {
    HostInfo info;
    info.os_family = JC_OS_LINUX;

#if defined(__x86_64__)
    info.architecture = JC_ARCH_X86_64;
#elif defined(__aarch64__)
    info.architecture = JC_ARCH_AARCH64;
#elif defined(__i386__)
    info.architecture = JC_ARCH_X86;
#else
    info.architecture = JC_ARCH_UNKNOWN;
#endif

    info.supported_capabilities = 
        JC_CAP_CPU_MONITORING |
        JC_CAP_MEMORY_MONITORING |
        JC_CAP_DISK_MONITORING |
        JC_CAP_CLEANUP_TEMP_FILES |
        JC_CAP_STORAGE_ANALYZER |
        JC_CAP_PROCESS_MONITORING |
        JC_CAP_DROP_CACHES_OPS;

    // drop_caches requires root/sudo on Linux
    info.elevated_capabilities = JC_CAP_DROP_CACHES_OPS;

    struct utsname uname_data;
    if (uname(&uname_data) == 0) {
        std::ostringstream ss;
        ss << uname_data.sysname << " " << uname_data.release;
        info.os_version_string = ss.str();
    } else {
        info.os_version_string = "Linux";
    }

    return info;
}

} // namespace junkscleaner::platform

#endif // __linux__
