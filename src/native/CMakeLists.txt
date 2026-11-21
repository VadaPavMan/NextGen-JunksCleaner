add_library(junkscleaner_native SHARED
    core/version.cpp
    core/status.cpp
    core/snapshot.cpp
    core/path_safety.cpp
    core/cleanup_engine.cpp
    core/cleanup_api.cpp
    core/memory_cleaner.cpp
)

target_include_directories(junkscleaner_native
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}
)

target_compile_definitions(junkscleaner_native
    PRIVATE
        JC_BUILD_SHARED
)

if(WIN32)
    target_sources(junkscleaner_native PRIVATE
        platform/windows/platform_windows.cpp
        platform/windows/platform_monitor_windows.cpp
        platform/windows/platform_memory_windows.cpp
    )
    target_link_libraries(junkscleaner_native PRIVATE ntdll psapi advapi32)
    if(MINGW)
        target_link_options(junkscleaner_native PRIVATE -static-libgcc -static-libstdc++)
    endif()
elseif(UNIX AND NOT APPLE)
    target_sources(junkscleaner_native PRIVATE
        platform/linux/platform_linux.cpp
        platform/linux/platform_monitor_linux.cpp
        platform/linux/platform_memory_linux.cpp
    )
endif()

set_target_properties(junkscleaner_native PROPERTIES
    VERSION ${PROJECT_VERSION}
    SOVERSION ${PROJECT_VERSION_MAJOR}
    OUTPUT_NAME "junkscleaner_native"
)
