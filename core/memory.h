/* SPDX-License-Identifier: MIT; freestanding libc contract, implemented by BSP or host libc. */
#ifndef K9_MEMORY_H
#define K9_MEMORY_H
#include <stddef.h>
void *memset(void *,int,size_t);
void *memcpy(void *,const void *,size_t);
int memcmp(const void *,const void *,size_t);
#endif
