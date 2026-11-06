# Exact intelligibility resume — November 6, 2026

Sole authorized owner: work-160cc0e6fa30-resume-2. Check owner/lock and active writers before edits; do not duplicate builds. AQUORA untouched. No publication.

Production DSP remains unchanged at verified 1641726b / source checkpoint 3a407ec. Existing native/WASM/797-hash acceptance and old CI/backup/MIDI/storage evidence were not replayed. Current research tools/results are checkpointed separately; no new firmware acceptance is claimed.

## Completed new experiment — do not rerun
Canonical evidence: validation/nucleus-2026-11-06/README.md and its corpus/recognition/analysis JSONs. Twelve fixed-pitch cases (vowels, diphthongs, consonant transitions, contexts) at MIDI 48/60/72; 36 baseline/late/smoothed recordings. Scores are identical between DSP variants. The same cached tiny.en ran offline with no expected-text prompt. Temporary runtime dependencies had been pruned and were restored; no new model was downloaded. environment.json records exact versions.

- Late glide (60% nucleus, final 40% glide): non-diphthong controls byte-identical; recognition worsened at 48/60 and failed at 72. REJECTED, not promoted.
- Independently moving band weights into existing smoothed input gain: M→IY exact-edge step at MIDI 72 falls .1703→.0023; P/T/K boundaries also improve. Recognition remains unsuccessful. Transition guard fails in BOTH baseline (746 limiter hits) and candidate (506), each 53,673,984 samples at velocity 127 across voices/styles/registers. Candidate ISOLATED, not promoted. Baseline production engine.c unchanged.

## Verified permanent experiment backup
Source/evidence workflow 42205571438 passed at 0177d9142c70d323da451785067fab8082f0a7ac. It reproduced only the new 36 audio hashes, packaged research evidence and preserved it; no recognition model or old acceptance tests were run there. Two packaging-only failures (YAML quoting and absent runner ffmpeg) are fixed; lossless WAV.gz now needs no media dependency.

Backup branch commit: a999d415609c3d458b0b4a3c39016c6718d5198c. Archive: experiments/0177d9142c70d323da451785067fab8082f0a7ac.zip. SHA256 de9ec59fa471af6507ba2a505e50eeec10cd9b620543a7e1be3fa68bcb836a31; 161 members. Independently downloaded and checked only this NEW experiment archive, source identity and every member hash. Old firmware archives remain intact. EXPERIMENT.json explicitly says firmware_changed=false/release_accepted=false. Evidence contains recorded recognition failures and lossless baseline/candidate pairs, not an accepted firmware package.

## Next single acoustic cause
Test smoothing OUTPUT band weights while preserving UNWEIGHTED resonator states, instead of carrying weighted energy inside resonators. Start with the same consonant-transition cases/registers and tests/nucleus_transition.c guard. Only if boundary quality/headroom improves should recognition be compared. Keep it isolated; do not combine it with the rejected late glide. Existing tools/nucleus_build.py reconstruct old candidates for review, not a request to rerun them. Add a new candidate without overwriting recorded baseline/late/input-smoothing evidence.

**English intelligibility is unresolved.** Repeated beep/wait/right/empty transcriptions are failures. No spectral proxy, CI success or archive hash is a listening pass. Physical FM-1 quality/CPU remain owner-unverified. All 23 release IDs and other blockers remain mandatory in NEXT_BUILD_ACTIVE.md; do not publish.
