# KIRA-9 — Work Mode START HERE
**Created 2026-11-05** | **State: pre-implementation specification** | **Target: orange M-VAVE FM-1 (240×240)**

## Single-pass entry, minimum usage
1. Read this file (once), `NEXT_BUILD_ACTIVE.md` (active incomplete work), `ACTIVE_SCOPE.md` (acceptance/scope). Refer to deeper docs **only for relevant implementation**; do not repeatedly reread the whole repository or archived logs.
2. The GitHub repository **`CodingSlapfu/KIRA-9`** now exists; verify its authoritative `main` branch and newest checkpoint before editing. Never create a duplicate repository or discard newer work.
3. Establish correct environment/toolchain and investigate relevant reference firmware and M-VAVE FM-1 SDK, hardware memory map, recovery bootloader, firmware identity, and copyright/license. **Don't blindly copy or modify AQUORA source**; a transport-neutral MIDI protocol/spec can be shared with permission and versioning.
4. Before ANY edits/build/deploy, check for a current work session and exclusive **KIRA-9 build lock**. One writer/one release publisher. Never overlap project builds or destroy an owned lock. AQ and KIRA-9 are separate repositories but coordinate shared MIDI-protocol changes via explicit versioned contracts.
5. Implement the complete active scope continuously: code → host/DSP tests → emulator → native firmware → web editor → browser installer → package → independent verification → GitHub backups → publish. **Don't pause to ask “proceed” after milestones.** Only stop for a genuine blocker, tool/usage limit, or needed physical hardware testing.
6. GitHub: commit and push at project start and every meaningful checkpoint, **before long compile/tests** and before stopping. Verify remote SHA/branch; tag final accepted release; archive downloadable source/artifacts and SHA-256 manifest so a temporary Work environment is not the only copy.
7. Maintain a very short, evidence-based `NEXT_BUILD_ACTIVE.md`: Completed means linked source commit + test + artifact/release verification. Move completed items to dated `CHANGELOG.md`/`validation/`. No accumulated duplicate tasks.
8. Preserve earlier working installers/releases, unique safe firmware identity and direct update paths. Never publish a build with known release-blocking defects. Hardware-only tests remain **UNVERIFIED** until owner runs them; no emulator benchmark claimed as physical evidence.
9. Report only concrete status: latest verified remote SHA, tests/pass/fail, compiled package identity/hash, live installer URL, remaining blockers, owner test instructions. Minimize narration, duplicate tool calls, redundant planning, and waiting.

## Mandatory missing-task prevention
Read `TASK_ACCOUNTABILITY.md` and `requirements/manifest.json` on first build; run `python3 tools/requirement_gate.py --phase plan`, reconcile latest owner comments/issues, and **refuse release if `--phase release` fails**. Do not confuse completion of a limited hotfix with completion of all requested project scope. Require real visual sequences and real singing-audio test evidence; carry deferred tasks forward with IDs and explicit owner acceptance.

## Fixed project decisions
- KIRA-9's character name = firmware brand/website name; one original female cyborg singer inspired by anime cyberpunk (do not copy any existing character).
- Standalone singing is first-class; never require a host, iPad, network or cloud for playback.
- Synced singing supports **direct BLE MIDI** and **class-compliant USB MIDI via iPad hub/CoreMIDI routing** (e.g. midimittr). Direct TRS cable between FM-1 devices not required. Core MIDI transport is generic; no KIRA-9-specific pairing whitelist.
- AQUORA's AIR radio mode and BLE MIDI **must be mutually exclusive**. USB MIDI is allowed with AIR. Coordination scope: AQUORA GitHub Issue #31, plus Issue #13; **don't silently modify AQUORA during KIRA-9 work unless a separate authorized owner session exists**.
- KIRA-9 vocal synthesis must support English phonemes, presets/voices, styles, standalone song engine, live playing, phrases, synchronized lyric performance, and authentic facial cybernetics. Occasional glitches are physical servo/twitch/expression misfires **not visual screen corruption**. Voice/timing unaffected.
- Website: original lyrics generator from ideas; import/edit user's lyrics; voice/style/phoneme/melody editing, audio and face preview, demo/phrase banks, device transfer, backup and browser installation. Generated lyrics need a melody/note timing plan before being called 'ready to sing'.
- Strict memory/performance constraints; source hardware limits from SDK/linker map, never assume fixed flash capacity or unlimited song slots.