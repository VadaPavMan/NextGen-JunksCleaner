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
