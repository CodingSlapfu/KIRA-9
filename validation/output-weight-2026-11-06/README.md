# Output-band-weight experiment — November 6, 2026

Baseline d40d558 / production DSP 1641726b. Same sole owner work-160cc0e6fa30-resume-2. Production core/app/studio are unchanged. No AQUORA edits, publication, old recording regeneration or old acceptance replay.

## Single change and controls
Three additional float states smooth OUTPUT formant-band weights at the existing .003 control rate. Raw resonator input gains and feedback states stay unweighted. No nucleus/glide, pitch, duration, voice, style, excitation or output-level changes were combined with it. Generated candidate/header/bridge live only in build/output-weight-study; tools/output_weight_build.py reproduces this isolated candidate.

288 feedback-state hash comparisons over a novel short phoneme probe match the baseline. Only three new candidate transition recordings were rendered (MIDI 48/60/72). Their comparisons reuse the preserved baseline WAVs and scores, checking those three file hashes; the old 36 recordings were not regenerated.

## Outcome
- MIDI 72 M→IY exact-edge step: 0.170288 → 0.002289. The ±3ms maximum falls .170288 → .015015. P/T/K boundaries improve too; results.json records all register/boundary values.
- Full-velocity transition guard: **562 limiter hits**, peak .940000, across **53,673,984 output samples**; stop tails pass. Recorded baseline has 746 hits; previous input-weight candidate 506. Those earlier guards were not rerun. A lower hit count is NOT a headroom pass.
- **Recognition NOT RUN.** The headroom prerequisite failed, so no model was loaded, downloaded or installed. No new recognition or intelligibility improvement is claimed.
- **Candidate rejected for promotion; production DSP unchanged.** No extra smoothing-rate or output-gain search was attempted. Only the new source/evidence will be archived, without rerunning successful CI or old backups.

## Reassessment: end this parameter-tuning line
The experiments show that controlling band-weight discontinuities improves a mechanical artifact, but neither input nor output smoothing solves transition headroom. Earlier timing/glide/EQ passes also did not establish English word recovery. The evidence does not prove that all formant synthesis is incapable of intelligible English; it shows that this uncalibrated backend is not ready, and more small weight/rate adjustments are not a justified plan.

Before another vocal-backend change:
1. Establish a credible English reference/control and a phoneme-identification/listening protocol across registers. The current tiny.en failures on synthetic singing cannot be the sole optimization target. Reuse the existing recognizer only if needed; no model-installation loop.
2. Instrument **unclamped transition energy** and resonator state/pole trajectories to locate energy carry/overshoot. Post-limiter hit counts and spectral centroid alone cannot identify that cause. Do not merely lower output gain to conceal it.
3. Make a bounded backend decision: compare the current implementation with a small, original reference-driven English source/filter prototype using validated excitation, consonant and coarticulation targets plus stable time-varying filter transitions. Keep the score/phoneme/viseme/control interfaces and all completed platform/MIDI/editor/storage work. Do not begin a broad product rewrite or copy GPL/Japanese voicebanks/art.
4. Predefine how phoneme/word recovery and transition safety will be judged, then decide whether this backend can meet the existing requirements. No claim of success from plots, hashes or nonzero PCM.

Next work is this synthesis reassessment and reference validation—not another smoothing constant, gain multiplier or rejected-glide rerun. Intelligibility and all original release gates remain OPEN. Physical FM-1 quality/CPU remain owner-unverified.

## Verified checkpoint preservation
Source: 889f674514e0bd0ad594f003bf48b50b85fe89c0. Permanent backup commit: 61ca84fe38dbf3b27bbfa9cab4f1fd720121d0b5. Archive: experiments/889f674514e0bd0ad594f003bf48b50b85fe89c0-output-weights.zip. ZIP SHA256: 167b589a9d8dd7680fa593fabcfce695225644c99896dfb904b5696794238c3c. Independently downloaded this NEW archive and checked source identity and all 17 members; no previous archives were reverified. Recognition was not run, candidate not promoted, production DSP unchanged.
No old CI, full acceptance or successful backup tests were rerun; new experiment archive only.
