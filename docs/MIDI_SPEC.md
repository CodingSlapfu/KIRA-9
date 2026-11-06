# Universal MIDI Specification — direct BLE + USB via iPad
Both AQUORA and KIRA-9 implement a **transport-neutral MIDI engine** compatible with *any* standards-compliant peer, not a proprietary pairing whitelist.

## Direct wireless
AQUORA default leader/central and KIRA-9 follower/peripheral, with role reversal if supported by the verified SDK. Standard BLE MIDI GATT/timestamps, discovered peer names, saved partner, auto-reconnect, observability and fault recovery. The two devices produce sound locally; BLE MIDI is control data, not Bluetooth audio.

## iPad USB hub
AQUORA MIDI OUT → powered USB hub → iPad CoreMIDI and midimittr (or other MIDI router) → KIRA-9 MIDI IN; optional selected return path KIRA-9 OUT → AQUORA IN. Both units expose class-compliant USB MIDI device **IN AND OUT** ports with distinguishable device names and simultaneous enumeration. midimittr generally routes rather than generates MIDI clock. A compatible DAW may act as the authoritative clock if selected.

## Interoperable messages
24 PPQN MIDI Clock 0xF8, Start 0xFA, Continue 0xFB, Stop 0xFC, note-on/off/velocity/gate, CC, pitch bend, program change, channel maps, optional Song Position Pointer and panic/all-notes-off. Design one source-authoritative transport; bounded/timestamped event scheduler, drift/jitter control, no echo loop, no double clock on USB+BLE, no held notes on disconnection.

## Optional versioned musician profile
A documented optional standard-MIDI CC/program mapping can select song ID, phrase ID, voice/style/preset, emotion and performance expression. **Lyrics themselves stay in KIRA-9 locally**; ordinary MIDI notes don't carry English lyric text. Unknown peers can play basic MIDI without implementing extensions.

## Operation and radio safety
KIRA-9: Internal Solo, Follow BLE, Follow USB, Auto (never force unexpected takeover). Generic MIDI peer choice, tempo source and meaningful status on-device; both paths may coexist only with one selected timing authority. AQUORA: **AIR and BLE MIDI are mutually exclusive radio modes**. Enabling BLE automatically disables AIR and smoothly returns AIR FX to baseline; enabling AIR first flushes BLE notes/clock then disconnects radio MIDI. **USB MIDI remains usable with AIR**. Source specification: https://github.com/CodingSlapfu/AQUORA/issues/31

## Acceptance
Independent BLE packet decode/encode/timestamp/fragmentation/invalid-input tests; two-node emulator, generic test peer, role changes, 24 PPQN stress and note recovery, correct USB descriptors and independent ports. Simulated iPad routing and owner-only real FM-1 + powered hub + midimittr verification. Physically measured latency/jitter and radio coexistence remain UNVERIFIED until tested.