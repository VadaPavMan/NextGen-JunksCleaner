#if defined(__linux__)

#include "platform/platform_info.h"
#include <chrono>
#include <cstring>
#include <fstream>
#include <sstream>
#include <string>
#include <mutex>
#include <algorithm>
#include <sys/statvfs.h>
#include <unistd.h>

namespace junkscleaner::platform {

namespace {

static std::mutex s_cpu_mutex;
static uint64_t s_prev_idle = 0;
static uint64_t s_prev_total = 0;
static bool s_has_prev_cpu = false;

struct LinuxCpuTimes {
    uint64_t idle{0};
    uint64_t total{0};
};

bool read_proc_stat(LinuxCpuTimes& times) {
    std::ifstream file("/proc/stat");
    if (!file.is_open()) {
        return false;
    }

    std::string line;
    if (std::getline(file, line)) {
        std::istringstream ss(line);
        std::string cpu_prefix;
        uint64_t user = 0, nice = 0, system = 0, idle = 0;
        uint64_t iowait = 0, irq = 0, softirq = 0, steal = 0;

        if (ss >> cpu_prefix >> user >> nice >> system >> idle >> iowait >> irq >> softirq >> steal) {
            times.idle = idle + iowait;
            times.total = user + nice + system + idle + iowait + irq + softirq + steal;
            return true;
        }
    }
    return false;
}

void sample_cpu(double& cpu_usage, uint32_t& logical_cores, uint64_t& flags) {
    long nprocs = sysconf(_SC_NPROCESSORS_ONLN);
    if (nprocs > 0) {
        logical_cores = static_cast<uint32_t>(nprocs);
        flags |= JC_SNAPSHOT_VALID_CPU_CORES;
    }

    LinuxCpuTimes curr{};
    if (!read_proc_stat(curr)) {
        return;
    }

    std::lock_guard<std::mutex> lock(s_cpu_mutex);
    if (!s_has_prev_cpu) {
        s_prev_idle = curr.idle;
        s_prev_total = curr.total;
        s_has_prev_cpu = true;
        usleep(25000); // 25ms
        if (!read_proc_stat(curr)) {
            return;
        }
    }

    uint64_t delta_idle = (curr.idle >= s_prev_idle) ? (curr.idle - s_prev_idle) : 0;
    uint64_t delta_total = (curr.total >= s_prev_total) ? (curr.total - s_prev_total) : 0;

    s_prev_idle = curr.idle;
    s_prev_total = curr.total;

    if (delta_total > 0 && delta_idle <= delta_total) {
        double busy = static_cast<double>(delta_total - delta_idle);
        double usage = (busy * 100.0) / static_cast<double>(delta_total);
        cpu_usage = std::clamp(usage, 0.0, 100.0);
        flags |= JC_SNAPSHOT_VALID_CPU_USAGE;
    }
}

void sample_memory(jc_system_snapshot_t* out, uint64_t& flags) {
    std::ifstream file("/proc/meminfo");
    if (!file.is_open()) {
        return;
    }

    std::string line;
    uint64_t mem_total_kb = 0, mem_free_kb = 0, mem_available_kb = 0;
    uint64_t buffers_kb = 0, cached_kb = 0;
    uint64_t swap_total_kb = 0, swap_free_kb = 0;
    uint64_t commit_limit_kb = 0, committed_as_kb = 0;

    while (std::getline(file, line)) {
        std::istringstream ss(line);
        std::string key;
        uint64_t val = 0;
        if (ss >> key >> val) {
            if (key == "MemTotal:") mem_total_kb = val;
            else if (key == "MemFree:") mem_free_kb = val;
            else if (key == "MemAvailable:") mem_available_kb = val;
            else if (key == "Buffers:") buffers_kb = val;
            else if (key == "Cached:") cached_kb = val;
            else if (key == "SwapTotal:") swap_total_kb = val;
            else if (key == "SwapFree:") swap_free_kb = val;
            else if (key == "CommitLimit:") commit_limit_kb = val;
            else if (key == "Committed_AS:") committed_as_kb = val;
        }
    }

    if (mem_total_kb > 0) {
        out->memory_total_bytes = mem_total_kb * 1024ULL;
        flags |= JC_SNAPSHOT_VALID_MEM_TOTAL;

        if (mem_available_kb > 0) {
            out->memory_available_bytes = mem_available_kb * 1024ULL;
            out->memory_used_bytes = (out->memory_total_bytes >= out->memory_available_bytes)
                                         ? (out->memory_total_bytes - out->memory_available_bytes)
                                         : 0;
            flags |= JC_SNAPSHOT_VALID_MEM_AVAILABLE | JC_SNAPSHOT_VALID_MEM_USED;
        } else if (mem_free_kb > 0) {
            uint64_t avail_kb = mem_free_kb + buffers_kb + cached_kb;
            out->memory_available_bytes = avail_kb * 1024ULL;
            out->memory_used_bytes = (out->memory_total_bytes >= out->memory_available_bytes)
                                         ? (out->memory_total_bytes - out->memory_available_bytes)
                                         : 0;
            flags |= JC_SNAPSHOT_VALID_MEM_AVAILABLE | JC_SNAPSHOT_VALID_MEM_USED;
        }

        if (cached_kb > 0 || buffers_kb > 0) {
            out->memory_cached_bytes = (cached_kb + buffers_kb) * 1024ULL;
            flags |= JC_SNAPSHOT_VALID_MEM_CACHED;
        }

        if (swap_total_kb > 0) {
            out->swap_total_bytes = swap_total_kb * 1024ULL;
            uint64_t swap_used_kb = (swap_total_kb >= swap_free_kb) ? (swap_total_kb - swap_free_kb) : 0;
            out->swap_used_bytes = swap_used_kb * 1024ULL;
            flags |= JC_SNAPSHOT_VALID_SWAP_TOTAL | JC_SNAPSHOT_VALID_SWAP_USED;
        }

        if (commit_limit_kb > 0 && committed_as_kb > 0) {
            out->memory_commit_limit_bytes = commit_limit_kb * 1024ULL;
            out->memory_committed_bytes = committed_as_kb * 1024ULL;
            flags |= JC_SNAPSHOT_VALID_MEM_COMMIT_LIMIT | JC_SNAPSHOT_VALID_MEM_COMMITTED;
        }
    }
}

void sample_disks(jc_system_snapshot_t* out, uint64_t& flags) {
    struct statvfs stat{};
    if (statvfs("/", &stat) == 0) {
        jc_disk_info_t& d = out->disks[0];
        std::memset(&d, 0, sizeof(d));
        std::strncpy(d.mount_point, "/", sizeof(d.mount_point) - 1);

        uint64_t block_size = stat.f_frsize ? stat.f_frsize : stat.f_bsize;
        d.total_bytes = stat.f_blocks * block_size;
        d.free_bytes = stat.f_bfree * block_size;
        d.available_bytes = stat.f_bavail * block_size;

        out->disk_count = 1;
        flags |= JC_SNAPSHOT_VALID_PRIMARY_DISK;
    }
}

} // namespace

bool capture_system_snapshot(jc_system_snapshot_t* out) {
    if (!out) {
        return false;
    }

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

#endif // __linux__
