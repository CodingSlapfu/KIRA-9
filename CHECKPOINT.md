# KIRA-9 — resume this implementation
Owner: work-160cc0e6fa30. Baseline 3d7c4c2; verified earlier checkpoints d83700a and 306b252. Read the latest remote main SHA; do not restart the specification-only baseline. Current development includes native firmware, host app, English source/filter core, factory demos/cues, typed banks, generic MIDI and a shared-WASM studio.

## One command (isolated checkout with no current owner)
`git submodule update --init --recursive && python3 tools/setup_native.py`
The setup prints JIELI_TOOLCHAIN and AC79_SDK; export those paths, activate Emscripten 4.0.19, then run `./tools/verify_checkpoint.sh`. Do not rerun unchanged passed stages except checks affected by new work. Exact active software blockers: NEXT_BUILD_ACTIVE.md. Requirement gate must remain closed until all real evidence exists.

## Environment recovery
- Compiler archive hash and three SDK hashes: validation/PLATFORM.md; tools/setup_native.py verifies every download. Extraction strips archive ownership.
- Platform/BSP pinned recursively; no Miku assets or synth code reused. Original source MIT, dependencies retain MPL/Apache/BSD/OFL terms.
- Git CLI push authentication is unavailable in this Work environment; public fetch works. Use connected GitHub blob/tree/commit/ref tools with expected-head lease for source checkpoints; verify remote ref after each write. Do not waste time retrying CLI authentication.
- Dictionary: tools/build_dictionary.py pins CMU source and preserves its license. Generated studio dictionary/WASM/emulator are intentionally rebuilt, not source-controlled copies.
- CI workflow creates a complete independent development ZIP with native and web artifacts plus source (including dependency source) and SHA256SUMS. It uploads a run artifact and maintains versioned ZIPs on kira-9-development-backups. Verify run and backup branch before claiming archive preservation.

No accepted release, public studio or live installer has been published. The first-release gate still rejects incomplete scope. Physical testing stays with the owner.
