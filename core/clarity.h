/* SPDX-License-Identifier: MIT; original measured source/filter balance. */
#ifndef K9_CLARITY_H
#define K9_CLARITY_H
/* Three parallel resonators otherwise overemphasize the low first formant.
 * Keep nasal energy low, and route sibilants to their upper noise bands. */
static const float k9_spectral_weights[K9_NPHONE][3] = {
  {1.00f,1.00f,1.00f}, /* SIL */
  {0.25f,4.00f,7.00f}, /* AA */
  {0.25f,4.00f,7.00f}, /* AE */
  {0.25f,4.00f,7.00f}, /* AH */
  {0.25f,4.00f,7.00f}, /* AO */
  {0.25f,4.00f,7.00f}, /* AW */
  {0.25f,4.00f,7.00f}, /* AY */
  {0.25f,4.00f,7.00f}, /* B */
  {1.00f,1.00f,1.00f}, /* CH */
  {0.25f,4.00f,7.00f}, /* D */
  {0.05f,2.00f,4.00f}, /* DH */
  {0.25f,4.00f,7.00f}, /* EH */
  {0.25f,4.00f,7.00f}, /* ER */
  {0.25f,4.00f,7.00f}, /* EY */
  {0.05f,2.00f,4.00f}, /* F */
  {0.25f,4.00f,7.00f}, /* G */
  {1.00f,1.00f,1.00f}, /* HH */
  {0.25f,4.00f,7.00f}, /* IH */
  {0.25f,4.00f,7.00f}, /* IY */
  {0.25f,4.00f,7.00f}, /* JH */
  {1.00f,1.00f,1.00f}, /* K */
  {0.25f,4.00f,7.00f}, /* L */
  {1.00f,0.25f,0.10f}, /* M */
  {1.00f,0.25f,0.10f}, /* N */
  {1.00f,0.25f,0.10f}, /* NG */
  {0.25f,4.00f,7.00f}, /* OW */
  {0.25f,4.00f,7.00f}, /* OY */
  {1.00f,1.00f,1.00f}, /* P */
  {0.25f,4.00f,7.00f}, /* R */
  {0.05f,2.00f,4.00f}, /* S */
  {0.05f,2.00f,4.00f}, /* SH */
  {1.00f,1.00f,1.00f}, /* T */
  {0.05f,2.00f,4.00f}, /* TH */
  {0.25f,4.00f,7.00f}, /* UH */
  {0.25f,4.00f,7.00f}, /* UW */
  {0.05f,2.00f,4.00f}, /* V */
  {0.25f,4.00f,7.00f}, /* W */
  {0.25f,4.00f,7.00f}, /* Y */
  {0.05f,2.00f,4.00f}, /* Z */
  {0.05f,2.00f,4.00f}, /* ZH */
};
#endif
