#include "path_safety.h"
#include <algorithm>
#include <system_error>

#if defined(_WIN32)
#include <windows.h>
#else
#include <unistd.h>
#include <fcntl.h>
#include <cstdlib>
#endif

namespace junkscleaner::safety {

bool is_safe_cleanup_root(const std::filesystem::path& root_path) {
    if (root_path.empty()) {
        return false;
    }

    std::error_code ec;
    auto norm = std::filesystem::weakly_canonical(root_path, ec);
    if (ec) {
        return false;
    }

    // Reject drive roots (e.g. "C:\" or "/")
    if (norm == norm.root_path() || norm.parent_path() == norm) {
        return false;
    }

#if defined(_WIN32)
    // Check Windows system directories
    WCHAR win_dir[MAX_PATH] = {0};
    if (GetWindowsDirectoryW(win_dir, MAX_PATH) > 0) {
        auto win_path = std::filesystem::weakly_canonical(win_dir, ec);
        if (!ec && (norm == win_path || norm == win_path / "System32")) {
            return false;
        }
    }

    // Check User profile root
    const wchar_t* profile = _wgetenv(L"USERPROFILE");
    if (profile) {
        auto prof_path = std::filesystem::weakly_canonical(profile, ec);
        if (!ec) {
            if (norm == prof_path ||
                norm == prof_path / "Desktop" ||
                norm == prof_path / "Documents" ||
                norm == prof_path / "Pictures" ||
                norm == prof_path / "Downloads") {
                return false;
            }
        }
    }
#else
    // Linux forbidden roots
    std::string s = norm.string();
    if (s == "/" || s == "/home" || s == "/root" || s == "/etc" ||
        s == "/bin" || s == "/sbin" || s == "/usr" || s == "/var") {
        return false;
    }
    const char* home = std::getenv("HOME");
    if (home) {
        auto home_path = std::filesystem::weakly_canonical(home, ec);
        if (!ec && (norm == home_path || norm == home_path / "Desktop" || norm == home_path / "Documents")) {
            return false;
        }
    }
#endif

    return true;
}

bool is_contained_within_root(
    const std::filesystem::path& candidate_path,
    const std::filesystem::path& approved_root
) {
    if (candidate_path.empty() || approved_root.empty()) {
        return false;
    }

    std::error_code ec;
    auto norm_root = std::filesystem::weakly_canonical(approved_root, ec);
    if (ec) return false;

    auto norm_cand = std::filesystem::weakly_canonical(candidate_path, ec);
    if (ec) return false;

    // Check lexical relative path
    auto rel = norm_cand.lexically_relative(norm_root);
    if (rel.empty() || rel == "." || rel == "..") {
        return false;
    }

    // If relative path starts with ".." it escapes the root
    auto first_part = rel.begin()->string();
    if (first_part == "..") {
        return false;
    }

    return true;
}

bool is_symlink_or_reparse_point(const std::filesystem::path& path) {
    std::error_code ec;
    auto status = std::filesystem::symlink_status(path, ec);
    if (!ec && std::filesystem::is_symlink(status)) {
        return true;
    }

#if defined(_WIN32)
    DWORD attrs = GetFileAttributesW(path.c_str());
    if (attrs != INVALID_FILE_ATTRIBUTES && (attrs & FILE_ATTRIBUTE_REPARSE_POINT)) {
        return true;
    }
#endif

    return false;
}

bool is_file_locked(const std::filesystem::path& path) {
#if defined(_WIN32)
    HANDLE h = CreateFileW(
        path.c_str(),
        GENERIC_READ | GENERIC_WRITE,
        0, // Exclusive access request
        nullptr,
        OPEN_EXISTING,
        FILE_ATTRIBUTE_NORMAL,
        nullptr
    );
    if (h == INVALID_HANDLE_VALUE) {
        DWORD err = GetLastError();
        if (err == ERROR_SHARING_VIOLATION || err == ERROR_LOCK_VIOLATION || err == ERROR_ACCESS_DENIED) {
            return true;
        }
        return false;
    }
    CloseHandle(h);
    return false;
#else
    int fd = open(path.c_str(), O_RDWR);
    if (fd == -1) {
        return (errno == ETXTBSY || errno == EACCES);
    }
    struct flock fl{};
    fl.l_type = F_WRLCK;
    fl.l_whence = SEEK_SET;
    int res = fcntl(fd, F_SETLK, &fl);
    close(fd);
    return (res == -1 && (errno == EACCES || errno == EAGAIN));
#endif
}

} // namespace junkscleaner::safety
