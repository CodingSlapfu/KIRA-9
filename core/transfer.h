/* SPDX-License-Identifier: MIT */
#ifndef K9_TRANSFER_H
#define K9_TRANSFER_H
#include <stdint.h>
#define K9_XFER_MAX 3840u
#define K9_XFER_CHUNK 96u
enum {
  K9_X_OK,
  K9_X_BAD,
  K9_X_BOUNDS,
  K9_X_BUSY,
  K9_X_ORDER,
  K9_X_CRC,
  K9_X_SAVE,
  K9_X_MISSING,
  K9_X_EXPIRED
};
typedef struct {
  uint8_t data[K9_XFER_MAX];
  uint32_t crc, deadline;
  uint16_t transaction, length, received, last_transaction;
  uint8_t kind, slot, active, last_valid, last_result;
} k9_transfer;
typedef struct {
  void *ctx;
  int (*busy)(void *);
  int (*load)(void *, uint8_t, uint8_t, uint8_t *, uint16_t);
  int (*validate)(void *, uint8_t, const uint8_t *, uint16_t);
  int (*save)(void *, uint8_t, uint8_t, const uint8_t *, uint16_t);
} k9_transfer_io;
void k9_transfer_init(k9_transfer *);
void k9_transfer_poll(k9_transfer *, uint32_t);
/* Decoded payload, not a raw MIDI frame. At most one bounded response. */
uint16_t k9_transfer_command(k9_transfer *, const k9_transfer_io *, uint32_t,
                             uint8_t, const uint8_t *, uint16_t, uint8_t *,
                             uint16_t);
#endif
