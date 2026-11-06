# Focused acoustic investigation — November 6, 2026

Baseline d8bff4d; same authorized owner work-160cc0e6fa30-resume-2. Existing CI repair and 780-member archive validation were not repeated. No AQUORA or completed editor/transport/storage redesign.

## Measured acoustic faults
The preserved updated phrase has /iy/ energy above 1.5kHz of about 0.4%, /ih/ 0.9%, and voiced /z/ above 3kHz only 2.3–3.5%. The parallel first resonator dominates: distinct upper vowel formants and frication cues are masked. This is a demonstrated spectral fault, not proof of the sole cause of poor word recognition.

Original targeted correction: three per-phone resonator weights (vowels/approximants .25/4/7; nasal 1/.25/.1; fricative .05/2/4). Apply the same balance to harmony. Preserve existing glottal excitation, timing, voice/style controls and seven formant banks. A small .035-amplitude triangle voicing bar under /z zh v dh/ preserves low-frequency periodicity independently of upper-band noise. It follows the same oscillator/envelope, with no extra state or allocation.

## Controlled experiments and rejected alternatives
On the same phrase, moderate balance increased /iy/ >1.5kHz energy from .004 to .575 and /ih/ from .009 to .718; /z/ upper noise energy increased to ~.97 before adding the periodic bar. The final bar deliberately restores voicing rather than maximizing a high-frequency ratio. Isolated steady-phone measurements, with identical pitch, are in analysis.json (do not confuse these with phrase values).

Rejected: a stronger .2/6/9 voiced balance clipped 0.0072% of the seven-voice/39-phone/four-pitch grid (peak limiter .94). A 70% original excitation/30% band-limited saw experiment reduced /iy/ upper-band recovery versus balance alone (.017 vs .155 in that experiment) and did not improve recognition. Neither source rewrite nor stronger gains were retained.

The moderate candidate alone weakened /z/'s low voicing cue: low-band RMS .00340 baseline → .00049. The retained small bar restores it while preserving frication. The final isolated /z/ low-energy fraction is ~.558; nasal /m/ remains concentrated below 1kHz. /s/ and /sh/ spectral centroids remain separated by over 500Hz.

## Reproducible acceptance and evidence limits
python3 tools/acoustic_comparison.py builds the baseline and current real C DSP, uses identical timed scores (no compiler/timing change), renders six phrase pairs and comparison.wav, and runs the 7×39×4 phoneme/pitch grid. The first three phrases are preserved fixtures; the final three are held-out contrasts. Audio hashes, spectral ratios, clipping and host callback distributions are in build/acoustic-ab/analysis.json; recordings are included in the new checkpoint archive.

The focused verification path runs affected audio stability/sanitizer/articulation, host playback, seven timbre fixtures, native/WASM PCM parity, acoustic probes, emulator/native build and new checkpoint packaging. It does not replay storage power-cut, repaired CI regression or old 780-member backup tests. New backup preservation verifies only the new archive. No new transcription models are installed; optional tools/transcribe_acoustic.py refuses to run without the existing tiny.en cache.

Spectral contrast and headroom improvements do not establish intelligible English. Human/recognition acceptance remains open until the new recordings support it. No release publication. Physical FM-1 quality/CPU remain owner-unverified.

Initial cached-model result: baseline phrase 0 returned empty text; the final produced unrelated/repeated words (“Wait for me to play…”). Held-out “see she sue shoe” returned empty text in both variants. These are failures, not recognition improvements. Default decoding/no expected-text prompt was used. Acoustic corrections are retained for their measured spectral and headroom benefits; English intelligibility remains unresolved.

Maximum-velocity follow-up: a 53,673,984-sample scan over seven voices, eight styles, all phones, four pitches, harmony +7 and velocity 127 found 82 limiter hits in the first candidate. Reserve ~0.8dB of output headroom (main .44→.40, harmony .12→.109); tests/acoustic_headroom.c now requires zero limiter hits. This new failure justified the affected follow-up, not a replay of the repaired CI or storage tests.
