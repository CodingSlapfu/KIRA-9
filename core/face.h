/* SPDX-License-Identifier: MIT; original KIRA-9 cel portrait. */
#ifndef K9_FACE_H
#define K9_FACE_H
#include "kira.h"
/* Render any horizontal band; caller owns the pixels. No engine mutation or
 * heap. */
void k9_face_render(uint16_t *pixels, unsigned y0, unsigned height,
                    const k9_face *pose);
#endif
