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
    std::cout << "[TEST] Starting System Snapshot API Tests..." << std::endl;

    // 1. Null pointer check
    {
        jc_status_t status = jc_get_system_snapshot(nullptr);
        TEST_ASSERT(status == JC_ERROR_INVALID_ARGUMENT, "Null pointer must return JC_ERROR_INVALID_ARGUMENT");
    }

    // 2. Invalid struct_size
    {
        jc_system_snapshot_t snap{};
        snap.struct_size = sizeof(jc_system_snapshot_t) - 8;
        snap.abi_version = JC_CURRENT_ABI_VERSION;
        jc_status_t status = jc_get_system_snapshot(&snap);
        TEST_ASSERT(status == JC_ERROR_INVALID_ARGUMENT, "Invalid struct_size must return JC_ERROR_INVALID_ARGUMENT");
    }

    // 3. Invalid ABI version
    {
        jc_system_snapshot_t snap{};
        snap.struct_size = sizeof(jc_system_snapshot_t);
        snap.abi_version = 0x12345678;
        jc_status_t status = jc_get_system_snapshot(&snap);
        TEST_ASSERT(status == JC_ERROR_ABI_MISMATCH, "Mismatched ABI version must return JC_ERROR_ABI_MISMATCH");
    }

    // 4. Valid snapshot capture
    {
        jc_system_snapshot_t snap{};
        snap.struct_size = sizeof(jc_system_snapshot_t);
        snap.abi_version = JC_CURRENT_ABI_VERSION;
        jc_status_t status = jc_get_system_snapshot(&snap);
        TEST_ASSERT(status == JC_OK, "Valid snapshot call must return JC_OK");

        TEST_ASSERT(snap.timestamp_ms > 0, "Timestamp must be populated");
        TEST_ASSERT(snap.validity_flags != JC_SNAPSHOT_VALID_NONE, "Validity flags must not be empty");

        // CPU Checks
        if (snap.validity_flags & JC_SNAPSHOT_VALID_CPU_CORES) {
            TEST_ASSERT(snap.logical_cpu_cores >= 1, "Must have at least 1 logical core");
            std::cout << "  - Logical CPU Cores: " << snap.logical_cpu_cores << std::endl;
        }
        if (snap.validity_flags & JC_SNAPSHOT_VALID_CPU_USAGE) {
            TEST_ASSERT(snap.cpu_usage_percent >= 0.0 && snap.cpu_usage_percent <= 100.0, "CPU usage must be 0-100%");
            std::cout << "  - CPU Usage: " << snap.cpu_usage_percent << "%" << std::endl;
        }

        // Memory Checks
        TEST_ASSERT(snap.validity_flags & JC_SNAPSHOT_VALID_MEM_TOTAL, "Total memory must be valid");
        TEST_ASSERT(snap.validity_flags & JC_SNAPSHOT_VALID_MEM_AVAILABLE, "Available memory must be valid");
        TEST_ASSERT(snap.validity_flags & JC_SNAPSHOT_VALID_MEM_USED, "Used memory must be valid");

        TEST_ASSERT(snap.memory_total_bytes > 0, "Total RAM must be greater than zero");
        TEST_ASSERT(snap.memory_available_bytes > 0, "Available RAM must be greater than zero");
        TEST_ASSERT(snap.memory_used_bytes > 0, "Used RAM must be greater than zero");

        std::cout << "  - RAM Total: " << (snap.memory_total_bytes / (1024 * 1024)) << " MB" << std::endl;
        std::cout << "  - RAM Used: " << (snap.memory_used_bytes / (1024 * 1024)) << " MB" << std::endl;
        std::cout << "  - RAM Available: " << (snap.memory_available_bytes / (1024 * 1024)) << " MB" << std::endl;

        if (snap.validity_flags & JC_SNAPSHOT_VALID_MEM_CACHED) {
            std::cout << "  - RAM Cached: " << (snap.memory_cached_bytes / (1024 * 1024)) << " MB" << std::endl;
        }
        if (snap.validity_flags & JC_SNAPSHOT_VALID_MEM_COMMITTED) {
            std::cout << "  - Commit Total: " << (snap.memory_committed_bytes / (1024 * 1024)) << " MB" << std::endl;
        }

        // Disk Checks
        TEST_ASSERT(snap.validity_flags & JC_SNAPSHOT_VALID_PRIMARY_DISK, "Primary disk must be valid");
        TEST_ASSERT(snap.disk_count >= 1, "Must detect at least 1 disk");
        for (uint32_t i = 0; i < snap.disk_count; ++i) {
            const auto& d = snap.disks[i];
            TEST_ASSERT(std::strlen(d.mount_point) > 0, "Mount point must not be empty");
            TEST_ASSERT(d.total_bytes > 0, "Disk total bytes must be > 0");
            std::cout << "  - Disk [" << d.mount_point << "]: "
                      << (d.free_bytes / (1024ULL * 1024ULL * 1024ULL)) << " GB free of "
                      << (d.total_bytes / (1024ULL * 1024ULL * 1024ULL)) << " GB" << std::endl;
        }
    }

    std::cout << "[TEST] All System Snapshot API Tests PASSED successfully!" << std::endl;
    return 0;
}
