#if defined(_WIN32)

#include "platform/platform_info.h"
#include <windows.h>
#include <psapi.h>
#include <chrono>
#include <mutex>
#include <algorithm>
#include <cstring>

namespace junkscleaner::platform {

namespace {

static std::mutex s_cpu_mutex;
static uint64_t s_prev_idle = 0;
static uint64_t s_prev_kernel = 0;
static uint64_t s_prev_user = 0;
static bool s_has_prev_cpu = false;

inline uint64_t filetime_to_uint64(const FILETIME& ft) {
    return (static_cast<uint64_t>(ft.dwHighDateTime) << 32) | ft.dwLowDateTime;
}

void sample_cpu(double& cpu_usage, uint32_t& logical_cores, uint64_t& flags) {
    SYSTEM_INFO sys_info{};
    GetSystemInfo(&sys_info);
    logical_cores = sys_info.dwNumberOfProcessors;
    flags |= JC_SNAPSHOT_VALID_CPU_CORES;

    FILETIME idle_ft{}, kernel_ft{}, user_ft{};
    if (!GetSystemTimes(&idle_ft, &kernel_ft, &user_ft)) {
        return;
    }

    uint64_t curr_idle = filetime_to_uint64(idle_ft);
    uint64_t curr_kernel = filetime_to_uint64(kernel_ft);
    uint64_t curr_user = filetime_to_uint64(user_ft);

    std::lock_guard<std::mutex> lock(s_cpu_mutex);
    if (!s_has_prev_cpu) {
        // First sample: wait 25ms to establish a reliable delta
        s_prev_idle = curr_idle;
        s_prev_kernel = curr_kernel;
        s_prev_user = curr_user;
        s_has_prev_cpu = true;
        Sleep(25);

        if (!GetSystemTimes(&idle_ft, &kernel_ft, &user_ft)) {
            return;
        }
        curr_idle = filetime_to_uint64(idle_ft);
        curr_kernel = filetime_to_uint64(kernel_ft);
        curr_user = filetime_to_uint64(user_ft);
    }

    uint64_t delta_idle = (curr_idle >= s_prev_idle) ? (curr_idle - s_prev_idle) : 0;
    uint64_t delta_kernel = (curr_kernel >= s_prev_kernel) ? (curr_kernel - s_prev_kernel) : 0;
    uint64_t delta_user = (curr_user >= s_prev_user) ? (curr_user - s_prev_user) : 0;

    s_prev_idle = curr_idle;
    s_prev_kernel = curr_kernel;
    s_prev_user = curr_user;

    uint64_t total_sys = delta_kernel + delta_user;
    if (total_sys > 0 && delta_idle <= total_sys) {
        double busy = static_cast<double>(total_sys - delta_idle);
        double usage = (busy * 100.0) / static_cast<double>(total_sys);
        cpu_usage = std::clamp(usage, 0.0, 100.0);
        flags |= JC_SNAPSHOT_VALID_CPU_USAGE;
    }
}

void sample_memory(jc_system_snapshot_t* out, uint64_t& flags) {
    MEMORYSTATUSEX mem_status{};
    mem_status.dwLength = sizeof(mem_status);
    if (GlobalMemoryStatusEx(&mem_status)) {
        out->memory_total_bytes = mem_status.ullTotalPhys;
        out->memory_available_bytes = mem_status.ullAvailPhys;
        out->memory_used_bytes = (mem_status.ullTotalPhys >= mem_status.ullAvailPhys)
                                     ? (mem_status.ullTotalPhys - mem_status.ullAvailPhys)
                                     : 0;
        flags |= JC_SNAPSHOT_VALID_MEM_TOTAL | JC_SNAPSHOT_VALID_MEM_AVAILABLE | JC_SNAPSHOT_VALID_MEM_USED;

        if (mem_status.ullTotalPageFile > mem_status.ullTotalPhys) {
            out->swap_total_bytes = mem_status.ullTotalPageFile - mem_status.ullTotalPhys;
            uint64_t avail_swap = 0;
            if (mem_status.ullAvailPageFile > mem_status.ullAvailPhys) {
                avail_swap = mem_status.ullAvailPageFile - mem_status.ullAvailPhys;
            }
            if (out->swap_total_bytes >= avail_swap) {
                out->swap_used_bytes = out->swap_total_bytes - avail_swap;
                flags |= JC_SNAPSHOT_VALID_SWAP_TOTAL | JC_SNAPSHOT_VALID_SWAP_USED;
            }
        }
    }

    PERFORMANCE_INFORMATION perf_info{};
    perf_info.cb = sizeof(perf_info);
    if (GetPerformanceInfo(&perf_info, sizeof(perf_info))) {
        uint64_t page_size = static_cast<uint64_t>(perf_info.PageSize);
        out->memory_cached_bytes = static_cast<uint64_t>(perf_info.SystemCache) * page_size;
        out->memory_committed_bytes = static_cast<uint64_t>(perf_info.CommitTotal) * page_size;
        out->memory_commit_limit_bytes = static_cast<uint64_t>(perf_info.CommitLimit) * page_size;
        out->process_count = static_cast<uint32_t>(perf_info.ProcessCount);
        out->thread_count = static_cast<uint32_t>(perf_info.ThreadCount);
        flags |= JC_SNAPSHOT_VALID_MEM_CACHED | JC_SNAPSHOT_VALID_MEM_COMMITTED |
                 JC_SNAPSHOT_VALID_MEM_COMMIT_LIMIT | JC_SNAPSHOT_VALID_PROCESS_COUNT |
                 JC_SNAPSHOT_VALID_THREAD_COUNT;
    }
}

void sample_disks(jc_system_snapshot_t* out, uint64_t& flags) {
    WCHAR drive_strings[256]{};
    DWORD len = GetLogicalDriveStringsW(255, drive_strings);
    uint32_t disk_idx = 0;

    if (len > 0 && len <= 255) {
        const WCHAR* drive = drive_strings;
        while (*drive && disk_idx < JC_MAX_SNAPSHOT_DISKS) {
            UINT type = GetDriveTypeW(drive);
            if (type == DRIVE_FIXED || type == DRIVE_REMOVABLE) {
                ULARGE_INTEGER free_bytes_avail{}, total_bytes{}, total_free_bytes{};
                if (GetDiskFreeSpaceExW(drive, &free_bytes_avail, &total_bytes, &total_free_bytes)) {
                    jc_disk_info_t& d = out->disks[disk_idx];
                    std::memset(&d, 0, sizeof(d));

                    int written = WideCharToMultiByte(
                        CP_UTF8, 0, drive, -1, d.mount_point, sizeof(d.mount_point), nullptr, nullptr
                    );
                    if (written > 0) {
                        d.total_bytes = total_bytes.QuadPart;
                        d.free_bytes = total_free_bytes.QuadPart;
                        d.available_bytes = free_bytes_avail.QuadPart;
                        disk_idx++;
                    }
                }
            }
            drive += wcslen(drive) + 1;
        }
    }

    out->disk_count = disk_idx;
    if (disk_idx > 0) {
        flags |= JC_SNAPSHOT_VALID_PRIMARY_DISK;
    }
}

} // namespace

bool capture_system_snapshot(jc_system_snapshot_t* out) {
    if (!out) {
        return false;
    }

    // Capture current timestamp
    auto now = std::chrono::system_clock::now();
    out->timestamp_ms = static_cast<uint64_t>(
        std::chrono::duration_cast<std::chrono::milliseconds>(now.time_since_epoch()).count()
    );

    uint64_t flags = JC_SNAPSHOT_VALID_NONE;

    sample_cpu(out->cpu_usage_percent, out->logical_cpu_cores, flags);
    sample_memory(out, flags);
    sample_disks(out, flags);

    out->validity_flags = flags;
    return true;
}

} // namespace junkscleaner::platform

#endif // _WIN32
