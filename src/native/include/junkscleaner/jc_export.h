#ifndef JUNKS_CLEANER_JC_EXPORT_H
#define JUNKS_CLEANER_JC_EXPORT_H

#if defined(_WIN32) || defined(__CYGWIN__)
    #if defined(JC_BUILD_SHARED)
        #define JC_EXPORT __declspec(dllexport)
    #elif defined(JC_STATIC)
        #define JC_EXPORT
    #else
        #define JC_EXPORT __declspec(dllimport)
    #endif
#else
    #if defined(__GNUC__) && __GNUC__ >= 4
        #define JC_EXPORT __attribute__((visibility("default")))
    #else
        #define JC_EXPORT
    #endif
#endif

#ifdef __cplusplus
    #define JC_EXTERN_C extern "C"
#else
    #define JC_EXTERN_C
#endif

#define JC_API JC_EXTERN_C JC_EXPORT

#endif /* JUNKS_CLEANER_JC_EXPORT_H */
