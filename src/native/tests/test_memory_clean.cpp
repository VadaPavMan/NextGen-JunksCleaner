#include "junkscleaner/jc_api.h"
#include <iostream>
#include <cassert>

#define TEST_ASSERT(cond, msg) \
    do { \
        if (!(cond)) { \
            std::cerr << "FAILED: " << msg << " (" << #cond << ") at " << __FILE__ << ":" << __LINE__ << std::endl; \
            return 1; \
        } \
    } while (0)

int main() {
    std::cout << "[TEST] Starting Memory Cleaner API & Parameter Tests..." << std::endl;

    // 1. Null pointers
    {
        jc_memory_clean_result_t res{};
        res.struct_size = sizeof(jc_memory_clean_result_t);
        res.abi_version = JC_CURRENT_ABI_VERSION;
        jc_status_t status = jc_execute_memory_clean(nullptr, &res);
        TEST_ASSERT(status == JC_ERROR_INVALID_ARGUMENT, "Null params must return JC_ERROR_INVALID_ARGUMENT");
    }
    {
        jc_memory_clean_params_t params{};
        params.struct_size = sizeof(jc_memory_clean_params_t);
        params.abi_version = JC_CURRENT_ABI_VERSION;
        params.operations_mask = JC_MEM_OP_WORKING_SETS;
        jc_status_t status = jc_execute_memory_clean(&params, nullptr);
        TEST_ASSERT(status == JC_ERROR_INVALID_ARGUMENT, "Null result must return JC_ERROR_INVALID_ARGUMENT");
    }

    // 2. Struct size mismatch
    {
        jc_memory_clean_params_t params{};
        params.struct_size = sizeof(jc_memory_clean_params_t) - 4;
        params.abi_version = JC_CURRENT_ABI_VERSION;
        params.operations_mask = JC_MEM_OP_WORKING_SETS;
        jc_memory_clean_result_t res{};
        res.struct_size = sizeof(jc_memory_clean_result_t);
        res.abi_version = JC_CURRENT_ABI_VERSION;
        jc_status_t status = jc_execute_memory_clean(&params, &res);
        TEST_ASSERT(status == JC_ERROR_INVALID_ARGUMENT, "Bad params struct_size must return JC_ERROR_INVALID_ARGUMENT");
    }
    {
        jc_memory_clean_params_t params{};
        params.struct_size = sizeof(jc_memory_clean_params_t);
        params.abi_version = JC_CURRENT_ABI_VERSION;
        params.operations_mask = JC_MEM_OP_WORKING_SETS;
        jc_memory_clean_result_t res{};
        res.struct_size = sizeof(jc_memory_clean_result_t) - 4;
        res.abi_version = JC_CURRENT_ABI_VERSION;
        jc_status_t status = jc_execute_memory_clean(&params, &res);
        TEST_ASSERT(status == JC_ERROR_INVALID_ARGUMENT, "Bad result struct_size must return JC_ERROR_INVALID_ARGUMENT");
    }

    // 3. ABI version mismatch
    {
        jc_memory_clean_params_t params{};
        params.struct_size = sizeof(jc_memory_clean_params_t);
        params.abi_version = 0xdeadbeef;
        params.operations_mask = JC_MEM_OP_WORKING_SETS;
        jc_memory_clean_result_t res{};
        res.struct_size = sizeof(jc_memory_clean_result_t);
        res.abi_version = JC_CURRENT_ABI_VERSION;
        jc_status_t status = jc_execute_memory_clean(&params, &res);
        TEST_ASSERT(status == JC_ERROR_ABI_MISMATCH, "Mismatched ABI version must return JC_ERROR_ABI_MISMATCH");
    }

    // 4. Empty operation mask
    {
        jc_memory_clean_params_t params{};
        params.struct_size = sizeof(jc_memory_clean_params_t);
        params.abi_version = JC_CURRENT_ABI_VERSION;
        params.operations_mask = JC_MEM_OP_NONE;
        jc_memory_clean_result_t res{};
        res.struct_size = sizeof(jc_memory_clean_result_t);
        res.abi_version = JC_CURRENT_ABI_VERSION;
        jc_status_t status = jc_execute_memory_clean(&params, &res);
        TEST_ASSERT(status == JC_ERROR_INVALID_ARGUMENT, "Empty operation mask must return JC_ERROR_INVALID_ARGUMENT");
    }

    // 5. Valid memory operation per platform
#if defined(_WIN32)
    {
        jc_memory_clean_params_t params{};
        params.struct_size = sizeof(jc_memory_clean_params_t);
        params.abi_version = JC_CURRENT_ABI_VERSION;
        params.operations_mask = JC_MEM_OP_WORKING_SETS;

        jc_memory_clean_result_t res{};
        res.struct_size = sizeof(jc_memory_clean_result_t);
        res.abi_version = JC_CURRENT_ABI_VERSION;

        jc_status_t status = jc_execute_memory_clean(&params, &res);
        TEST_ASSERT(status == JC_OK || status == JC_ERROR_PARTIAL_SUCCESS, "Working set clean should succeed or return partial success");
        TEST_ASSERT((res.operations_attempted & JC_MEM_OP_WORKING_SETS) != 0, "Operation attempted must include JC_MEM_OP_WORKING_SETS");
        TEST_ASSERT(res.before_used_bytes > 0, "Before memory usage must be recorded");
        TEST_ASSERT(res.after_used_bytes > 0, "After memory usage must be recorded");
        TEST_ASSERT(res.processes_trimmed > 0, "At least one process working set must be trimmed");

        std::cout << "  - Memory Before: " << (res.before_used_bytes / (1024 * 1024)) << " MB" << std::endl;
        std::cout << "  - Memory After:  " << (res.after_used_bytes / (1024 * 1024)) << " MB" << std::endl;
        std::cout << "  - Processes Trimmed: " << res.processes_trimmed << " (Failed: " << res.processes_failed << ")" << std::endl;
        std::cout << "  - Reclaimed: " << (res.bytes_reclaimed / (1024 * 1024)) << " MB" << std::endl;
    }

    // 6. Multi-target memory operation flags
    {
        jc_memory_clean_params_t params{};
        params.struct_size = sizeof(jc_memory_clean_params_t);
        params.abi_version = JC_CURRENT_ABI_VERSION;
        params.operations_mask = JC_MEM_OP_WORKING_SETS | JC_MEM_OP_MODIFIED_FILE_CACHE | JC_MEM_OP_COMBINED_LIST;

        jc_memory_clean_result_t res{};
        res.struct_size = sizeof(jc_memory_clean_result_t);
        res.abi_version = JC_CURRENT_ABI_VERSION;

        jc_status_t status = jc_execute_memory_clean(&params, &res);
        TEST_ASSERT(status == JC_OK || status == JC_ERROR_PARTIAL_SUCCESS, "Multi-target clean should succeed or return partial success");
        TEST_ASSERT(res.operations_attempted == (JC_MEM_OP_WORKING_SETS | JC_MEM_OP_MODIFIED_FILE_CACHE | JC_MEM_OP_COMBINED_LIST), "Operations attempted must match request");
        std::cout << "  - Multi-target memory clean succeeded (succeeded mask: " << res.operations_succeeded << ")" << std::endl;
    }
#elif defined(__linux__)
    // On Linux, sync/modified list is supported unprivileged
    {
        jc_memory_clean_params_t params{};
        params.struct_size = sizeof(jc_memory_clean_params_t);
        params.abi_version = JC_CURRENT_ABI_VERSION;
        params.operations_mask = JC_MEM_OP_MODIFIED_LIST;

        jc_memory_clean_result_t res{};
        res.struct_size = sizeof(jc_memory_clean_result_t);
        res.abi_version = JC_CURRENT_ABI_VERSION;

        jc_status_t status = jc_execute_memory_clean(&params, &res);
        TEST_ASSERT(status == JC_OK, "sync/modified list should succeed on Linux");
        TEST_ASSERT((res.operations_attempted & JC_MEM_OP_MODIFIED_LIST) != 0, "Operation attempted must include JC_MEM_OP_MODIFIED_LIST");
        TEST_ASSERT(res.before_used_bytes > 0, "Before memory usage must be recorded");
        TEST_ASSERT(res.after_used_bytes > 0, "After memory usage must be recorded");
        std::cout << "  - Linux sync/modified list executed successfully." << std::endl;
    }
    // And working sets should explicitly report unsupported
    {
        jc_memory_clean_params_t params{};
        params.struct_size = sizeof(jc_memory_clean_params_t);
        params.abi_version = JC_CURRENT_ABI_VERSION;
        params.operations_mask = JC_MEM_OP_WORKING_SETS;

        jc_memory_clean_result_t res{};
        res.struct_size = sizeof(jc_memory_clean_result_t);
        res.abi_version = JC_CURRENT_ABI_VERSION;

        jc_status_t status = jc_execute_memory_clean(&params, &res);
        TEST_ASSERT(status == JC_ERROR_UNSUPPORTED, "Working sets must be unsupported on Linux");
        std::cout << "  - Linux working sets explicitly returned JC_ERROR_UNSUPPORTED." << std::endl;
    }
#endif

    std::cout << "[TEST] All Memory Cleaner native tests passed successfully!" << std::endl;
    return 0;
}
