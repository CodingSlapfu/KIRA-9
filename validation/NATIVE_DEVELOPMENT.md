# Native development build — not a release
Compiler/SDK provenance: PLATFORM.md. App is now in app/ so the register-access auditor checks application source rather than recursively auditing its own platform dependency. No safety check disabled.

Native build succeeded before latest DSP changes: 177000-byte app, 11782-byte update loader, 614938-byte development .fwsc; identity FM-1_7400. Linker: RAM code 5444/32768 bytes, data+bss 52472/98304, pool 19204/344064. No soft-double routines, no inlined 64-bit-multiply/load hazard; radio ramp in RAM; own BLE stack links no vendor libraries. Latest source must be rebuilt before claiming matching artifacts.

Host panel acceptance: tests/panel.txt passed playback/stop, voice selection, SAVE/reboot persistence, source selection and rejecting USB transport in BLE-follow mode. This is simulated hardware, not physical evidence.

Pending: phoneme listening quality/style repertoire, all four performance modes (initial code currently shares live behavior in three modes), peer picker/reconnection UI, full library types/migration, editor, transfer, true animation approval, comprehensive release acceptance. No native or host result makes those complete.
