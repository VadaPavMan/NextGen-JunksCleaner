add_executable(test_abi_version
    test_abi_version.cpp
)
target_link_libraries(test_abi_version PRIVATE junkscleaner_native)
add_test(NAME test_abi_version COMMAND test_abi_version)

add_executable(test_system_snapshot
    test_system_snapshot.cpp
)
target_link_libraries(test_system_snapshot PRIVATE junkscleaner_native)
add_test(NAME test_system_snapshot COMMAND test_system_snapshot)

add_executable(test_safe_cleanup
    test_safe_cleanup.cpp
)
target_link_libraries(test_safe_cleanup PRIVATE junkscleaner_native)
add_test(NAME test_safe_cleanup COMMAND test_safe_cleanup)
