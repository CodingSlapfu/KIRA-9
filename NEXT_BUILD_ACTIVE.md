# KIRA-9 — v0.2.3-dev testing and acceptance

Testing identity FM-1_74000202/build05A90D68. CI42635509598 passed native/WASM/emulator/parity/package gates; exact37-file input manifest matched locally. Full source, installer, exact021 rollback, older rollback options and SHA256 evidence are packaged. See validation/development-022/STATUS.md and OWNER_TESTS.md. No official release/public deployment; AQUORA untouched.

- K9-003/004: naturalness and English vowel intelligibility remain human acceptance gates. New onset tuning, sustained legato/vibrato and bounded diphthong/viseme timing are technically tested. Frozen five-grain experiment remains unchanged/unpromoted pending owner evidence; do not replay its old trials.
- Issue3/K9-003/004/008/013/019/010/022: all five techniques, persisted selectors, scoped editor/presets and native arrangements preserved. New source-owned pedal release/panic, cancelled Scat onset and immediate studio STOP/live expression are tested. Complete physical technique/editor/control workflow acceptance.
- K9-005/006/019: real visemes plus envelope-driven brows/emotional lids and closed humming passed software checks. Full portrait quality, timing/readability and complete navigation remain owner-unverified.
- K9-014–017: duplicate/future/stale clock rejection and source ownership pass host checks. Generic physical BLE pairing/reconnect, jitter/long sessions/tempo/clock authority remain open. Preserve existing transport infrastructure; wireless performance is the priority.
- K9-001/002/007/009/018/020/021/023: current native/WASM/resource/updater gates pass. Physical CPU/audio, interrupted flash/recovery/rollback/restore and final user workflows remain open. Saved settings/map unchanged from021;020/legacy resets newer preferences, so retain matching device backups.

All23 IDs remain mandatory/partial; official release gate remains blocked. Reuse passed receipts. Current compiled inputs are preserved in GitHub workflow0f36eb06 and successful artifact13682442773; full source backup is recorded in validation/development-022/github-source-backup.json when verified. Do not confuse the original54f9d9a checkout used by CI with the restored/overlaid022 build inputs.

## OWNER PRIORITY — KIRA-9 visual identity correction (next build; OPEN)

Owner rejected current website character art as unattractive and not faithful to the intended late-1980s/1990s Japanese cyberpunk anime identity. **Treat as substantial design correction, not minor polish.** Full actionable art and animation requirements: [KIRA9_ART_DIRECTION_NEXT_BUILD.md](KIRA9_ART_DIRECTION_NEXT_BUILD.md).

- Original, beautiful, elegant, memorable cyborg vocalist; *Ghost in the Shell* / *Akira* era style inspiration **without copying existing characters**. Distinctive close-up face, expressive anime eyes, refined proportions, iconic hair silhouette and integrated tasteful cybernetics.
- Premium cel-shaded linework, cinematic controlled palette; no generic/chibi/western-cartoon/uncanny/vector-placeholder results.
- Smooth blink/gaze/micro-expression and precise attractive singing visemes/lip sync; correct across website, emulator and resource-limited 240×240 FM-1 firmware.
- **Acceptance required:** before/after website + firmware previews and singing-animation frames, targeted resource/performance checks, owner's review of actual visual quality; no false claims of completion from deployment alone. Preserve installer, rollback, audio/BLE, existing technical passes and AQUORA. **Status: v0.2.3 implementation and technical validation in progress / OWNER ACCEPTANCE OPEN.**

## v0.2.3 development correction
Original cel portrait/registered lid-viseme rig and expressive performance contours implemented. See validation/development-023/STATUS.md. Native/WASM/installer evidence and package receipts are recorded there; hardware/visual/listening acceptance remains OPEN. Preserve v0.2.2 rollback and all 23 IDs. No official production release.

## OWNER RESEARCH — JAZZY MIDI Host / MIDIMON BLE routing (2026-11-10)

**Status: owner-approved next-build research/handoff; NOT implemented, compiled, hardware-tested, or release-accepted by this note.** Preserve the latest source, already passing MIDI/clock/transport tests, all 23 requirement IDs, firmware identity, owner acceptance gates, and AQUORA. Coordinate with K9-008, K9-014–017, K9-019, and Issue #4 (Perfect Key/Auto-Tune); do not spin up a competing firmware build solely for this note.

**Source analysis (FM-1 firmware on identical JieLi AC791N hardware):**
- JAZZY: https://github.com/JazzyRhythmer/Jazzy — public firmware explicitly includes USB MIDI Host; its host is adapted from the Rhythmer / ChoralRoot / Melodee lineage. Specific reviewed files: https://github.com/JazzyRhythmer/Rhythmer/blob/main/rhythmer/firmware/src/usb_host.c and https://github.com/JazzyRhythmer/Rhythmer/blob/main/rhythmer/firmware/src/usb_host_desc.h.
- The USB-host code discovers class-compliant USB-MIDI 1.0 streaming interfaces via descriptors; accepts MIDI channel messages, clock/Start/Continue/Stop and Song Position; supports IN/OUT endpoints and compatible hubs; tracks faults and disconnections, reconnects, and releases MIDI-owned notes without unnecessarily releasing local keys. The FM-1 USB port does not supply host VBUS: externally powered devices/host adapters are needed. Host/device are mutually exclusive; the host selection is intentionally NOT persisted, returning to USB device mode on boot to protect normal firmware-update paths. Some behavior is software-tested only; do not imply KIRA-9 hardware acceptance.
- More directly relevant wireless reference: https://github.com/ignis32/midimonitor_fm1 — FM-1 firmware demonstrating simultaneous BLE Central and Peripheral, generic discovery/peer choice, saved-peer reconnect, many-to-many MIDI routing/filters, clock diagnostics, USB device/host switching and disconnect investigation. Inspect its BLE and source-ownership practices; do not assume direct compatibility without measured FM-1 tests.

**KIRA-9 next-build priorities, preserving owner's WIRELESS-ONLY product direction:**
1. **P0 BLE MIDI Central + Peripheral**: receive notes from standard wireless keyboards/controllers while also functioning as an ordinary discoverable BLE MIDI instrument/follower for AQUORA and other peers. Implement robust peer selection, stored partner/autoreconnect, BLE MIDI GATT timestamps, packet fragmentation, bounded queues, status/error UI and resource-safe radio scheduling. No proprietary peer whitelist or mandatory iPad/computer.
2. **P0 live vocal control**: wire external Note On/Off, velocity, sustain, legato, CC/expression, pitch bend, channel/program settings and panic into KIRA-9 voice, lyrics/phrase/vocalise/scat/humming/vocables, with on-device Perfect Key and synthesis-aware vocal pitch correction from Issue #4. Keep vocal and face timing aligned; external note input is not itself waveform Auto-Tune.
3. **P0 authoritative sync and safety**: 24-PPQN Clock, Start, Stop, Continue, optionally Song Position; deterministic one-source tempo authority, jitter/clock-loss handling, no double-clock or MIDI feedback, source-owned note releases, stop/panic safety, and uninterrupted independently controlled backing-music transport and live singing.
4. **Validation**: test with generic BLE peripherals and centrals plus AQUORA; simultaneous role behavior, repeated pairing, long sessions, lost/reordered MIDI, disconnect/reconnect, sustain, clock-jitter measurement, watchdog/audio-XRUN/headroom and face/FX load. Label all hardware-dependent checks UNVERIFIED until owner tests on the physical orange FM-1.
5. **USB MIDI Host = research-only, not an approved change to wireless-only scope.** If the owner separately authorizes wired USB host, assess it as an opt-in secondary feature (powered hub or device power required; default USB device mode on reboot), never replacing or regressing BLE. No TRS requirement.

**Licensing constraint:** JAZZY/Rhythmer host files are marked GPL-3.0-only, while KIRA-9 top-level LICENSE is MIT and BLE builds may link licensed JieLi SDK components. Do NOT paste JAZZY host source blindly into KIRA-9. Investigate the separately MPL-2.0-authorized port https://github.com/hugelton/felucca-bsp/pull/7 and its original authors' explicit permissions documented at https://github.com/ignis32/midimonitor_fm1/blob/main/LICENSING.md, or write original code, with license review before integration.

**Completion gate:** Research is recorded; no claim that new BLE Central, USB Host, or hardware sync features are implemented by this documentation change. Implement only in a safely owned, separately authorized next firmware build and retain official release gates.

## v0.2.4-dev testing branch

Resume from `kira-0.2.4-development` for the latest testing candidate. This pass
adds original beat-grid backing to all eight factory vocal scores, whole-bar
looping, an independent backing mute, live Perfect Key, synthesis-integrated
pitch correction and chorus/echo/delay/reverb. The voice remains formant-based.
Human-singer naturalness and English intelligibility still require listening
acceptance and further source-engine work. Preserve the accepted 0.2.3 portrait.

FM-1 BLE scan no longer clears discovery results on every UI poll, and
disconnect handling releases the affected link's notes and clock ownership.
Real controller pairing, reconnect, jitter, simultaneous links and CPU/XRUNs
remain physical acceptance work. Keep all 23 requirements open for release.
See `validation/development-024/OWNER_TESTS.md` for controls and hardware checks.
