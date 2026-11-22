"""Type definitions and ctypes structures matching jc_types.h."""

import ctypes
from dataclasses import dataclass
from enum import IntEnum, IntFlag

JC_ABI_VERSION_MAJOR: int = 1
JC_ABI_VERSION_MINOR: int = 0
JC_ABI_VERSION_PATCH: int = 0

JC_CURRENT_ABI_VERSION: int = (
    (JC_ABI_VERSION_MAJOR << 24) | (JC_ABI_VERSION_MINOR << 16) | JC_ABI_VERSION_PATCH
)


class JcStatus(IntEnum):
    """Status and error codes matching jc_status_t."""

    OK = 0
    ERROR_INVALID_ARGUMENT = 1
    ERROR_UNSUPPORTED = 2
    ERROR_PERMISSION_DENIED = 3
    ERROR_CANCELLED = 4
    ERROR_PARTIAL_SUCCESS = 5
    ERROR_IO_ERROR = 6
    ERROR_INTERNAL = 7
    ERROR_ABI_MISMATCH = 8
    ERROR_BUFFER_TOO_SMALL = 9


class JcOsFamily(IntEnum):
    """OS family enum matching jc_os_family_t."""

    UNKNOWN = 0
    WINDOWS = 1
    LINUX = 2


class JcArchitecture(IntEnum):
    """Architecture enum matching jc_architecture_t."""

    UNKNOWN = 0
    X86_64 = 1
    AARCH64 = 2
    X86 = 3


class JcCapabilityFlags(IntFlag):
    """Capability flags matching jc_capability_flags_t."""

    NONE = 0
    CPU_MONITORING = 1 << 0
    MEMORY_MONITORING = 1 << 1
    DISK_MONITORING = 1 << 2
    CLEANUP_TEMP_FILES = 1 << 3
    STORAGE_ANALYZER = 1 << 4
    PROCESS_MONITORING = 1 << 5
    STANDBY_LIST_OPS = 1 << 6
    DROP_CACHES_OPS = 1 << 7


class JcSnapshotValidityFlags(IntFlag):
    """Validity bitmask flags for system snapshot fields."""

    NONE = 0
    CPU_USAGE = 1 << 0
    CPU_CORES = 1 << 1
    MEM_TOTAL = 1 << 2
    MEM_USED = 1 << 3
    MEM_AVAILABLE = 1 << 4
    MEM_CACHED = 1 << 5
    MEM_COMMITTED = 1 << 6
    MEM_COMMIT_LIMIT = 1 << 7
    SWAP_TOTAL = 1 << 8
    SWAP_USED = 1 << 9
    PRIMARY_DISK = 1 << 10
    PROCESS_COUNT = 1 << 11
    THREAD_COUNT = 1 << 12


JC_MAX_SNAPSHOT_DISKS: int = 8


def format_bytes(num_bytes: int) -> str:
    """Format bytes into binary prefix string (B, KiB, MiB, GiB, TiB)."""
    if num_bytes < 1024:
        return f"{num_bytes} B"
    units = ["B", "KiB", "MiB", "GiB", "TiB", "PiB"]
    val = float(num_bytes)
    for u in units:
        if val < 1024.0 or u == units[-1]:
            return f"{val:.2f} {u}"
        val /= 1024.0
    return f"{num_bytes} B"


class CTypesDiskInfo(ctypes.Structure):
    """Internal ctypes structure for jc_disk_info_t."""

    _fields_ = [
        ("mount_point", ctypes.c_char * 32),
        ("total_bytes", ctypes.c_uint64),
        ("free_bytes", ctypes.c_uint64),
        ("available_bytes", ctypes.c_uint64),
    ]


class CTypesSystemSnapshot(ctypes.Structure):
    """Internal ctypes structure for jc_system_snapshot_t."""

    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("abi_version", ctypes.c_uint32),
        ("timestamp_ms", ctypes.c_uint64),
        ("validity_flags", ctypes.c_uint64),
        ("cpu_usage_percent", ctypes.c_double),
        ("logical_cpu_cores", ctypes.c_uint32),
        ("physical_cpu_cores", ctypes.c_uint32),
        ("memory_total_bytes", ctypes.c_uint64),
        ("memory_used_bytes", ctypes.c_uint64),
        ("memory_available_bytes", ctypes.c_uint64),
        ("memory_cached_bytes", ctypes.c_uint64),
        ("memory_committed_bytes", ctypes.c_uint64),
        ("memory_commit_limit_bytes", ctypes.c_uint64),
        ("swap_total_bytes", ctypes.c_uint64),
        ("swap_used_bytes", ctypes.c_uint64),
        ("process_count", ctypes.c_uint32),
        ("thread_count", ctypes.c_uint32),
        ("disk_count", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32),
        ("disks", CTypesDiskInfo * JC_MAX_SNAPSHOT_DISKS),
    ]


class CTypesCleanupItem(ctypes.Structure):
    """Internal ctypes structure for jc_cleanup_item_t."""

    _fields_ = [
        ("target_id", ctypes.c_char * 32),
        ("relative_path", ctypes.c_char * 260),
        ("display_path", ctypes.c_char * 260),
        ("size_bytes", ctypes.c_uint64),
        ("last_modified_ms", ctypes.c_uint64),
        ("risk_level", ctypes.c_uint32),
        ("is_locked", ctypes.c_uint32),
    ]


class CTypesScanOptions(ctypes.Structure):
    """Internal ctypes structure for jc_scan_options_t."""

    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("abi_version", ctypes.c_uint32),
        ("custom_root_override", ctypes.c_char_p),
        ("min_age_seconds", ctypes.c_uint32),
        ("max_depth", ctypes.c_uint32),
    ]


class CTypesScanResult(ctypes.Structure):
    """Internal ctypes structure for jc_scan_result_t."""

    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("abi_version", ctypes.c_uint32),
        ("total_candidates_count", ctypes.c_uint64),
        ("total_estimated_bytes", ctypes.c_uint64),
        ("item_count", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32),
        ("items", ctypes.POINTER(CTypesCleanupItem)),
    ]


class CTypesCleanupOptions(ctypes.Structure):
    """Internal ctypes structure for jc_cleanup_options_t."""

    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("abi_version", ctypes.c_uint32),
        ("custom_root_override", ctypes.c_char_p),
        ("item_count", ctypes.c_uint32),
        ("is_dry_run", ctypes.c_uint32),
        ("items", ctypes.POINTER(CTypesCleanupItem)),
        ("cancel_token", ctypes.POINTER(ctypes.c_int32)),
    ]


class CTypesCleanupReport(ctypes.Structure):
    """Internal ctypes structure for jc_cleanup_report_t."""

    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("abi_version", ctypes.c_uint32),
        ("duration_ms", ctypes.c_uint64),
        ("selected_count", ctypes.c_uint64),
        ("deleted_count", ctypes.c_uint64),
        ("skipped_count", ctypes.c_uint64),
        ("failed_count", ctypes.c_uint64),
        ("actual_bytes_deleted", ctypes.c_uint64),
        ("was_cancelled", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32),
    ]


class CTypesVersionInfo(ctypes.Structure):
    """Internal ctypes structure for jc_version_info_t."""

    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("abi_version", ctypes.c_uint32),
        ("major", ctypes.c_uint32),
        ("minor", ctypes.c_uint32),
        ("patch", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32),
    ]


class CTypesCapabilities(ctypes.Structure):
    """Internal ctypes structure for jc_capabilities_t."""

    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("abi_version", ctypes.c_uint32),
        ("os_family", ctypes.c_uint32),
        ("architecture", ctypes.c_uint32),
        ("supported_capabilities", ctypes.c_uint64),
        ("elevated_capabilities", ctypes.c_uint64),
        ("os_version_string", ctypes.c_char * 64),
    ]


@dataclass(frozen=True)
class JcVersionInfo:
    """Idiomatic Python representation of jc_version_info_t."""

    major: int
    minor: int
    patch: int
    abi_version: int

    @property
    def version_string(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True)
class JcCapabilities:
    """Idiomatic Python representation of jc_capabilities_t."""

    os_family: JcOsFamily
    architecture: JcArchitecture
    supported_capabilities: JcCapabilityFlags
    elevated_capabilities: JcCapabilityFlags
    os_version_string: str

    def supports(self, flag: JcCapabilityFlags) -> bool:
        return bool(self.supported_capabilities & flag)

    def requires_elevation(self, flag: JcCapabilityFlags) -> bool:
        return bool(self.elevated_capabilities & flag)


@dataclass(frozen=True)
class JcDiskInfo:
    """Idiomatic representation of jc_disk_info_t."""

    mount_point: str
    total_bytes: int
    free_bytes: int
    available_bytes: int

    @property
    def used_bytes(self) -> int:
        return max(0, self.total_bytes - self.free_bytes)

    @property
    def used_percent(self) -> float:
        if self.total_bytes == 0:
            return 0.0
        return (self.used_bytes * 100.0) / self.total_bytes

    @property
    def total_display(self) -> str:
        return format_bytes(self.total_bytes)

    @property
    def free_display(self) -> str:
        return format_bytes(self.free_bytes)

    @property
    def used_display(self) -> str:
        return format_bytes(self.used_bytes)


@dataclass(frozen=True)
class JcSystemSnapshot:
    """Idiomatic representation of jc_system_snapshot_t."""

    timestamp_ms: int
    validity_flags: JcSnapshotValidityFlags
    cpu_usage_percent: float
    logical_cpu_cores: int
    physical_cpu_cores: int
    memory_total_bytes: int
    memory_used_bytes: int
    memory_available_bytes: int
    memory_cached_bytes: int
    memory_committed_bytes: int
    memory_commit_limit_bytes: int
    swap_total_bytes: int
    swap_used_bytes: int
    process_count: int
    thread_count: int
    disks: list[JcDiskInfo]

    def is_valid(self, flag: JcSnapshotValidityFlags) -> bool:
        return bool(self.validity_flags & flag)

    @property
    def cpu_usage_display(self) -> str:
        if self.is_valid(JcSnapshotValidityFlags.CPU_USAGE):
            return f"{self.cpu_usage_percent:.1f}%"
        return "N/A"

    @property
    def memory_used_percent(self) -> float | None:
        if self.is_valid(JcSnapshotValidityFlags.MEM_TOTAL) and self.memory_total_bytes > 0:
            return (self.memory_used_bytes * 100.0) / self.memory_total_bytes
        return None

    @property
    def memory_used_display(self) -> str:
        if self.is_valid(JcSnapshotValidityFlags.MEM_USED):
            return format_bytes(self.memory_used_bytes)
        return "N/A"

    @property
    def memory_total_display(self) -> str:
        if self.is_valid(JcSnapshotValidityFlags.MEM_TOTAL):
            return format_bytes(self.memory_total_bytes)
        return "N/A"

    @property
    def memory_available_display(self) -> str:
        if self.is_valid(JcSnapshotValidityFlags.MEM_AVAILABLE):
            return format_bytes(self.memory_available_bytes)
        return "N/A"

    @property
    def memory_cached_display(self) -> str:
        if self.is_valid(JcSnapshotValidityFlags.MEM_CACHED):
            return format_bytes(self.memory_cached_bytes)
        return "N/A"


class JcRiskLevel(IntEnum):
    """Cleanup risk classifications matching jc_risk_level_t."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass(frozen=True)
class JcCleanupItem:
    """Discovered disposable cleanup item metadata."""

    target_id: str
    relative_path: str
    display_path: str
    size_bytes: int
    last_modified_ms: int
    risk_level: JcRiskLevel
    is_locked: bool

    @property
    def size_display(self) -> str:
        return format_bytes(self.size_bytes)


@dataclass(frozen=True)
class JcScanResult:
    """Discovered candidate items and aggregated metadata."""

    total_candidates_count: int
    total_estimated_bytes: int
    items: list[JcCleanupItem]

    @property
    def total_estimated_display(self) -> str:
        return format_bytes(self.total_estimated_bytes)


@dataclass(frozen=True)
class JcCleanupReport:
    """Report detailing actual deleted files and bytes freed."""

    duration_ms: int
    selected_count: int
    deleted_count: int
    skipped_count: int
    failed_count: int
    actual_bytes_deleted: int
    was_cancelled: bool

    @property
    def actual_deleted_display(self) -> str:
        return format_bytes(self.actual_bytes_deleted)


class JcMemoryOperationFlags(IntFlag):
    """Memory cleanup operation flags matching jc_memory_operation_flags_t."""

    NONE = 0
    WORKING_SETS = 1 << 0
    SYSTEM_CACHE = 1 << 1
    STANDBY_LIST = 1 << 2
    MODIFIED_LIST = 1 << 3
    COMBINED_LIST = 1 << 4
    REGISTRY_CACHE = 1 << 5
    MODIFIED_FILE_CACHE = 1 << 6
    STANDBY_LOW_PRIORITY = 1 << 7


class CTypesMemoryCleanParams(ctypes.Structure):
    """Internal ctypes structure for jc_memory_clean_params_t."""

    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("abi_version", ctypes.c_uint32),
        ("operations_mask", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32),
    ]


class CTypesMemoryCleanResult(ctypes.Structure):
    """Internal ctypes structure for jc_memory_clean_result_t."""

    _fields_ = [
        ("struct_size", ctypes.c_uint32),
        ("abi_version", ctypes.c_uint32),
        ("before_used_bytes", ctypes.c_uint64),
        ("after_used_bytes", ctypes.c_uint64),
        ("bytes_reclaimed", ctypes.c_uint64),
        ("operations_attempted", ctypes.c_uint32),
        ("operations_succeeded", ctypes.c_uint32),
        ("operations_failed", ctypes.c_uint32),
        ("processes_trimmed", ctypes.c_uint32),
        ("processes_failed", ctypes.c_uint32),
        ("reserved", ctypes.c_uint32),
    ]


@dataclass(frozen=True)
class JcMemoryCleanResult:
    """Idiomatic Python report of memory optimization operations."""

    before_used_bytes: int
    after_used_bytes: int
    bytes_reclaimed: int
    operations_attempted: JcMemoryOperationFlags
    operations_succeeded: JcMemoryOperationFlags
    operations_failed: JcMemoryOperationFlags
    processes_trimmed: int
    processes_failed: int

    @property
    def bytes_reclaimed_display(self) -> str:
        return format_bytes(self.bytes_reclaimed)

    @property
    def before_used_display(self) -> str:
        return format_bytes(self.before_used_bytes)

    @property
    def after_used_display(self) -> str:
        return format_bytes(self.after_used_bytes)

