# Exact priority resume — November 6, 2026

Same authorized owner: work-160cc0e6fa30-resume-2. No second build/publisher. AQUORA untouched.

Latest vocal source: f17d09f92d123c3a8cde1859c2b948c2fe855c3a. Development CI run 42194202045 PASSED matching native/WASM verification and backup preservation. It verified 780 member hashes and remote backup commit 22f981c004a997231344fe8a19e9d0ce5762d8a4. Do not repeat it. If transient infrastructure/preservation failure, rerun only that failed job; code failures require the targeted fix and affected tests.

CI repair is independently verified at 63ab82c, run 42193284767, backup branch commit e044e448d955843b90c28ec93126bdc20fcd9460 (760 archive members). The APP_SYSEX callback enables the native USB-session API. Never return to the failing 13aca33 configuration or rerun its successful storage/editor tests merely because native linking failed.

Vocal changes: core/articulation.h + core/engine.c, dictionary stress preservation, tempo-aware compiler consonants and connected-speech defaults. New focused tests pass. Local actual C transfer roundtrip also passed after compiler changes. tools/vocal_comparison.py recreates baseline/updated recordings at build/vocal-comparison; comparison.wav alternates before/after per phrase. The development backup ZIP includes these recordings and fresh metrics. No external GPL code/tables/art copied.

Remaining highest priority: acoustic English intelligibility. Tiny.en returned empty transcriptions for all three phrases in both versions: no transcription/listening pass is claimed. Fixed timing and lexical stress are measured improvements, not proof of natural/intelligible singing. Use the preserved A/B recordings and tests to guide the next targeted acoustic change. Avoid a broad rewrite or repeated recognizer installation. Physical FM-1 assessment remains owner-unverified.

Other first-release blockers remain in NEXT_BUILD_ACTIVE.md. All 23 IDs remain mandatory; no publication until release gate and real acceptance pass. Do not restart completed platform, face, storage, MIDI, editor or factory demos.

Verified archive SHA256: e7977b02b4dff02c0f976d33af4d673257e40a85622dad8f2dfc13a03e6da05c. Native image 220500 B, data+bss 77960/98304, pool 176844/344064, development identity FM-1_7400. Exact PCM parity: 51,200 samples, zero error. No release acceptance or publication.

Independent download verification in this Work run: fetched the ZIP from the permanent GitHub backup branch, checked the whole-archive SHA above, source_commit=f17d09f and all 780 contained member hashes, including comparison.wav. Firmware SHA256: 351bdd0a291d19da7f09dfd35d22470ad0c8f6e78aadcf06a6b80d71c2c8b5ce. Local post-compiler C-transfer roundtrip/failure-recovery checks also passed. Requirement plan passes; release gate still rejects incomplete P0s.
