#if defined(_WIN32)

#include "platform/platform_memory.h"
#include <windows.h>
#include <psapi.h>
#include <tlhelp32.h>
#include <winioctl.h>
#include <cstdint>

namespace junkscleaner::platform {

namespace {

// Undocumented NT types and function pointers for memory management
typedef LONG(NTAPI* NtSetSystemInformationPtr)(
    INT SystemInformationClass,
    PVOID SystemInformation,
    ULONG SystemInformationLength
);

constexpr INT SYSTEM_FILECACHE_INFORMATION = 21;
constexpr INT SYSTEM_MEMORY_LIST_INFORMATION = 80;
constexpr INT SYSTEM_COMBINE_PHYSICAL_MEMORY_INFORMATION = 130;
constexpr INT SYSTEM_REGISTRY_RECONCILIATION_INFORMATION = 155;

enum SYSTEM_MEMORY_LIST_COMMAND {
    MemoryCaptureAccessedBits           = 0,
    MemoryCaptureAndResetAccessedBits   = 1,
    MemoryEmptyWorkingSets              = 2,
    MemoryFlushModifiedList             = 3,
    MemoryPurgeStandbyList              = 4,
    MemoryPurgeLowPriorityStandbyList   = 5,
    MemoryCommandMax                    = 6
};

#ifndef FSCTL_DISCARD_VOLUME_CACHE
#define FSCTL_DISCARD_VOLUME_CACHE 0x00090054
#endif

#ifndef FSCTL_RESET_WRITE_ORDER
#define FSCTL_RESET_WRITE_ORDER 0x000900F8
#endif

#pragma pack(push, 1)
struct MEMORY_COMBINE_INFORMATION_EX {
    HANDLE Handle;
    ULONG_PTR PagesCombined;
    ULONG_PTR Flags;
};

struct SYSTEM_FILECACHE_INFORMATION_64 {
    int64_t CurrentSize;
    int64_t PeakSize;
    int64_t PageFaultCount;
    int64_t MinimumWorkingSet;
    int64_t MaximumWorkingSet;
    int64_t CurrentSizeIncludingTransitionInPages;
    int64_t PeakSizeIncludingTransitionInPages;
    int64_t TransitionRePurposeCount;
    int64_t Flags;
};

struct SYSTEM_FILECACHE_INFORMATION_32 {
    int32_t CurrentSize;
    int32_t PeakSize;
    int32_t PageFaultCount;
    int32_t MinimumWorkingSet;
    int32_t MaximumWorkingSet;
    int32_t CurrentSizeIncludingTransitionInPages;
    int32_t PeakSizeIncludingTransitionInPages;
    int32_t TransitionRePurposeCount;
    int32_t Flags;
};
#pragma pack(pop)

bool enable_token_privilege(LPCWSTR privilege_name) {
    HANDLE token = NULL;
    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_ADJUST_PRIVILEGES | TOKEN_QUERY, &token)) {
        return false;
    }

    LUID luid;
    if (!LookupPrivilegeValueW(NULL, privilege_name, &luid)) {
        CloseHandle(token);
        return false;
    }

    TOKEN_PRIVILEGES tp{};
    tp.PrivilegeCount = 1;
    tp.Privileges[0].Luid = luid;
    tp.Privileges[0].Attributes = SE_PRIVILEGE_ENABLED;

    BOOL res = AdjustTokenPrivileges(token, FALSE, &tp, sizeof(tp), NULL, NULL);
    DWORD err = GetLastError();
    CloseHandle(token);

    return res && (err != ERROR_NOT_ALL_ASSIGNED);
}

NtSetSystemInformationPtr get_nt_set_system_information() {
    HMODULE ntdll = GetModuleHandleW(L"ntdll.dll");
    if (!ntdll) {
        return nullptr;
    }
#if defined(__GNUC__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wcast-function-type"
#endif
    return reinterpret_cast<NtSetSystemInformationPtr>(GetProcAddress(ntdll, "NtSetSystemInformation"));
#if defined(__GNUC__)
#pragma GCC diagnostic pop
#endif
}

} // namespace

bool is_process_elevated() {
    HANDLE token = NULL;
    if (!OpenProcessToken(GetCurrentProcess(), TOKEN_QUERY, &token)) {
        return false;
    }

    TOKEN_ELEVATION elevation{};
    DWORD size = sizeof(elevation);
    BOOL res = GetTokenInformation(token, TokenElevation, &elevation, sizeof(elevation), &size);
    CloseHandle(token);

    return res && (elevation.TokenIsElevated != 0);
}

jc_status_t execute_platform_memory_clean(
    uint32_t operations_mask,
    MemoryCleanDetail& detail
) {
    if (operations_mask == JC_MEM_OP_NONE) {
        return JC_ERROR_INVALID_ARGUMENT;
    }

    detail = MemoryCleanDetail{};
    NtSetSystemInformationPtr pNtSetSystemInfo = get_nt_set_system_information();

    // Enable high-privilege NT security tokens matching WinMemoryCleaner
    enable_token_privilege(L"SeProfileSingleProcessPrivilege");
    enable_token_privilege(L"SeIncreaseQuotaPrivilege");
    enable_token_privilege(L"SeDebugPrivilege");

    // Execution sequence ordered for maximum memory reclamation:
    // 1. Modified File Cache -> 2. Modified Page List -> 3. Standby List ->
    // 4. System File Cache -> 5. Working Sets -> 6. Combined Page List -> 7. Registry Cache

    // ── 1. Modified File Cache (Flush volume write order & file buffers) ──────
    if (operations_mask & JC_MEM_OP_MODIFIED_FILE_CACHE) {
        detail.operations_attempted |= JC_MEM_OP_MODIFIED_FILE_CACHE;
        bool any_succeeded = false;
        WCHAR drive_strings[256]{};
        DWORD len = GetLogicalDriveStringsW(255, drive_strings);

        if (len > 0 && len <= 255) {
            const WCHAR* drive = drive_strings;
            while (*drive) {
                if (GetDriveTypeW(drive) == DRIVE_FIXED) {
                    WCHAR vol_path[16]{};
                    if ((drive[0] >= L'A' && drive[0] <= L'Z') || (drive[0] >= L'a' && drive[0] <= L'z')) {
                        vol_path[0] = L'\\';
                        vol_path[1] = L'\\';
                        vol_path[2] = L'.';
                        vol_path[3] = L'\\';
                        vol_path[4] = drive[0];
                        vol_path[5] = L':';
                        vol_path[6] = L'\0';

                        HANDLE hVol = CreateFileW(
                            vol_path,
                            GENERIC_READ | GENERIC_WRITE,
                            FILE_SHARE_READ | FILE_SHARE_WRITE,
                            NULL,
                            OPEN_EXISTING,
                            FILE_ATTRIBUTE_NORMAL | FILE_FLAG_NO_BUFFERING,
                            NULL
                        );

                        if (hVol != INVALID_HANDLE_VALUE) {
                            DWORD bytes_returned = 0;
                            BYTE buffer[1] = {0};

                            DeviceIoControl(
                                hVol,
                                FSCTL_RESET_WRITE_ORDER,
                                buffer,
                                sizeof(buffer),
                                NULL,
                                0,
                                &bytes_returned,
                                NULL
                            );

                            DeviceIoControl(
                                hVol,
                                FSCTL_DISCARD_VOLUME_CACHE,
                                NULL,
                                0,
                                NULL,
                                0,
                                &bytes_returned,
                                NULL
                            );

                            if (FlushFileBuffers(hVol)) {
                                any_succeeded = true;
                            }
                            CloseHandle(hVol);
                        }
                    }
                }
                drive += wcslen(drive) + 1;
            }
        }

        if (any_succeeded) {
            detail.operations_succeeded |= JC_MEM_OP_MODIFIED_FILE_CACHE;
        } else {
            detail.operations_failed |= JC_MEM_OP_MODIFIED_FILE_CACHE;
        }
    }

    // ── 2. Modified Page List (Flush dirty memory pages to disk / standby) ────
    if (operations_mask & JC_MEM_OP_MODIFIED_LIST) {
        detail.operations_attempted |= JC_MEM_OP_MODIFIED_LIST;
        bool success = false;
        if (pNtSetSystemInfo) {
            SYSTEM_MEMORY_LIST_COMMAND cmd = MemoryFlushModifiedList;
            LONG status = pNtSetSystemInfo(
                SYSTEM_MEMORY_LIST_INFORMATION,
                &cmd,
                sizeof(cmd)
            );
            if (status >= 0) {
                success = true;
            }
        }
        if (success) {
            detail.operations_succeeded |= JC_MEM_OP_MODIFIED_LIST;
        } else {
            detail.operations_failed |= JC_MEM_OP_MODIFIED_LIST;
        }
    }

    // ── 3. Standby List Purge (Full or Low-Priority) ──────────────────────────
    if ((operations_mask & JC_MEM_OP_STANDBY_LIST) || (operations_mask & JC_MEM_OP_STANDBY_LOW_PRIORITY)) {
        uint32_t target_flag = (operations_mask & JC_MEM_OP_STANDBY_LOW_PRIORITY)
                                   ? JC_MEM_OP_STANDBY_LOW_PRIORITY
                                   : JC_MEM_OP_STANDBY_LIST;
        detail.operations_attempted |= target_flag;

        bool success = false;
        if (pNtSetSystemInfo) {
            SYSTEM_MEMORY_LIST_COMMAND cmd = (target_flag == JC_MEM_OP_STANDBY_LOW_PRIORITY)
                                                 ? MemoryPurgeLowPriorityStandbyList
                                                 : MemoryPurgeStandbyList;
            LONG status = pNtSetSystemInfo(
                SYSTEM_MEMORY_LIST_INFORMATION,
                &cmd,
                sizeof(cmd)
            );
            if (status >= 0) {
                success = true;
            }
        }

        if (success) {
            detail.operations_succeeded |= target_flag;
        } else {
            detail.operations_failed |= target_flag;
        }
    }

    // ── 4. System File Cache (NtSetSystemInformation + SetSystemFileCacheSize) 
    if (operations_mask & JC_MEM_OP_SYSTEM_CACHE) {
        detail.operations_attempted |= JC_MEM_OP_SYSTEM_CACHE;
        bool success = false;

        if (pNtSetSystemInfo) {
#if defined(_WIN64)
            SYSTEM_FILECACHE_INFORMATION_64 sfci{};
            sfci.MinimumWorkingSet = -1;
            sfci.MaximumWorkingSet = -1;
            LONG status = pNtSetSystemInfo(SYSTEM_FILECACHE_INFORMATION, &sfci, sizeof(sfci));
            if (status >= 0) {
                success = true;
            }
#else
            SYSTEM_FILECACHE_INFORMATION_32 sfci{};
            sfci.MinimumWorkingSet = static_cast<int32_t>(0x7FFFFFFF);
            sfci.MaximumWorkingSet = static_cast<int32_t>(0x7FFFFFFF);
            LONG status = pNtSetSystemInfo(SYSTEM_FILECACHE_INFORMATION, &sfci, sizeof(sfci));
            if (status >= 0) {
                success = true;
            }
#endif
        }

        if (SetSystemFileCacheSize(static_cast<SIZE_T>(-1), static_cast<SIZE_T>(-1), 0)) {
            success = true;
        }

        if (success) {
            detail.operations_succeeded |= JC_MEM_OP_SYSTEM_CACHE;
        } else {
            detail.operations_failed |= JC_MEM_OP_SYSTEM_CACHE;
        }
    }

    // ── 5. Working Sets (Global NT Trimming + Individual Process Trimming) ────
    if (operations_mask & JC_MEM_OP_WORKING_SETS) {
        detail.operations_attempted |= JC_MEM_OP_WORKING_SETS;
        bool global_success = false;

        // Global working set trim via NtSetSystemInformation (SystemMemoryListInformation, 2)
        if (pNtSetSystemInfo) {
            SYSTEM_MEMORY_LIST_COMMAND cmd = MemoryEmptyWorkingSets;
            LONG status = pNtSetSystemInfo(
                SYSTEM_MEMORY_LIST_INFORMATION,
                &cmd,
                sizeof(cmd)
            );
            if (status >= 0) {
                global_success = true;
            }
        }

        // Iterate running processes with SeDebugPrivilege enabled
        HANDLE snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
        if (snapshot != INVALID_HANDLE_VALUE) {
            PROCESSENTRY32W pe32{};
            pe32.dwSize = sizeof(PROCESSENTRY32W);

            if (Process32FirstW(snapshot, &pe32)) {
                do {
                    DWORD pid = pe32.th32ProcessID;
                    if (pid <= 4) {
                        continue; // Skip System Idle Process (0) and System (4)
                    }

                    HANDLE hProc = OpenProcess(
                        PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA,
                        FALSE,
                        pid
                    );
                    if (!hProc) {
                        hProc = OpenProcess(
                            PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_SET_QUOTA,
                            FALSE,
                            pid
                        );
                    }

                    if (hProc) {
                        if (K32EmptyWorkingSet(hProc)) {
                            detail.processes_trimmed++;
                        } else {
                            detail.processes_failed++;
                        }
                        CloseHandle(hProc);
                    } else {
                        detail.processes_failed++;
                    }
                } while (Process32NextW(snapshot, &pe32));
            }
            CloseHandle(snapshot);
        }

        if (global_success || detail.processes_trimmed > 0) {
            detail.operations_succeeded |= JC_MEM_OP_WORKING_SETS;
        } else {
            detail.operations_failed |= JC_MEM_OP_WORKING_SETS;
        }
    }

    // ── 6. Combined Page List (Deduplicate identical physical memory pages) ───
    if (operations_mask & JC_MEM_OP_COMBINED_LIST) {
        detail.operations_attempted |= JC_MEM_OP_COMBINED_LIST;
        bool success = false;

        if (pNtSetSystemInfo) {
            MEMORY_COMBINE_INFORMATION_EX combine_info{};
            LONG status = pNtSetSystemInfo(
                SYSTEM_COMBINE_PHYSICAL_MEMORY_INFORMATION,
                &combine_info,
                sizeof(combine_info)
            );
            if (status >= 0) {
                success = true;
            }
        }

        if (success) {
            detail.operations_succeeded |= JC_MEM_OP_COMBINED_LIST;
        } else {
            detail.operations_failed |= JC_MEM_OP_COMBINED_LIST;
        }
    }

    // ── 7. Registry Cache (Reconciliation & Hive buffer flush) ───────────────
    if (operations_mask & JC_MEM_OP_REGISTRY_CACHE) {
        detail.operations_attempted |= JC_MEM_OP_REGISTRY_CACHE;
        bool success = false;

        if (pNtSetSystemInfo) {
            LONG status = pNtSetSystemInfo(
                SYSTEM_REGISTRY_RECONCILIATION_INFORMATION,
                NULL,
                0
            );
            if (status >= 0) {
                success = true;
            }
        }

        if (success) {
            detail.operations_succeeded |= JC_MEM_OP_REGISTRY_CACHE;
        } else {
            detail.operations_failed |= JC_MEM_OP_REGISTRY_CACHE;
        }
    }

    // ── 8. Trim calling application's own working set ────────────────────────
    SetProcessWorkingSetSize(GetCurrentProcess(), static_cast<SIZE_T>(-1), static_cast<SIZE_T>(-1));

    // Determine aggregate status
    if (detail.operations_succeeded == detail.operations_attempted) {
        return JC_OK;
    }
    if (detail.operations_succeeded > 0) {
        return JC_ERROR_PARTIAL_SUCCESS;
    }

    // If completely failed, check if lack of privilege was the cause
    if (!is_process_elevated()) {
        return JC_ERROR_PERMISSION_DENIED;
    }

    return JC_ERROR_INTERNAL;
}

} // namespace junkscleaner::platform

#endif // _WIN32
