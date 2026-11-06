/* SPDX-License-Identifier: MIT; original portrait and mechanical facial rig. */
#include "face.h"
#define RGB(r, g, b)                                                           \
  ((uint16_t)((((r) >> 3) << 11) | (((g) >> 2) << 5) | ((b) >> 3)))
typedef struct {
  int x, y;
} point;
typedef struct {
  uint16_t *p;
  int y, h;
} canvas;
static void pixel(canvas *c, int x, int y, uint16_t color) {
  if ((unsigned)x < 240u && y >= c->y && y < c->y + c->h)
    c->p[(y - c->y) * 240 + x] = color;
}
static void rect(canvas *c, int x, int y, int w, int h, uint16_t color) {
  int xx, yy;
  if (x < 0) {
    w += x;
    x = 0;
  }
  if (x + w > 240)
    w = 240 - x;
  if (y < c->y) {
    h -= c->y - y;
    y = c->y;
  }
  if (y + h > c->y + c->h)
    h = c->y + c->h - y;
  for (yy = y; yy < y + h; yy++)
    for (xx = x; xx < x + w; xx++)
      pixel(c, xx, yy, color);
}
static void line(canvas *c, int x, int y, int xx, int yy, uint16_t color) {
  int dx = xx > x ? xx - x : x - xx, sx = x < xx ? 1 : -1,
      dy = yy > y ? y - yy : yy - y, sy = y < yy ? 1 : -1, error = dx + dy,
      guard = 600;
  while (guard--) {
    int e2 = error * 2;
    pixel(c, x, y, color);
    if (x == xx && y == yy)
      break;
    if (e2 >= dy) {
      error += dy;
      x += sx;
    }
    if (e2 <= dx) {
      error += dx;
      y += sy;
    }
  }
}
static void oval(canvas *c, int cx, int cy, int rx, int ry, uint16_t color) {
  int y, xx;
  if (rx < 1 || ry < 1)
    return;
  for (y = cy - ry; y <= cy + ry; y++) {
    int dy = y - cy, w = rx;
    if (y < c->y || y >= c->y + c->h)
      continue;
    while (w > 0 && w * w * ry * ry + dy * dy * rx * rx > rx * rx * ry * ry)
      w--;
    for (xx = cx - w; xx <= cx + w; xx++)
      pixel(c, xx, y, color);
  }
}
static void poly(canvas *c, const point *p, unsigned n, uint16_t color) {
  int y, min = 240, max = 0;
  unsigned i;
  for (i = 0; i < n; i++) {
    if (p[i].y < min)
      min = p[i].y;
    if (p[i].y > max)
      max = p[i].y;
  }
  if (min < c->y)
    min = c->y;
  if (max >= c->y + c->h)
    max = c->y + c->h - 1;
  for (y = min; y <= max; y++) {
    int hit[20], count = 0;
    for (i = 0; i < n && count < 20; i++) {
      point a = p[i], b = p[(i + 1) % n];
      if ((a.y <= y && b.y > y) || (b.y <= y && a.y > y))
        hit[count++] = a.x + (y - a.y) * (b.x - a.x) / (b.y - a.y);
    }
    for (int j = 1; j < count; j++) {
      int v = hit[j], k = j;
      while (k > 0 && hit[k - 1] > v) {
        hit[k] = hit[k - 1];
        k--;
      }
      hit[k] = v;
    }
    for (int j = 0; j + 1 < count; j += 2)
      rect(c, hit[j], y, hit[j + 1] - hit[j] + 1, 1, color);
  }
}
static void joint(canvas *c, int x, int y, int radius, uint16_t accent) {
  oval(c, x, y, radius, radius, RGB(24, 30, 48));
  oval(c, x, y, radius - 1, radius - 1, RGB(131, 155, 171));
  oval(c, x, y, radius - 3, radius - 3, accent);
  pixel(c, x - 1, y - 1, RGB(244, 245, 230));
}
static void piston(canvas *c, int x, int y, int xx, int yy, uint16_t accent) {
  line(c, x - 1, y, xx - 1, yy, RGB(32, 42, 60));
  line(c, x, y, xx, yy, RGB(118, 145, 165));
  line(c, x + 1, y, xx + 1, yy, RGB(224, 234, 229));
  joint(c, x, y, 4, accent);
  joint(c, xx, yy, 3, accent);
}
void k9_face_render(uint16_t *pixels, unsigned y0, unsigned height,
                    const k9_face *f) {
  canvas c = {pixels, (int)y0, (int)height};
  int i, side;
  uint16_t dark = RGB(18, 21, 38), hair = RGB(37, 31, 62),
           hair_light = RGB(69, 53, 96), skin = RGB(229, 182, 166),
           skin_shadow = RGB(185, 124, 126), cyan = RGB(93, 224, 211),
           copper = RGB(255, 177, 103);
  for (unsigned y = 0; y < height; y++)
    for (unsigned x = 0; x < 240; x++)
      pixels[y * 240 + x] =
          RGB(10 + (int)(y + y0) / 30, 15 + (int)(y + y0) / 28,
              29 + (int)(y + y0) / 20);
  /* Original bob silhouette, neck suspension and shoulders, behind the face. */
  {
    const point p[] = {{23, 71},  {37, 28},   {84, 9},    {148, 7},  {188, 30},
                       {212, 75}, {207, 207}, {173, 233}, {65, 232}, {25, 207}};
    poly(&c, p, 10, hair);
  }
  {
    const point p[] = {{39, 239},  {72, 213},  {96, 204},
                       {144, 204}, {176, 216}, {203, 239}};
    poly(&c, p, 6, RGB(37, 53, 69));
  }
  rect(&c, 99 + f->neck, 177, 43, 63, RGB(61, 76, 94));
  rect(&c, 108 + f->neck, 187, 24, 51, RGB(29, 38, 58));
  for (i = 0; i < 6; i++) {
    line(&c, 108 + f->neck, 199 + i * 6, 131 + f->neck, 196 + i * 6,
         RGB(144, 159, 171));
    line(&c, 110 + f->neck, 201 + i * 6, 129 + f->neck, 198 + i * 6, copper);
  }
  piston(&c, 94, 181, 88 + f->neck, 226, copper);
  piston(&c, 146, 181, 153 + f->neck, 226, cyan);
  /* Facial silhouette, asymmetric cool titanium cheek and warm skin planes. */
  {
    const point p[] = {{58, 66},   {82, 47},   {150, 44},  {179, 70},
                       {183, 122}, {169, 161}, {145, 187}, {120, 201},
                       {96, 190},  {73, 165},  {57, 130},  {53, 93}};
    poly(&c, p, 12, skin_shadow);
  }
  {
    const point p[] = {{62, 65},   {85, 48},   {150, 47},  {175, 73},
                       {178, 119}, {162, 158}, {140, 183}, {120, 194},
                       {99, 182},  {79, 158},  {64, 123},  {59, 92}};
    poly(&c, p, 12, skin);
  }
  {
    const point p[] = {{91, 68},   {146, 60},  {161, 91}, {154, 134},
                       {129, 171}, {103, 164}, {82, 126}};
    poly(&c, p, 7, RGB(239, 195, 174));
  }
  {
    const point p[] = {{59, 123},          {69, 119}, {80, 143 + f->cheek},
                       {83, 169 + f->jaw}, {68, 158}, {59, 140}};
    poly(&c, p, 6, RGB(87, 111, 133));
  }
  {
    const point p[] = {{62, 128},
                       {66, 126},
                       {75, 145 + f->cheek},
                       {76, 158 + f->jaw},
                       {68, 152}};
    poly(&c, p, 5, RGB(168, 189, 194));
  }
  /* Optical assemblies: shaped lashes, iris depth, lids driven by actual blink.
   */
  for (side = -1; side <= 1; side += 2) {
    int x = 120 + side * 38, gaze = f->gaze,
        eyeh = 11 - (int)f->blink * 10 / 255,
        brow = f->cheek == 1   ? -3
               : f->cheek == 2 ? 3
               : f->cheek == 3 ? 1
                               : 0;
    uint16_t iris = side < 0 ? cyan : copper;
    if (eyeh < 1)
      eyeh = 1;
    oval(&c, x, 101, 26, eyeh + 3, skin_shadow);
    oval(&c, x, 103, 25, eyeh, RGB(248, 235, 214));
    oval(&c, x + gaze, 102, 10, eyeh, RGB(37, 68, 79));
    oval(&c, x + gaze, 104, 8, eyeh > 2 ? eyeh - 1 : 1, iris);
    oval(&c, x + gaze, 104, 4, eyeh > 2 ? eyeh - 1 : 1, dark);
    if (eyeh > 4) {
      oval(&c, x + gaze - 3, 100, 3, 3, RGB(255, 253, 238));
      pixel(&c, x + gaze + 4, 108, RGB(255, 252, 220));
    }
    line(&c, x - 25, 103 - eyeh / 3, x - 14, 101 - eyeh, dark);
    line(&c, x - 14, 101 - eyeh, x + 11, 101 - eyeh, dark);
    line(&c, x + 11, 101 - eyeh, x + 25, 103 - eyeh / 3, dark);
    line(&c, x - 22, 102 - eyeh / 3, x - 12, 100 - eyeh, dark);
    line(&c, x - 12, 100 - eyeh, x + 11, 100 - eyeh, dark);
    if (side < 0) {
      line(&c, x - 25, 101, x - 30, 94, dark);
      line(&c, x - 23, 99, x - 26, 92, dark);
    } else {
      line(&c, x + 25, 101, x + 30, 94, dark);
      line(&c, x + 23, 99, x + 26, 92, dark);
    }
    line(&c, x - 20, 82 + brow - side * f->cheek, x + 18,
         80 + brow + side * f->cheek, hair);
    line(&c, x - 18, 83 + brow - side * f->cheek, x + 16,
         81 + brow + side * f->cheek, hair);
    piston(&c, x + side * 29, 86, x + side * 25, 98 + (int)f->blink / 32, iris);
    piston(&c, 120 + side * 57, 125 + f->cheek, 120 + side * 40, 168 + f->jaw,
           iris);
    joint(&c, 120 + side * 50, 143 + f->cheek, 5, iris);
    line(&c, 120 + side * 61, 131, 120 + side * 47, 161 + f->jaw,
         RGB(33, 45, 63));
    if (f->cheek == 1)
      oval(&c, x, 130, 12, 3, RGB(226, 143, 139));
  }
  /* Nose highlights and a real five-way phonetic lip rig. */
  line(&c, 119, 108, 115, 128, skin_shadow);
  line(&c, 115, 128, 121, 131, skin_shadow);
  line(&c, 121, 131, 127, 128, RGB(244, 204, 185));
  {
    int mouth_y = 151 + f->jaw,
        w = f->mouth == 3   ? 9
            : f->mouth == 2 ? 23
                            : 16,
        h = (int)f->open / 3,
        smile = f->cheek == 1   ? 3
                : f->cheek == 2 ? -2
                                : 0;
    if (f->mouth == 4)
      h = 0;
    if (f->mouth == 5)
      h = 3;
    if (h < 1) {
      line(&c, 120 - w, mouth_y - smile, 120, mouth_y + 1, RGB(128, 61, 82));
      line(&c, 120, mouth_y + 1, 120 + w, mouth_y - smile, RGB(128, 61, 82));
      line(&c, 112, mouth_y + 4, 128, mouth_y + 4, RGB(242, 174, 161));
    } else {
      oval(&c, 120, mouth_y, w + 2, h + 2, RGB(168, 81, 103));
      oval(&c, 120, mouth_y, w, h, RGB(49, 27, 48));
      if (h > 4) {
        rect(&c, 120 - w + 4, mouth_y - h + 1, w * 2 - 8, 2,
             RGB(248, 232, 208));
        oval(&c, 120, mouth_y + h - 2, w / 2, 2, RGB(193, 102, 122));
      }
      if (f->mouth == 5)
        rect(&c, 120 - w + 2, mouth_y - 2, w * 2 - 4, 3, RGB(246, 231, 210));
      line(&c, 114, mouth_y + h + 2, 126, mouth_y + h + 2, RGB(255, 188, 175));
    }
  }
  /* Hair panels form a distinct swept fringe, not a borrowed character. */
  {
    const point p[] = {{34, 64},  {48, 30},  {91, 16},  {153, 15}, {188, 41},
                       {191, 71}, {167, 62}, {147, 42}, {128, 65}, {96, 72},
                       {72, 66},  {61, 89},  {47, 114}};
    poly(&c, p, 13, hair);
  }
  {
    const point p[] = {{47, 53},  {74, 26}, {116, 22}, {153, 26},
                       {131, 51}, {98, 61}, {68, 56}};
    poly(&c, p, 7, hair_light);
  }
  {
    const point p[] = {{145, 29}, {177, 42}, {188, 72}, {171, 59}};
    poly(&c, p, 4, RGB(88, 73, 114));
  }
  line(&c, 57, 45, 97, 30, RGB(125, 108, 149));
  line(&c, 97, 30, 139, 29, RGB(125, 108, 149));
  line(&c, 50, 58, 80, 66, copper);
  line(&c, 80, 66, 107, 65, copper);
  line(&c, 174, 50, 186, 90, cyan);
  line(&c, 180, 72, 192, 145, hair_light);
  line(&c, 39, 84, 34, 184, hair_light);
  line(&c, 37, 95, 33, 171, RGB(89, 68, 116));
  /* Ear housings, rotating cheek servos and cabling. */
  rect(&c, 26, 91, 17, 57, RGB(27, 36, 56));
  rect(&c, 28, 95, 11, 47, RGB(133, 155, 169));
  rect(&c, 30, 102, 7, 31, copper);
  joint(&c, 35, 93, 5, copper);
  joint(&c, 35, 147, 5, copper);
  rect(&c, 195, 88, 17, 55, RGB(27, 36, 56));
  rect(&c, 198, 94, 10, 41, RGB(121, 146, 162));
  rect(&c, 201, 100, 4, 25, cyan);
  joint(&c, 204, 89, 5, cyan);
  line(&c, 34, 153, 46, 181, copper);
  line(&c, 46, 181, 72, 197, copper);
  line(&c, 205, 149, 195, 182, cyan);
  line(&c, 195, 182, 169, 201, cyan);
  for (i = 0; i < 3; i++) {
    rect(&c, 28, 159 + i * 8, 4, 3, RGB(114, 140, 157));
    rect(&c, 204, 154 + i * 8, 4, 3, RGB(114, 140, 157));
  }
}
