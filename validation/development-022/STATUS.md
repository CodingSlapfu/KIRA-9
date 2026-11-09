# KIRA-9 v0.2.2-dev — testing candidate

Native identity FM-1_74000202, build05A90D68. Compiled application223292B; data/BSS78264/98304; pool176844/344064; RAM code5444/32768. Build is forced-single-core. Real FM-1 CPU, latency and thermal/long-session behaviour remain owner-unverified.

New implementation:
- First voiced onset snaps to the intended note rather than gliding down from initialization at A440. Connected vowels and hummed notes retain vibrato onset; contiguous sung-vowel events avoid a repeated release gate.
- Diphthongs hold their vowel nucleus and complete a smooth off-glide within the final120ms, bounded to35% for short notes. Mouth shape follows the same transition. Formant tables and the frozen five-grain experiment were not changed/promoted. English naturalness/intelligibility is not established by these technical changes.
- MIDI sustain is source-owned: note-off is deferred until the correct pedal release; foreign releases cannot stop the held note; STOP/panic clears pedal/pending transitions. Released Scat onsets cannot later reopen a vowel.
- Clock duplicates, future timestamps and timestamps older than2seconds are rejected before advancing transport. Existing timestamp-burst/wrap/jitter regression passes. Physical BLE pairing/reconnect/interoperability is still unverified.
- Brows follow real voice emphasis; emotional upper lids and their mechanical actuators move without opening hummed lips. Studio STOP immediately clears pose/status, and live voice/expression controls reach the running engine.

Evidence:
- targeted.txt: new tuning/legato/sustain/source isolation/cancelled onset/closed hum/diphthong-viseme/clock tests; ASan/UBSan also pass.
- core-regressions.txt: revalidated affected core, articulation, face/arrangement and requirement gate; no old acoustic/listening experiments replayed.
- clock.txt and controls.txt: timestamped-clock checks and actual app SAVE/reboot/live families/note-off.
- parity.txt: Linux C/shared WASM1,024,000 PCM samples and2,000 exact poses, max error0.
- worklet.txt: actual WASM AudioWorklet at48kHz with mixed section profiles, closed hum and STOP.
- package-and-budgets.json/package-safety.txt: actual target package CRC, decrypted application/loader bytes, RAM/flash bounds, store isolation, simulated021→022 update/recovery/loss/final-identity.
- visual-sequence.json and engine-face-022.gif:140 actual240x240 frames at20fps, including28 closed-hum frames; no audio file created. Browser compact pose carries mouth/open and selected emotion; native envelope-driven brow emphasis is not separately encoded in that compact preview. This remains a visual parity refinement, not a hardware acceptance claim.
- rollback.json: exact021 rollback from022 simulated successfully with zero wrong bytes;60-byte preferences and storage map retained.
- native/wasm/emulator build logs and compiled-input.json link artifacts to37 exact input SHA256 hashes. CI42635509598 succeeded; downloaded artifact SHA25693077c5f40aac93b2514d36977dbc06a67c88d8631be10d6ed78c6be7040f93c matched GitHub's artifact digest. All37 inputs matched this recovered workspace.

The original checkout/compiler cache was absent; verified021 source was restored. Native compilation used the authenticated GitHub connection, pinned platform/BSP/toolchain and a compile-only job. No Git credentials, Base64 archives, audio deliverables or public firmware deployment were used.

Storage formats/map and the60-byte saved preferences layout are unchanged from021. Exact021 rollback is included. Older020/legacy rollback remains available; older firmware resets the newer preferences object, so restore its matching pre-update device backup.

All23 mandatory requirements remain tracked as partial. Release gate still blocks official publication. Outstanding: owner naturalness/intelligibility and frozen-pair judgments; full character/controls/editor workflow acceptance; real BLE peers/reconnection/jitter/sustain/clock; device CPU/audio; actual interrupted flash/rollback/restore. AQUORA was not modified.

Source backup commit2afb96f2c8dbc80cf6521b77ed014a32cac1eb0f independently verified against187 source/evidence blob hashes and the main branch ref. Additional final packaging/visual/rollback helpers are in the downloadable source snapshot.
