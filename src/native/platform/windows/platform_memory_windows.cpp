#if defined(_WIN32)

#include "platform/platform_memory.h"
#include <windows.h>
#include <psapi.h>
#include <tlhelp32.h>

namespace junkscleaner::platform {

namespace {

// Undocumented NT types for SystemMemoryListInformation
typedef LONG(NTAPI* NtSetSystemInformationPtr)(
    INT SystemInformationClass,
    PVOID SystemInformation,
    ULONG SystemInformationLength
);

enum SYSTEM_MEMORY_LIST_COMMAND {
    MemoryCaptureAccessedBits           = 0,
    MemoryCaptureAndResetAccessedBits   = 1,
    MemoryEmptyWorkingSets              = 2,
    MemoryFlushModifiedList             = 3,
    MemoryPurgeStandbyList              = 4,
    MemoryPurgeLowPriorityStandbyList   = 5,
    MemoryCommandMax                    = 6
};

constexpr INT SYSTEM_MEMORY_LIST_INFORMATION = 80;

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

    // 1. Process Working Sets
    if (operations_mask & JC_MEM_OP_WORKING_SETS) {
        detail.operations_attempted |= JC_MEM_OP_WORKING_SETS;

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

            if (detail.processes_trimmed > 0) {
                detail.operations_succeeded |= JC_MEM_OP_WORKING_SETS;
            } else {
                detail.operations_failed |= JC_MEM_OP_WORKING_SETS;
            }
        } else {
            detail.operations_failed |= JC_MEM_OP_WORKING_SETS;
        }
    }

    // 2. System Working Set / File System Cache
    if (operations_mask & JC_MEM_OP_SYSTEM_CACHE) {
        detail.operations_attempted |= JC_MEM_OP_SYSTEM_CACHE;

        bool has_priv = enable_token_privilege(L"SeIncreaseQuotaPrivilege");
        if (has_priv && SetSystemFileCacheSize(static_cast<SIZE_T>(-1), static_cast<SIZE_T>(-1), 0)) {
            detail.operations_succeeded |= JC_MEM_OP_SYSTEM_CACHE;
        } else {
            detail.operations_failed |= JC_MEM_OP_SYSTEM_CACHE;
        }
    }

    // 3. Standby List Purge
    if (operations_mask & JC_MEM_OP_STANDBY_LIST) {
        detail.operations_attempted |= JC_MEM_OP_STANDBY_LIST;

        bool has_priv = enable_token_privilege(L"SeProfileSingleProcessPrivilege");
        if (has_priv && pNtSetSystemInfo) {
            SYSTEM_MEMORY_LIST_COMMAND cmd = MemoryPurgeStandbyList;
            LONG status = pNtSetSystemInfo(
                SYSTEM_MEMORY_LIST_INFORMATION,
                &cmd,
                sizeof(cmd)
            );
            if (status >= 0) {
                detail.operations_succeeded |= JC_MEM_OP_STANDBY_LIST;
            } else {
                detail.operations_failed |= JC_MEM_OP_STANDBY_LIST;
            }
        } else {
            detail.operations_failed |= JC_MEM_OP_STANDBY_LIST;
        }
    }

    // 4. Modified Page List Flush
    if (operations_mask & JC_MEM_OP_MODIFIED_LIST) {
        detail.operations_attempted |= JC_MEM_OP_MODIFIED_LIST;

        bool has_priv = enable_token_privilege(L"SeProfileSingleProcessPrivilege");
        if (has_priv && pNtSetSystemInfo) {
            SYSTEM_MEMORY_LIST_COMMAND cmd = MemoryFlushModifiedList;
            LONG status = pNtSetSystemInfo(
                SYSTEM_MEMORY_LIST_INFORMATION,
                &cmd,
                sizeof(cmd)
            );
            if (status >= 0) {
                detail.operations_succeeded |= JC_MEM_OP_MODIFIED_LIST;
            } else {
                detail.operations_failed |= JC_MEM_OP_MODIFIED_LIST;
            }
        } else {
            detail.operations_failed |= JC_MEM_OP_MODIFIED_LIST;
        }
    }

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
