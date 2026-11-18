#pragma once

#include <filesystem>
#include <string>

namespace junkscleaner::safety {

/**
 * Validate that a proposed cleanup root is safe and permitted.
 * Rejects drive roots, user home directories, system folders, etc.
 */
bool is_safe_cleanup_root(const std::filesystem::path& root_path);

/**
 * Check whether a target file path is strictly contained within an approved root.
 * Resolves symlinks/relative segments and validates strict prefix matching.
 */
bool is_contained_within_root(
    const std::filesystem::path& candidate_path,
    const std::filesystem::path& approved_root
);

/**
 * Check if the given path or any of its parent components is a symlink or Windows reparse point.
 */
bool is_symlink_or_reparse_point(const std::filesystem::path& path);

/**
 * Check if a regular file is currently locked/in-use by another process.
 */
bool is_file_locked(const std::filesystem::path& path);

} // namespace junkscleaner::safety
