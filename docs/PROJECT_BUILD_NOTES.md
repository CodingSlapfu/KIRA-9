# KIRA-9 — Active Outstanding Work Only
**Revision 2026-11-05** | **Status: all entries NEW/UNVERIFIED; nothing built.**

1. **P0 / NEW — Repository and reproducible platform.** Create/verify `CodingSlapfu/KIRA-9` and baseline commit of this package; exclusive lock, pinned toolchain, safe firmware identity/flash layout, license audit, validated hardware memory/resource budget, CI/test harness. Evidence: remote SHA, build manifest and checks.
2. **P0 / NEW — Singing & animation.** English phoneme/syllable/source-filter pipeline, original voice/style presets, facial phoneme rig with actuators/expression & occasional physical twitches, audio/visual independence. Evidence: host audio renders/intelligibility fixtures, deterministic animation renders, CPU/flash/SRAM profile.
3. **P0 / NEW — Standalone songs.** Full offline sequencer/transport, demo songs, keyboard LIVE/SOLO SONG/PHRASE/WORD modes, compatible phrase/melody event model. Evidence: host song regressions, native/emulator boot + playback.
4. **P0 / NEW — MIDI bridge.** Generic BLE MIDI peer pairing/notes/clock/transport + bidirectional class-compliant USB MIDI via iPad hub; one master; shared transport-neutral engine; disconnection recovery. Evidence: protocol tests, two-node fixture, USB descriptor and BLE packet tests, UI traces. Physical pairing and iPad test: owner-UNVERIFIED.
5. **P0 / NEW — Library & editor.** Factory demos and safe persistent song/phrase/word storage; KIRA-9 website lyric generator, own-lyrics import/edit, phoneme/melody alignment, preview, transfer/backup/restore, flash installer. Evidence: save/power-loss/migration, browser/device-transfer, website E2E tests.
6. **P0 / NEW — Full product acceptance & publication.** Source→feature/controls matrix; CPU/deadline, OLED/LCD screen timings, sound/phoneme tests, web/native/emulator/midi/packaging/security/installer, reproducibility, verified GitHub release, SHA-256 ZIP backup and live site. Physical FM-1 testing remains with owner.

**Done-work hygiene:** Each completed entry moves into dated `CHANGELOG.md` and `validation/ACCEPTANCE.md` with commit, test, package and release evidence. Leave only unfinished items here; never re-run completed milestones just to fill time. If blocked, preserve newest verified remote checkpoint and one exact resume command.

---

# KIRA-9 — Work Mode START HERE
**Created 2026-11-05** | **State: pre-implementation specification** | **Target: orange M-VAVE FM-1 (240×240)**

## Single-pass entry, minimum usage
1. Read this file (once), `NEXT_BUILD_ACTIVE.md` (active incomplete work), `ACTIVE_SCOPE.md` (acceptance/scope). Refer to deeper docs **only for relevant implementation**; do not repeatedly reread the whole repository or archived logs.
2. If KIRA-9 GitHub repository does not yet exist, create **`CodingSlapfu/KIRA-9`** with user-authorized access, then upload these planning files as the initial baseline. If repository creation is not available, report the precise blocker and provide importable source files; **never claim the remote repository exists without verifying it**.
3. Establish correct environment/toolchain and investigate relevant reference firmware and M-VAVE FM-1 SDK, hardware memory map, recovery bootloader, firmware identity, and copyright/license. **Don't blindly copy or modify AQUORA source**; a transport-neutral MIDI protocol/spec can be shared with permission and versioning.
4. Before ANY edits/build/deploy, check for a current work session and exclusive **KIRA-9 build lock**. One writer/one release publisher. Never overlap project builds or destroy an owned lock. AQ and KIRA-9 are separate repositories but coordinate shared MIDI-protocol changes via explicit versioned contracts.
5. Implement the complete active scope continuously: code → host/DSP tests → emulator → native firmware → web editor → browser installer → package → independent verification → GitHub backups → publish. **Don't pause to ask “proceed” after milestones.** Only stop for a genuine blocker, tool/usage limit, or needed physical hardware testing.
6. GitHub: commit and push at project start and every meaningful checkpoint, **before long compile/tests** and before stopping. Verify remote SHA/branch; tag final accepted release; archive downloadable source/artifacts and SHA-256 manifest so a temporary Work environment is not the only copy.
7. Maintain a very short, evidence-based `NEXT_BUILD_ACTIVE.md`: Completed means linked source commit + test + artifact/release verification. Move completed items to dated `CHANGELOG.md`/`validation/`. No accumulated duplicate tasks.
8. Preserve earlier working installers/releases, unique safe firmware identity and direct update paths. Never publish a build with known release-blocking defects. Hardware-only tests remain **UNVERIFIED** until owner runs them; no emulator benchmark claimed as physical evidence.
9. Report only concrete status: latest verified remote SHA, tests/pass/fail, compiled package identity/hash, live installer URL, remaining blockers, owner test instructions. Minimize narration, duplicate tool calls, redundant planning, and waiting.

## Fixed project decisions
- KIRA-9's character name = firmware brand/website name; one original female cyborg singer inspired by anime cyberpunk (do not copy any existing character).
- Standalone singing is first-class; never require a host, iPad, network or cloud for playback.
- Synced singing supports **direct BLE MIDI** and **class-compliant USB MIDI via iPad hub/CoreMIDI routing** (e.g. midimittr). Direct TRS cable between FM-1 devices not required. Core MIDI transport is generic; no KIRA-9-specific pairing whitelist.
- AQUORA's AIR radio mode and BLE MIDI **must be mutually exclusive**. USB MIDI is allowed with AIR. Coordination scope: AQUORA GitHub Issue #31, plus Issue #13; **don't silently modify AQUORA during KIRA-9 work unless a separate authorized owner session exists**.
- KIRA-9 vocal synthesis must support English phonemes, presets/voices, styles, standalone song engine, live playing, phrases, synchronized lyric performance, and authentic facial cybernetics. Occasional glitches are physical servo/twitch/expression misfires **not visual screen corruption**. Voice/timing unaffected.
- Website: original lyrics generator from ideas; import/edit user's lyrics; voice/style/phoneme/melody editing, audio and face preview, demo/phrase banks, device transfer, backup and browser installation. Generated lyrics need a melody/note timing plan before being called 'ready to sing'.
- Strict memory/performance constraints; source hardware limits from SDK/linker map, never assume fixed flash capacity or unlimited song slots.

---

# Copy into ChatGPT Work (KIRA-9 first build)

Build **KIRA-9**, a brand-new standalone cybernetic singing-instrument firmware for my **orange M-VAVE FM-1**, plus its independent website, web lyric/song editor and browser installer. **AQUORA and KIRA-9 are my only active projects.**

Initial specification is the attached/imported `KIRA-9_Repository_Starter` package. Create or verify a new dedicated GitHub repository **CodingSlapfu/KIRA-9**; push the specification immediately and verify the exact remote commit. Do not confuse this with AQUORA or resume retired projects. First read `WORK_MODE_START_HERE.md`, `NEXT_BUILD_ACTIVE.md`, `ACTIVE_SCOPE.md` and only the technical references you need. Inspect existing work before editing; acquire an exclusive KIRA-9 project lock and do not overlap builds.

Implement all outstanding scope end-to-end in one continuous run where tools/limits permit: English singing vocal/phoneme engine, original singing styles/voice identities, standalone demo songs/keyboard/live/phrase/word modes, full expressive animated female cyborg face with phoneme-driven mouth/eye/jaw actuators and rare *physical servo twitches* (not screen glitches), compact reliable persistent library, independent lyric-generator website with user-lyrics import/phoneme/melody editor and transfer, generic interoperable direct BLE MIDI, two-device USB MIDI via iPad hub/midimittr routing, MIDI-follow mode and safe external transport, accessible on-device UI, native firmware/emulator/reproducible host acceptance and verified web installer.

AQUORA must work with the same generic MIDI transport: see https://github.com/CodingSlapfu/AQUORA/issues/31 . AQUORA AIR and Bluetooth MIDI are mutually exclusive; USB MIDI can coexist with AIR. **Do not edit or publish AQUORA in this KIRA-9 build session without explicitly coordinating single-writer ownership and an authorized separate AQUORA release.**

Use hardware facts, legal assets and evidence. Prioritize audio reliability, English intelligibility, excellent character motion, safe firmware update, testable USB/BLE interoperability and website editor. No fake hardware measurements or unlicensed artist voice copies. Stage/review all scope, native build, host tests, emulator, BLE/USB protocol fixtures, website acceptance, secure song storage, source↔package hashes, independent backups and website publication. Keep only unfinished work in `NEXT_BUILD_ACTIVE.md`, archive completed work with verification, never restart passed stages or ask me to keep saying 'proceed'. Push and verify remote GitHub checkpoints before long work and on interruption; preserve source/artifact ZIPs, checksums, and exact resume steps.

Release only after software blockers are resolved, and leave physical FM-1 flashing, pairing, audio/listening, actual FPS and iPad hub testing to me as **UNVERIFIED**. If a genuine blocker prevents release, preserve a verified remote checkpoint and report precisely what remains; do not publish an incomplete firmware.