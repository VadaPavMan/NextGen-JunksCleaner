#ifndef JUNKS_CLEANER_JC_API_H
#define JUNKS_CLEANER_JC_API_H

#include "jc_export.h"
#include "jc_types.h"
#include "jc_version.h"

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Retrieve the C ABI version supported by this native library.
 *
 * @param out_version Pointer to jc_version_info_t. Caller must initialize
 *                    struct_size to sizeof(jc_version_info_t).
 * @return JC_OK on success, JC_ERROR_INVALID_ARGUMENT if out_version is NULL
 *         or struct_size does not match.
 */
JC_API jc_status_t jc_get_abi_version(jc_version_info_t* out_version);

/**
 * Retrieve the implementation library version of this native library.
 *
 * @param out_version Pointer to jc_version_info_t. Caller must initialize
 *                    struct_size to sizeof(jc_version_info_t).
 * @return JC_OK on success, JC_ERROR_INVALID_ARGUMENT if out_version is NULL
 *         or struct_size does not match.
 */
JC_API jc_status_t jc_get_library_version(jc_version_info_t* out_version);

/**
 * Query host OS, architecture, and feature capabilities supported by this build.
 *
 * @param out_caps Pointer to jc_capabilities_t. Caller must initialize
 *                 struct_size to sizeof(jc_capabilities_t) and
 *                 abi_version to JC_CURRENT_ABI_VERSION.
 * @return JC_OK on success, JC_ERROR_INVALID_ARGUMENT on bad pointer or struct_size,
 *         or JC_ERROR_ABI_MISMATCH if abi_version is not supported.
 */
JC_API jc_status_t jc_get_capabilities(jc_capabilities_t* out_caps);

/**
 * Capture a real-time system resource snapshot (CPU, memory, disk, and process counts).
 *
 * @param out_snapshot Pointer to jc_system_snapshot_t. Caller must initialize
 *                     struct_size to sizeof(jc_system_snapshot_t) and
 *                     abi_version to JC_CURRENT_ABI_VERSION.
 * @return JC_OK on success, JC_ERROR_INVALID_ARGUMENT on bad pointer or struct_size,
 *         or JC_ERROR_ABI_MISMATCH if abi_version is not supported.
 */
JC_API jc_status_t jc_get_system_snapshot(jc_system_snapshot_t* out_snapshot);

/**
 * Scan allow-listed cleanup targets to discover disposable candidate files.
 *
 * @param options Scan configuration options.
 * @param out_result Output pointer receiving the allocated jc_scan_result_t*.
 *                   Caller MUST free this result using jc_free_scan_result.
 * @return JC_OK on success, JC_ERROR_INVALID_ARGUMENT on bad arguments.
 */
JC_API jc_status_t jc_scan_cleanup_targets(
    const jc_scan_options_t* options,
    jc_scan_result_t** out_result
);

/**
 * Release memory allocated for a jc_scan_result_t.
 *
 * @param result Pointer to jc_scan_result_t to free. Safe to pass NULL.
 */
JC_API void jc_free_scan_result(jc_scan_result_t* result);

/**
 * Execute cleanup deletion of user-approved candidate items after strict revalidation.
 *
 * @param options Cleanup options containing selected items and optional cancellation token.
 * @param out_report Output pointer receiving execution metrics and deleted bytes report.
 * @return JC_OK on success, JC_ERROR_CANCELLED if aborted early by token,
 *         or JC_ERROR_PARTIAL_SUCCESS if some items failed or were skipped.
 */
JC_API jc_status_t jc_execute_cleanup(
    const jc_cleanup_options_t* options,
    jc_cleanup_report_t* out_report
);

/**
 * Return a static, human-readable string description for a status code.
 *
 * @param status The status enum value.
 * @return A non-null, static, null-terminated string literal.
 */
JC_API const char* jc_status_to_string(jc_status_t status);

#ifdef __cplusplus
}
#endif

#endif /* JUNKS_CLEANER_JC_API_H */
