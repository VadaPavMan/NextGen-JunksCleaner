#ifndef JUNKS_CLEANER_JC_TYPES_H
#define JUNKS_CLEANER_JC_TYPES_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

/**
 * Status and error codes returned across the C ABI boundary.
 */
typedef enum jc_status_e {
    JC_OK                       = 0,
    JC_ERROR_INVALID_ARGUMENT   = 1,
    JC_ERROR_UNSUPPORTED        = 2,
    JC_ERROR_PERMISSION_DENIED  = 3,
    JC_ERROR_CANCELLED          = 4,
    JC_ERROR_PARTIAL_SUCCESS    = 5,
    JC_ERROR_IO_ERROR           = 6,
    JC_ERROR_INTERNAL           = 7,
    JC_ERROR_ABI_MISMATCH       = 8,
    JC_ERROR_BUFFER_TOO_SMALL   = 9
} jc_status_t;

/**
 * Operating system family identifier.
 */
typedef enum jc_os_family_e {
    JC_OS_UNKNOWN = 0,
    JC_OS_WINDOWS = 1,
    JC_OS_LINUX   = 2
} jc_os_family_t;

/**
 * Target CPU architecture.
 */
typedef enum jc_architecture_e {
    JC_ARCH_UNKNOWN = 0,
    JC_ARCH_X86_64  = 1,
    JC_ARCH_AARCH64 = 2,
    JC_ARCH_X86     = 3
} jc_architecture_t;

/**
 * Capability bitmask flags.
 */
typedef enum jc_capability_flags_e {
    JC_CAP_NONE                 = 0,
    JC_CAP_CPU_MONITORING       = (1ULL << 0),
    JC_CAP_MEMORY_MONITORING    = (1ULL << 1),
    JC_CAP_DISK_MONITORING      = (1ULL << 2),
    JC_CAP_CLEANUP_TEMP_FILES   = (1ULL << 3),
    JC_CAP_STORAGE_ANALYZER     = (1ULL << 4),
    JC_CAP_PROCESS_MONITORING   = (1ULL << 5),
    JC_CAP_STANDBY_LIST_OPS     = (1ULL << 6),
    JC_CAP_DROP_CACHES_OPS      = (1ULL << 7)
} jc_capability_flags_t;

/**
 * Version information payload.
 */
typedef struct jc_version_info_s {
    uint32_t struct_size;    /* Must be sizeof(jc_version_info_t) */
    uint32_t abi_version;    /* Must match JC_CURRENT_ABI_VERSION */
    uint32_t major;
    uint32_t minor;
    uint32_t patch;
    uint32_t reserved;       /* Alignment padding */
} jc_version_info_t;

/**
 * System and platform capability report.
 */
typedef struct jc_capabilities_s {
    uint32_t struct_size;            /* Must be sizeof(jc_capabilities_t) */
    uint32_t abi_version;            /* Must match JC_CURRENT_ABI_VERSION */
    uint32_t os_family;              /* jc_os_family_t */
    uint32_t architecture;           /* jc_architecture_t */
    uint64_t supported_capabilities; /* Bitmask of supported jc_capability_flags_t */
    uint64_t elevated_capabilities;  /* Bitmask of capabilities requiring elevation */
    char os_version_string[64];      /* Human-readable OS version name (null-terminated) */
} jc_capabilities_t;

/**
 * Validity bitmask flags for system snapshot fields.
 * Distinguishes between zero values and unavailable/unsupported metrics.
 */
typedef enum jc_snapshot_validity_flags_e {
    JC_SNAPSHOT_VALID_NONE              = 0,
    JC_SNAPSHOT_VALID_CPU_USAGE         = (1ULL << 0),
    JC_SNAPSHOT_VALID_CPU_CORES         = (1ULL << 1),
    JC_SNAPSHOT_VALID_MEM_TOTAL         = (1ULL << 2),
    JC_SNAPSHOT_VALID_MEM_USED          = (1ULL << 3),
    JC_SNAPSHOT_VALID_MEM_AVAILABLE     = (1ULL << 4),
    JC_SNAPSHOT_VALID_MEM_CACHED        = (1ULL << 5),
    JC_SNAPSHOT_VALID_MEM_COMMITTED     = (1ULL << 6),
    JC_SNAPSHOT_VALID_MEM_COMMIT_LIMIT  = (1ULL << 7),
    JC_SNAPSHOT_VALID_SWAP_TOTAL        = (1ULL << 8),
    JC_SNAPSHOT_VALID_SWAP_USED         = (1ULL << 9),
    JC_SNAPSHOT_VALID_PRIMARY_DISK      = (1ULL << 10),
    JC_SNAPSHOT_VALID_PROCESS_COUNT     = (1ULL << 11),
    JC_SNAPSHOT_VALID_THREAD_COUNT      = (1ULL << 12)
} jc_snapshot_validity_flags_t;

#define JC_MAX_SNAPSHOT_DISKS 8U

/**
 * Disk volume usage snapshot.
 */
typedef struct jc_disk_info_s {
    char mount_point[32];       /* e.g. "C:\" on Windows or "/" on Linux */
    uint64_t total_bytes;
    uint64_t free_bytes;
    uint64_t available_bytes;
} jc_disk_info_t;

/**
 * Real-time system telemetry snapshot.
 */
typedef struct jc_system_snapshot_s {
    uint32_t struct_size;              /* Must be sizeof(jc_system_snapshot_t) */
    uint32_t abi_version;              /* Must match JC_CURRENT_ABI_VERSION */
    uint64_t timestamp_ms;             /* Milliseconds since Unix epoch */
    uint64_t validity_flags;           /* Bitmask of jc_snapshot_validity_flags_t */

    /* CPU Metrics */
    double cpu_usage_percent;          /* 0.0 to 100.0 */
    uint32_t logical_cpu_cores;
    uint32_t physical_cpu_cores;

    /* Memory Metrics (bytes) */
    uint64_t memory_total_bytes;
    uint64_t memory_used_bytes;
    uint64_t memory_available_bytes;
    uint64_t memory_cached_bytes;
    uint64_t memory_committed_bytes;
    uint64_t memory_commit_limit_bytes;
    uint64_t swap_total_bytes;
    uint64_t swap_used_bytes;

    /* Process/Thread counts (if exposed) */
    uint32_t process_count;
    uint32_t thread_count;

    /* Primary Disk / Volumes */
    uint32_t disk_count;
    uint32_t reserved;                 /* Alignment padding */
    jc_disk_info_t disks[JC_MAX_SNAPSHOT_DISKS];
} jc_system_snapshot_t;

/**
 * Cleanup target risk classification.
 */
typedef enum jc_risk_level_e {
    JC_RISK_LOW       = 1,   /* Disposable temp files with zero user state */
    JC_RISK_MEDIUM    = 2,   /* App caches with known regeneration semantics */
    JC_RISK_HIGH      = 3    /* Potentially sensitive or requires app restart */
} jc_risk_level_t;

/**
 * Cleanup candidate item metadata.
 */
typedef struct jc_cleanup_item_s {
    char target_id[32];          /* Target identifier (e.g. "user_temp") */
    char relative_path[260];     /* Path relative to target root */
    char display_path[260];      /* Safe display representation */
    uint64_t size_bytes;         /* File size in bytes */
    uint64_t last_modified_ms;   /* Modification time in epoch ms */
    uint32_t risk_level;         /* jc_risk_level_t */
    uint32_t is_locked;          /* 1 if locked or inaccessible, 0 otherwise */
} jc_cleanup_item_t;

/**
 * Scan request parameters.
 */
typedef struct jc_scan_options_s {
    uint32_t struct_size;              /* sizeof(jc_scan_options_t) */
    uint32_t abi_version;              /* JC_CURRENT_ABI_VERSION */
    const char* custom_root_override;  /* Override root for safety testing; NULL for OS default */
    uint32_t min_age_seconds;          /* Minimum file age in seconds; 0 for all */
    uint32_t max_depth;                /* Maximum traversal directory depth (default: 5) */
} jc_scan_options_t;

/**
 * Complete scan result container.
 */
typedef struct jc_scan_result_s {
    uint32_t struct_size;              /* sizeof(jc_scan_result_t) */
    uint32_t abi_version;              /* JC_CURRENT_ABI_VERSION */
    uint64_t total_candidates_count;   /* Count of discovered candidate files */
    uint64_t total_estimated_bytes;    /* Sum of candidate file sizes */
    uint32_t item_count;               /* Number of items in items array */
    uint32_t reserved;                 /* Alignment */
    jc_cleanup_item_t* items;          /* Dynamically allocated array of items */
} jc_scan_result_t;

/**
 * Cleanup execution parameters.
 */
typedef struct jc_cleanup_options_s {
    uint32_t struct_size;              /* sizeof(jc_cleanup_options_t) */
    uint32_t abi_version;              /* JC_CURRENT_ABI_VERSION */
    const char* custom_root_override;  /* Must match approved target root */
    uint32_t item_count;               /* Number of items selected for deletion */
    uint32_t is_dry_run;               /* 1 = simulate without deletion, 0 = delete */
    const jc_cleanup_item_t* items;    /* Items selected by user to delete */
    const volatile int32_t* cancel_token; /* Cooperative cancellation flag pointer; NULL if none */
} jc_cleanup_options_t;

/**
 * Cleanup execution report.
 */
typedef struct jc_cleanup_report_s {
    uint32_t struct_size;              /* sizeof(jc_cleanup_report_t) */
    uint32_t abi_version;              /* JC_CURRENT_ABI_VERSION */
    uint64_t duration_ms;              /* Elapsed execution time in milliseconds */
    uint64_t selected_count;           /* Total items requested */
    uint64_t deleted_count;            /* Successfully removed items */
    uint64_t skipped_count;            /* Skipped (e.g. locked, changed, symlinks) */
    uint64_t failed_count;             /* Attempted but failed with I/O error */
    uint64_t actual_bytes_deleted;     /* Total bytes actually freed from disk */
    uint32_t was_cancelled;            /* 1 if terminated early by cancellation token */
    uint32_t reserved;                 /* Alignment */
} jc_cleanup_report_t;

/**
 * Memory cleanup operation flags.
 */
typedef enum jc_memory_operation_flags_e {
    JC_MEM_OP_NONE             = 0,
    JC_MEM_OP_WORKING_SETS     = (1U << 0), /* Trim working sets of running processes */
    JC_MEM_OP_SYSTEM_CACHE     = (1U << 1), /* Flush system file cache / system working set */
    JC_MEM_OP_STANDBY_LIST     = (1U << 2), /* Purge standby page list */
    JC_MEM_OP_MODIFIED_LIST    = (1U << 3)  /* Flush modified page list to pagefile/disk */
} jc_memory_operation_flags_t;

/**
 * Memory cleanup execution parameters.
 */
typedef struct jc_memory_clean_params_s {
    uint32_t struct_size;          /* Must be sizeof(jc_memory_clean_params_t) */
    uint32_t abi_version;          /* Must match JC_CURRENT_ABI_VERSION */
    uint32_t operations_mask;      /* Bitmask of jc_memory_operation_flags_t */
    uint32_t reserved;             /* Alignment padding */
} jc_memory_clean_params_t;

/**
 * Memory cleanup execution result report.
 */
typedef struct jc_memory_clean_result_s {
    uint32_t struct_size;              /* Must be sizeof(jc_memory_clean_result_t) */
    uint32_t abi_version;              /* Must match JC_CURRENT_ABI_VERSION */
    uint64_t before_used_bytes;        /* Used memory before cleaning */
    uint64_t after_used_bytes;         /* Used memory after cleaning */
    uint64_t bytes_reclaimed;          /* Bytes reclaimed (0 if increased or unchanged) */
    uint32_t operations_attempted;     /* Mask of attempted operations */
    uint32_t operations_succeeded;     /* Mask of succeeded operations */
    uint32_t operations_failed;        /* Mask of failed operations */
    uint32_t processes_trimmed;        /* Count of processes whose working sets were trimmed */
    uint32_t processes_failed;         /* Count of processes that could not be trimmed */
    uint32_t reserved;                 /* Alignment padding */
} jc_memory_clean_result_t;

#ifdef __cplusplus
}
#endif

#endif /* JUNKS_CLEANER_JC_TYPES_H */
