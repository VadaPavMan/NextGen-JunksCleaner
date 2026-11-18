#include "junkscleaner/jc_api.h"
#include <iostream>
#include <cassert>
#include <cstring>

#define TEST_ASSERT(cond, msg) \
    do { \
        if (!(cond)) { \
            std::cerr << "FAILED: " << msg << " (" << #cond << ") at " << __FILE__ << ":" << __LINE__ << std::endl; \
            return 1; \
        } \
    } while (0)

int main() {
    std::cout << "[TEST] Starting JunksCleaner Native ABI & Capability Tests..." << std::endl;

    // 1. ABI Version with NULL pointer
    {
        jc_status_t status = jc_get_abi_version(nullptr);
        TEST_ASSERT(status == JC_ERROR_INVALID_ARGUMENT, "Null pointer must return JC_ERROR_INVALID_ARGUMENT");
    }

    // 2. ABI Version with invalid struct_size
    {
        jc_version_info_t v{};
        v.struct_size = sizeof(jc_version_info_t) - 4; // intentionally wrong
        jc_status_t status = jc_get_abi_version(&v);
        TEST_ASSERT(status == JC_ERROR_INVALID_ARGUMENT, "Invalid struct_size must return JC_ERROR_INVALID_ARGUMENT");
    }

    // 3. ABI Version with valid parameters
    {
        jc_version_info_t v{};
        v.struct_size = sizeof(jc_version_info_t);
        jc_status_t status = jc_get_abi_version(&v);
        TEST_ASSERT(status == JC_OK, "Valid ABI call must return JC_OK");
        TEST_ASSERT(v.major == JC_ABI_VERSION_MAJOR, "ABI major must match constant");
        TEST_ASSERT(v.minor == JC_ABI_VERSION_MINOR, "ABI minor must match constant");
        TEST_ASSERT(v.patch == JC_ABI_VERSION_PATCH, "ABI patch must match constant");
        TEST_ASSERT(v.abi_version == JC_CURRENT_ABI_VERSION, "Packed ABI version must match constant");
        std::cout << "  - ABI Version Verified: " << v.major << "." << v.minor << "." << v.patch << std::endl;
    }

    // 4. Library Version with valid parameters
    {
        jc_version_info_t v{};
        v.struct_size = sizeof(jc_version_info_t);
        jc_status_t status = jc_get_library_version(&v);
        TEST_ASSERT(status == JC_OK, "Valid library version call must return JC_OK");
        TEST_ASSERT(v.major == JC_LIBRARY_VERSION_MAJOR, "Library major must match constant");
        TEST_ASSERT(v.minor == JC_LIBRARY_VERSION_MINOR, "Library minor must match constant");
        TEST_ASSERT(v.patch == JC_LIBRARY_VERSION_PATCH, "Library patch must match constant");
        std::cout << "  - Library Version Verified: " << v.major << "." << v.minor << "." << v.patch << std::endl;
    }

    // 5. Capabilities with invalid ABI version
    {
        jc_capabilities_t caps{};
        caps.struct_size = sizeof(jc_capabilities_t);
        caps.abi_version = 0x99999999; // intentionally mismatched
        jc_status_t status = jc_get_capabilities(&caps);
        TEST_ASSERT(status == JC_ERROR_ABI_MISMATCH, "Mismatched ABI version must return JC_ERROR_ABI_MISMATCH");
    }

    // 6. Capabilities with valid parameters
    {
        jc_capabilities_t caps{};
        caps.struct_size = sizeof(jc_capabilities_t);
        caps.abi_version = JC_CURRENT_ABI_VERSION;
        jc_status_t status = jc_get_capabilities(&caps);
        TEST_ASSERT(status == JC_OK, "Valid capabilities call must return JC_OK");
#if defined(_WIN32)
        TEST_ASSERT(caps.os_family == JC_OS_WINDOWS, "OS family must be Windows");
#elif defined(__linux__)
        TEST_ASSERT(caps.os_family == JC_OS_LINUX, "OS family must be Linux");
#endif
        TEST_ASSERT(caps.architecture != JC_ARCH_UNKNOWN, "Architecture must be identified");
        TEST_ASSERT(caps.supported_capabilities & JC_CAP_CPU_MONITORING, "CPU monitoring must be supported");
        TEST_ASSERT(caps.supported_capabilities & JC_CAP_MEMORY_MONITORING, "Memory monitoring must be supported");
        TEST_ASSERT(caps.supported_capabilities & JC_CAP_DISK_MONITORING, "Disk monitoring must be supported");
        TEST_ASSERT(caps.supported_capabilities & JC_CAP_CLEANUP_TEMP_FILES, "Temp cleanup must be supported");
        TEST_ASSERT(std::strlen(caps.os_version_string) > 0, "OS version string must not be empty");

        std::cout << "  - OS Family: " << caps.os_family << " (" << caps.os_version_string << ")" << std::endl;
        std::cout << "  - Architecture: " << caps.architecture << std::endl;
        std::cout << "  - Supported Capabilities: 0x" << std::hex << caps.supported_capabilities << std::dec << std::endl;
    }

    // 7. Status string conversion
    {
        const char* ok_str = jc_status_to_string(JC_OK);
        TEST_ASSERT(ok_str != nullptr && std::strcmp(ok_str, "Success") == 0, "JC_OK string mismatch");
        const char* err_str = jc_status_to_string(JC_ERROR_INVALID_ARGUMENT);
        TEST_ASSERT(err_str != nullptr, "JC_ERROR_INVALID_ARGUMENT string cannot be null");
    }

    std::cout << "[TEST] All Native ABI & Capability Tests PASSED successfully!" << std::endl;
    return 0;
}
