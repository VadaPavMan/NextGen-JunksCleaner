#if defined(_WIN32)

#include "platform/platform_info.h"
#include <windows.h>
#include <sstream>

namespace junkscleaner::platform {

typedef LONG(NTAPI* RtlGetVersionPtr)(PRTL_OSVERSIONINFOW);

HostInfo get_host_info() {
    HostInfo info;
    info.os_family = JC_OS_WINDOWS;

#if defined(_M_X64) || defined(__x86_64__)
    info.architecture = JC_ARCH_X86_64;
#elif defined(_M_ARM64) || defined(__aarch64__)
    info.architecture = JC_ARCH_AARCH64;
#elif defined(_M_IX86) || defined(__i386__)
    info.architecture = JC_ARCH_X86;
#else
    info.architecture = JC_ARCH_UNKNOWN;
#endif

    // Capabilities supported on Windows
    info.supported_capabilities = 
        JC_CAP_CPU_MONITORING |
        JC_CAP_MEMORY_MONITORING |
        JC_CAP_DISK_MONITORING |
        JC_CAP_CLEANUP_TEMP_FILES |
        JC_CAP_STORAGE_ANALYZER |
        JC_CAP_PROCESS_MONITORING |
        JC_CAP_STANDBY_LIST_OPS;

    // Operations requiring elevation on Windows
    info.elevated_capabilities = JC_CAP_STANDBY_LIST_OPS;

    // Detect Windows Version
    std::string ver_str = "Windows";
    HMODULE ntdll = GetModuleHandleW(L"ntdll.dll");
    if (ntdll) {
#if defined(__GNUC__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wcast-function-type"
#endif
        auto rtl_get_version = reinterpret_cast<RtlGetVersionPtr>(GetProcAddress(ntdll, "RtlGetVersion"));
#if defined(__GNUC__)
#pragma GCC diagnostic pop
#endif
        if (rtl_get_version) {
            RTL_OSVERSIONINFOW rovi{};
            rovi.dwOSVersionInfoSize = sizeof(rovi);
            if (rtl_get_version(&rovi) == 0) {
                std::ostringstream ss;
                ss << "Windows " << rovi.dwMajorVersion << "." << rovi.dwMinorVersion
                   << " (Build " << rovi.dwBuildNumber << ")";
                ver_str = ss.str();
            }
        }
    }
    info.os_version_string = ver_str;

    return info;
}

} // namespace junkscleaner::platform

#endif // _WIN32
