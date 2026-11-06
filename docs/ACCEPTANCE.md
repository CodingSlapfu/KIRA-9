# KIRA-9 — Required Acceptance (planning; no release built)

## Truth labels
Software COMPILED / HOST TESTED / EMULATED / PUBLISHED / OWNER HARDWARE VERIFIED are different levels. Never treat host/emulator timing or audio as physical FM-1 acceptance. Gate requirements through requirements/manifest.json and tools/requirement_gate.py --phase release; the initial project deliberately FAILS release certification.

## Firmware/platform
Pin actual legal SDK/toolchain and link-time memory map; unique updater identity and safe flash partitions, native executable + maps, forced-single-core fallback, reproducible host/WASM/emulator and source-matched .fwsc package with SHA256. Capture p50/p95/p99/max 256-frame callback times, audio XRUN, RAM high-water and LCD frame budget; protect the 5.8 ms 44.1kHz deadline. No blocking BT, flash or graphics in audio ISR.

## Vocal and character
Demonstrate intelligible English plosives/fricatives/nasals/diphthongs, phoneme vs note timing and lyric prosody. Actual comparative rendered PCM for distinct original voices/styles, loudness, pitch, breath, portamento, register, emotion, morphing and expressive note transitions; no clipping or stuck notes on Stop. Test actual 240×240 multi-frame mouth/eye/brow/jaw actuator motion mapped to phonemes, rare physical character twitches, deterministic control and no screen artifacts. Audio buffer parity with/without twitches.

## Solo and interoperability
Stand-alone demo playback from cold boot with USB unplugged and Bluetooth off; standalone Song/Live/Phrase/Word modes; stable lyric timing without another instrument. BLE MIDI generic peer scan/pair/clock/notes/CC/program/bend and robust reconnect; class-compliant USB MIDI IN/OUT, 2-device iPad hub routing through midimittr, one selected clock master, auto sync safely and no note loop. AQUORA AIR↔BLE exclusive; USB with AIR allowed.

## Storage, website and release
Factory demos restorable; songs/phrases/words save, reboot, CRC corruption/power-cut, full capacity, export/import and transfer roundtrip. AI-assisted original lyric generation and own-lyrics preservation, editor phoneme/melody/viseme output, actual browser voice preview, emulator UI and web installer; test exact release identity, direct update and rollback path. GitHub backup and independent ZIP/checksums verified BEFORE publication; live website and installer verified through browser.

## Owner-only (UNVERIFIED until tested)
Real orange FM-1 flashing, native speaker/headphone intelligibility, LCD lip-sync/FPS, actual DMA callback and battery figures, storage across physical power cycles, BLE pair/jitter to AQUORA, both FM-1s via powered hub/iPad/midimittr. Issue a short physical checklist and collect feedback after software acceptance.