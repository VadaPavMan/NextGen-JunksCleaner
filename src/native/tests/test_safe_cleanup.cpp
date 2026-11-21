#include "junkscleaner/jc_api.h"
#include <iostream>
#include <fstream>
#include <filesystem>
#include <string>
#include <chrono>
#include <cassert>
#include <cstring>

#define TEST_ASSERT(cond, msg) \
    do { \
        if (!(cond)) { \
            std::cerr << "FAILED: " << msg << " (" << #cond << ") at " << __FILE__ << ":" << __LINE__ << std::endl; \
            return 1; \
        } \
    } while (0)

namespace fs = std::filesystem;

int main() {
    std::cout << "[TEST] Starting Safe Cleanup & Containment Unit Tests..." << std::endl;

    // Create an isolated temporary test directory
    fs::path test_root = fs::temp_directory_path() / ("jc_test_cleanup_" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count()));
    fs::create_directories(test_root / "subdir");

    // Also create a file outside test_root that MUST NEVER be touched
    fs::path external_dir = fs::temp_directory_path() / ("jc_test_ext_" + std::to_string(std::chrono::system_clock::now().time_since_epoch().count()));
    fs::create_directories(external_dir);
    fs::path canary_file = external_dir / "canary_do_not_delete.txt";
    {
        std::ofstream f(canary_file);
        f << "CANARY_DATA_DO_NOT_DELETE";
    }

    // Populate test files inside test_root
    fs::path file1 = test_root / "temp1.tmp";
    fs::path file2 = test_root / "subdir" / "temp2.log";
    fs::path excluded_db = test_root / "cache.db"; // Should be excluded
    {
        std::ofstream f(file1);
        f << "1234567890"; // 10 bytes
    }
    {
        std::ofstream f(file2);
        f << "abcdefghij12345"; // 15 bytes
    }
    {
        std::ofstream f(excluded_db);
        f << "SQLITE_HEADER";
    }

    // Create a symlink pointing to canary_file inside test_root if permissions permit
    fs::path symlink_to_canary = test_root / "symlink_escape.tmp";
    std::error_code sym_ec;
    fs::create_symlink(canary_file, symlink_to_canary, sym_ec);

    std::string test_root_str = test_root.string();

    // 1. Scan the test root
    jc_scan_options_t scan_opts{};
    scan_opts.struct_size = sizeof(jc_scan_options_t);
    scan_opts.abi_version = JC_CURRENT_ABI_VERSION;
    scan_opts.custom_root_override = test_root_str.c_str();
    scan_opts.max_depth = 3;
    scan_opts.min_age_seconds = 0;

    jc_scan_result_t* scan_res = nullptr;
    jc_status_t scan_status = jc_scan_cleanup_targets(&scan_opts, &scan_res);
    TEST_ASSERT(scan_status == JC_OK, "Scan must succeed on valid test root");
    TEST_ASSERT(scan_res != nullptr, "Scan result pointer must not be null");
    TEST_ASSERT(scan_res->item_count == 2, "Must find exactly 2 valid temp files (db and symlink excluded)");
    TEST_ASSERT(scan_res->total_estimated_bytes == 25, "Estimated bytes must equal 10 + 15 = 25");

    std::cout << "  - Scan discovered " << scan_res->item_count << " candidate files (" << scan_res->total_estimated_bytes << " bytes)" << std::endl;

    // 2. Dry run execution
    jc_cleanup_options_t clean_opts{};
    clean_opts.struct_size = sizeof(jc_cleanup_options_t);
    clean_opts.abi_version = JC_CURRENT_ABI_VERSION;
    clean_opts.custom_root_override = test_root_str.c_str();
    clean_opts.item_count = scan_res->item_count;
    clean_opts.items = scan_res->items;
    clean_opts.is_dry_run = 1;

    jc_cleanup_report_t report{};
    report.struct_size = sizeof(jc_cleanup_report_t);
    report.abi_version = JC_CURRENT_ABI_VERSION;

    jc_status_t dry_status = jc_execute_cleanup(&clean_opts, &report);
    TEST_ASSERT(dry_status == JC_OK, "Dry run must return JC_OK");
    TEST_ASSERT(report.deleted_count == 2, "Dry run must report 2 items deleted");
    TEST_ASSERT(report.actual_bytes_deleted == 25, "Dry run must report 25 bytes");
    TEST_ASSERT(fs::exists(file1), "File 1 must still exist after dry run");
    TEST_ASSERT(fs::exists(file2), "File 2 must still exist after dry run");

    std::cout << "  - Dry run verified: no files deleted." << std::endl;

    // 3. Adversarial path traversal attack attempt
    jc_cleanup_item_t malicious_item{};
    std::strncpy(malicious_item.target_id, "user_temp", sizeof(malicious_item.target_id) - 1);
    std::strncpy(malicious_item.relative_path, "../canary_do_not_delete.txt", sizeof(malicious_item.relative_path) - 1);
    malicious_item.size_bytes = 100;

    jc_cleanup_options_t attack_opts{};
    attack_opts.struct_size = sizeof(jc_cleanup_options_t);
    attack_opts.abi_version = JC_CURRENT_ABI_VERSION;
    attack_opts.custom_root_override = test_root_str.c_str();
    attack_opts.item_count = 1;
    attack_opts.items = &malicious_item;
    attack_opts.is_dry_run = 0;

    jc_cleanup_report_t attack_report{};
    attack_report.struct_size = sizeof(jc_cleanup_report_t);
    attack_report.abi_version = JC_CURRENT_ABI_VERSION;

    jc_status_t attack_status = jc_execute_cleanup(&attack_opts, &attack_report);
    TEST_ASSERT(attack_status == JC_ERROR_PARTIAL_SUCCESS, "Skipped attack item must report partial success");
    TEST_ASSERT(attack_report.deleted_count == 0, "Malicious item must NOT be deleted");
    TEST_ASSERT(attack_report.skipped_count == 1, "Malicious item must be skipped");
    TEST_ASSERT(fs::exists(canary_file), "Canary file MUST remain untouched!");
    std::cout << "  - Path traversal attack successfully blocked!" << std::endl;

    // 4. Real deletion execution on approved items
    clean_opts.is_dry_run = 0;
    jc_status_t real_status = jc_execute_cleanup(&clean_opts, &report);
    TEST_ASSERT(real_status == JC_OK, "Real cleanup must return JC_OK");
    TEST_ASSERT(report.deleted_count == 2, "Real cleanup must report 2 deleted");
    TEST_ASSERT(report.actual_bytes_deleted == 25, "Real cleanup must report 25 bytes freed");
    TEST_ASSERT(!fs::exists(file1), "File 1 must be deleted from disk");
    TEST_ASSERT(!fs::exists(file2), "File 2 must be deleted from disk");
    TEST_ASSERT(fs::exists(excluded_db), "Excluded database must still exist");
    TEST_ASSERT(fs::exists(canary_file), "External canary file must remain intact");

    std::cout << "  - Real cleanup verified: target files deleted, external canary preserved." << std::endl;

    // 5. Cooperative cancellation test
    volatile int32_t cancel_flag = 1; // Pre-cancelled
    clean_opts.cancel_token = &cancel_flag;
    jc_status_t cancel_status = jc_execute_cleanup(&clean_opts, &report);
    TEST_ASSERT(cancel_status == JC_ERROR_CANCELLED, "Pre-cancelled token must return JC_ERROR_CANCELLED");
    TEST_ASSERT(report.was_cancelled == 1, "Report must reflect was_cancelled == 1");

    std::cout << "  - Cooperative cancellation verified." << std::endl;

    // Cleanup resources
    jc_free_scan_result(scan_res);
    fs::remove_all(test_root);
    fs::remove_all(external_dir);

    std::cout << "[TEST] All Safe Cleanup & Containment Unit Tests PASSED successfully!" << std::endl;
    return 0;
}
