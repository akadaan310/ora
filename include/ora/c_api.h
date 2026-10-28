#pragma once
#include <stddef.h>
#include <stdint.h>
#if defined(_WIN32)
#define ORA_EXPORT __declspec(dllexport)
#else
#define ORA_EXPORT __attribute__((visibility("default")))
#endif
#ifdef __cplusplus
extern "C" {
#endif
ORA_EXPORT const char* ora_version(void);
/* Returns bytes required (excluding NUL), writes only if capacity >= required + 1. */
ORA_EXPORT size_t ora_inspect(const char* utf8_text,char* output,size_t capacity);
ORA_EXPORT size_t ora_scene(uint64_t seed,size_t star_count,char* output,size_t capacity);
/* Returns 1 if admitted program, 0 if rejected. No side effects. */
ORA_EXPORT int ora_compile(const char* expression,char* output,size_t capacity);
#ifdef __cplusplus
}
#endif
