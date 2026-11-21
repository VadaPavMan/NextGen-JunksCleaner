#include "cleanup_engine.h"
#include "path_safety.h"
#include <chrono>
#include <cstring>
#include <algorithm>

#if defined(_WIN32)
#include <windows.h>
#else
#include <cstdlib>
#endif

namespace junkscleaner::cleanup {

namespace {

bool is_excluded_filename(const std::string& filename) {
    std::string lower = filename;
    std::transform(lower.begin(), lower.end(), lower.begin(), [](unsigned char c) {
        return static_cast<char>(std::tolower(c));
    });

    // Skip databases, active lock files, and session caches
    if (lower.length() >= 3 && lower.substr(lower.length() - 3) == ".db") return true;
    if (lower.length() >= 7 && lower.substr(lower.length() - 7) == ".sqlite") return true;
    if (lower.length() >= 5 && lower.substr(lower.length() - 5) == ".lock") return true;
    if (lower.length() >= 4 && lower.substr(lower.length() - 4) == ".wal") return true;
    return false;
}

std::filesystem::path get_default_user_temp() {
#if defined(_WIN32)
    WCHAR buf[MAX_PATH] = {0};
    DWORD len = GetTempPathW(MAX_PATH, buf);
    if (len > 0 && len < MAX_PATH) {
        return std::filesystem::path(buf);
    }
    const wchar_t* local_app_data = _wgetenv(L"LOCALAPPDATA");
    if (local_app_data) {
        return std::filesystem::path(local_app_data) / "Temp";
    }
    return std::filesystem::path("C:\\Windows\\Temp"); // Fallback
#else
    const char* tmp = std::getenv("TMPDIR");
    if (tmp) return std::filesystem::path(tmp);
    return std::filesystem::path("/tmp");
#endif
}

void scan_directory_recursive(
    const std::filesystem::path& current_dir,
    const std::filesystem::path& approved_root,
    uint32_t current_depth,
    uint32_t max_depth,
    uint32_t min_age_seconds,
    std::vector<jc_cleanup_item_t>& items,
    uint64_t& total_bytes
) {
    if (current_depth > max_depth) {
        return;
    }

    std::error_code ec;
    auto iter = std::filesystem::directory_iterator(
        current_dir,
        std::filesystem::directory_options::skip_permission_denied,
        ec
    );
    if (ec) {
        return;
    }

    auto now = std::chrono::system_clock::now();

    for (const auto& entry : iter) {
        const auto& path = entry.path();

        // Safety: NEVER follow or inspect symlinks/reparse points
        if (safety::is_symlink_or_reparse_point(path)) {
            continue;
        }

        // Safety: Validate strict path containment within root
        if (!safety::is_contained_within_root(path, approved_root)) {
            continue;
        }

        if (entry.is_directory(ec)) {
            scan_directory_recursive(
                path,
                approved_root,
                current_depth + 1,
                max_depth,
                min_age_seconds,
                items,
                total_bytes
            );
        } else if (entry.is_regular_file(ec)) {
            std::string filename = path.filename().string();
            if (is_excluded_filename(filename)) {
                continue;
            }

            // Check age policy if min_age_seconds > 0
            auto lwt = entry.last_write_time(ec);
            if (ec) continue;

            // Convert file_time_type to system_clock
            auto sctp = std::chrono::time_point_cast<std::chrono::system_clock::duration>(
                lwt - std::filesystem::file_time_type::clock::now() + std::chrono::system_clock::now()
            );
            auto age = std::chrono::duration_cast<std::chrono::seconds>(now - sctp).count();
            if (min_age_seconds > 0 && age < static_cast<int64_t>(min_age_seconds)) {
                continue;
            }

            uint64_t fsize = entry.file_size(ec);
            if (ec) continue;

            jc_cleanup_item_t item{};
            std::strncpy(item.target_id, "user_temp", sizeof(item.target_id) - 1);

            std::string rel_str = path.lexically_relative(approved_root).string();
            std::strncpy(item.relative_path, rel_str.c_str(), sizeof(item.relative_path) - 1);

            std::string disp_str = path.filename().string();
            std::strncpy(item.display_path, disp_str.c_str(), sizeof(item.display_path) - 1);

            item.size_bytes = fsize;
            item.last_modified_ms = static_cast<uint64_t>(
                std::chrono::duration_cast<std::chrono::milliseconds>(sctp.time_since_epoch()).count()
            );
            item.risk_level = JC_RISK_LOW;
            item.is_locked = safety::is_file_locked(path) ? 1U : 0U;

            items.push_back(item);
            total_bytes += fsize;
        }
    }
}

} // namespace

std::filesystem::path resolve_target_root(
    const std::string& target_id,
    const char* custom_root_override
) {
    if (custom_root_override && std::strlen(custom_root_override) > 0) {
        std::filesystem::path custom(custom_root_override);
        if (safety::is_safe_cleanup_root(custom)) {
            return custom;
        }
        return {};
    }

    if (target_id == "user_temp") {
        auto def = get_default_user_temp();
        if (safety::is_safe_cleanup_root(def)) {
            return def;
        }
    }

    return {};
}

jc_status_t scan_target(
    const jc_scan_options_t* options,
    std::vector<jc_cleanup_item_t>& out_items,
    uint64_t& out_total_bytes
) {
    const char* root_override = options ? options->custom_root_override : nullptr;
    auto root = resolve_target_root("user_temp", root_override);
    if (root.empty()) {
        return JC_ERROR_INVALID_ARGUMENT;
    }

    std::error_code ec;
    if (!std::filesystem::exists(root, ec) || !std::filesystem::is_directory(root, ec)) {
        return JC_ERROR_IO_ERROR;
    }

    uint32_t max_depth = (options && options->max_depth > 0) ? options->max_depth : 5;
    uint32_t min_age = options ? options->min_age_seconds : 0;

    out_total_bytes = 0;
    scan_directory_recursive(root, root, 1, max_depth, min_age, out_items, out_total_bytes);
    return JC_OK;
}

jc_status_t execute_cleanup(
    const jc_cleanup_options_t* options,
    jc_cleanup_report_t* out_report
) {
    if (!options || !out_report) {
        return JC_ERROR_INVALID_ARGUMENT;
    }

    auto start_time = std::chrono::steady_clock::now();

    out_report->selected_count = options->item_count;
    out_report->deleted_count = 0;
    out_report->skipped_count = 0;
    out_report->failed_count = 0;
    out_report->actual_bytes_deleted = 0;
    out_report->was_cancelled = 0;

    auto root = resolve_target_root("user_temp", options->custom_root_override);
    if (root.empty()) {
        return JC_ERROR_INVALID_ARGUMENT;
    }

    bool was_cancelled = false;
    for (uint32_t i = 0; i < options->item_count; ++i) {
        // Check cooperative cancellation token
        if (options->cancel_token && *options->cancel_token != 0) {
            was_cancelled = true;
            break;
        }

        const auto& item = options->items[i];
        std::string rel_str(item.relative_path);

        // Security check: Reject path traversal in relative path
        if (rel_str.find("..") != std::string::npos) {
            out_report->skipped_count++;
            continue;
        }

        std::filesystem::path full_path = root / rel_str;

        // Security check: Verify strict containment within approved root
        if (!safety::is_contained_within_root(full_path, root)) {
            out_report->skipped_count++;
            continue;
        }

        // Security check: TOCTOU revalidation immediately before deletion
        std::error_code ec;
        if (!std::filesystem::exists(full_path, ec)) {
            out_report->skipped_count++;
            continue;
        }

        // Check if replaced by symlink/reparse point between scan and deletion
        if (safety::is_symlink_or_reparse_point(full_path)) {
            out_report->skipped_count++;
            continue;
        }

        if (!std::filesystem::is_regular_file(std::filesystem::symlink_status(full_path, ec))) {
            out_report->skipped_count++;
            continue;
        }

        if (options->is_dry_run) {
            out_report->deleted_count++;
            out_report->actual_bytes_deleted += item.size_bytes;
        } else {
            if (safety::is_file_locked(full_path)) {
                out_report->skipped_count++;
                continue;
            }

            if (std::filesystem::remove(full_path, ec)) {
                out_report->deleted_count++;
                out_report->actual_bytes_deleted += item.size_bytes;
            } else {
                out_report->failed_count++;
            }
        }
    }

    auto end_time = std::chrono::steady_clock::now();
    out_report->duration_ms = static_cast<uint64_t>(
        std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time).count()
    );

    if (was_cancelled) {
        out_report->was_cancelled = 1;
        return JC_ERROR_CANCELLED;
    }

    if (out_report->failed_count > 0 || out_report->skipped_count > 0) {
        return JC_ERROR_PARTIAL_SUCCESS;
    }

    return JC_OK;
}

} // namespace junkscleaner::cleanup
