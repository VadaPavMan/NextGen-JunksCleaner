# Native C ABI Contract

## 1. Purpose
Define a stable, versioned C ABI consumed by Python. The ABI is a contract; internal C++ implementation may change without breaking callers.

## 2. Rules
- Public headers must compile as both C and C++.
- Export symbols with platform-specific visibility macros.
- Use fixed-width types (`uint32_t`, `uint64_t`, `int32_t`).
- Prefix public symbols and types with `jc_`.
- Every public struct includes `struct_size` and `abi_version` where extensibility is needed.
- No STL, templates, references, C++ classes, `std::string`, or exceptions in public signatures.
- No ownership ambiguity.
- Every returned allocation has a matching release function or caller-provided buffer contract.
- All functions return explicit status codes.
- Validate all input pointers and lengths.
- Catch exceptions inside exported C++ functions.

## 3. Initial API surface (proposal)
- `jc_get_abi_version`
- `jc_get_library_version`
- `jc_get_capabilities`
- `jc_get_system_snapshot`
- `jc_scan_cleanup_targets`
- `jc_free_scan_result`
- `jc_execute_cleanup`
- `jc_cancel_operation`
- `jc_get_last_error_message` or explicit result error payload
- `jc_free_string` only if the API intentionally returns allocated strings

Names and signatures must be reviewed and finalized before implementation. Do not invent parallel APIs in Python.

## 4. Status model
Define stable status codes such as:
`JC_OK`, `JC_INVALID_ARGUMENT`, `JC_UNSUPPORTED`, `JC_PERMISSION_DENIED`, `JC_CANCELLED`, `JC_PARTIAL_SUCCESS`, `JC_IO_ERROR`, `JC_INTERNAL_ERROR`, `JC_ABI_MISMATCH`.

OS-specific numeric error codes may be included as diagnostic metadata.

## 5. Memory ownership
Document whether buffers are caller-owned or library-owned. Prefer caller-provided buffers or opaque result handles with explicit free functions. No pointer may outlive its documented owner.

## 6. Progress and cancellation
Callbacks must include operation ID, stage, completed count, total count if known, and safe message code. Callback may run on a worker thread. Callbacks must not retain caller pointers after return. Cancellation must be thread-safe and cooperative.

## 7. ABI compatibility
Increment ABI major for breaking changes. Additive fields require size/version-aware handling. Python wrapper checks ABI version before invoking operations. Test x64 and ARM64 if supported.
