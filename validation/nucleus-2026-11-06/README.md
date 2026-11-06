# Isolated nucleus/transition study — 2026-11-06

Baseline: 3a407ec (firmware DSP unchanged from the verified 1641726b source). Same owner work-160cc0e6fa30-resume-2. No AQUORA changes, old CI/backup/MIDI/storage acceptance replay or publication.

## Controls and decisions
Twelve identical-score cases: four groups at MIDI 48, 60 and 72. Vowel pairs: “beat bit bet bat boot bought”; diphthong contrasts: “bait bet bite bat boat bought”; consonant transitions: “pea tea key see she me”; contexts: “my high light night right”. Pitch is fixed within each clip, with explicit durations/stress. corpus.json contains exact compiled events.

1. **Late glide:** keep initial 60% nucleus then linear glide over final 40%; only tract progress changes. Monophthong and transition control PCM is byte-identical at all registers. Recognition worsens at MIDI 48 and 60, and remains unsuccessful at 72. REJECTED; production glide stays unchanged.
2. **Smoothed band-weight input:** independently move per-phone spectral weights from instantaneous resonator output to existing smoothed gain targets; original glide retained. This reduces the measured M→IY exact-edge step at MIDI 72 from 0.1703 to 0.0023 (and the ±3ms maximum from .1703 to .0098). P/T/K boundaries also improve. Recognition remains unsuccessful. A maximum-velocity transition sweep still fails headroom: baseline 746 limiter hits, candidate 506, each over 53,673,984 samples. **Candidate isolated, NOT promoted.** Both stop-tail tests pass. Production engine.c is unchanged; no new native acceptance claim.

| MIDI note | Baseline mean WER | Late glide | Smoothed weights |
|---|---:|---:|---:|
| 48 | 0.9917 | 1.0500 | 1.0000 |
| 60 | 1.0917 | 1.1333 | 1.0500 |
| 72 | 1.0000 | 1.0000 | 1.0000 |

WER includes insertions and may exceed 1. These results are failed English recognition, not a listening pass. Repetitive “beep”, “wait”, “right” etc. must not be mistaken for successful phrase recovery. Same cached tiny.en, offline, beam 5, no expected-text prompt. Maintenance had removed its temporary runtime; only runtime dependencies were restored, not a new model. environment.json records versions. Within this run all paired variants share the same decoder/environment.

## Evidence and reproduction
- tools/nucleus_build.py creates candidates in build/nucleus-study without editing production code.
- tools/nucleus_scores.mjs --from-corpus reproduces exact scores without dictionary downloads.
- tools/nucleus_study.py [--variant smooth] renders new experiment recordings. --recognize uses only an existing cached model.
- tools/nucleus_analysis.py [--variant smooth] measures nuclei, glides and boundaries and summarizes recorded recognition.
- tests/nucleus_transition.c is a diagnostic guard currently failing in BOTH baseline/candidate; it is not wired into previously passed acceptance scripts.
- tools/nucleus_pack.py verifies all 36 WAV hashes and creates lossless baseline/candidate paired WAV.gz files. tools/nucleus_archive.py creates an experiment-only archive; existing firmware archives remain untouched.

The new evidence-preservation workflow reproduces only these new audio artifacts, checks them against recorded WAV hashes and backs up the experiment. It does not execute old CI/repair tests or install/use recognition models. Recognition JSONs are observed local results, not falsely labelled CI model runs.

## Exact next experiment
Test smoothing the **output band weights themselves**, keeping unweighted resonator states, instead of storing weighted energy inside resonators. Isolate that single change against the same transition cases and guard, then examine recognition only if it improves the acoustic boundary without failing headroom. This is a hypothesis, not an implemented fix. Do not rerun the rejected late-glide experiment or unrelated acceptance. Native/WASM/firmware publication remains blocked by intelligibility and original release gates.

Artifact preservation note: the independent job reproduced all 36 expected WAV hashes before packaging failed because the runner lacks ffmpeg. Packaging now uses Python's lossless gzip support for WAVs, avoiding an extra runner install. No recognition or old acceptance checks are repeated for packaging.
