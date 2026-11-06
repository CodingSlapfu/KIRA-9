# Issue #2 — bounded English articulation and stress

Baseline: 13aca33. Original implementation informed by the research hypotheses in GitHub Issue #2; no Miku source, tables, voicebanks or character assets were copied.

Changes: P/T/K/B/D/G and CH/JH use independently chosen millisecond closure/burst/tail phases. Long events no longer stretch closures/bursts; short events compress to fit before the next phone. Noise bursts taper continuously; sustained fricatives have attack/release ramps; nasal and approximant onsets are softened. The face's plosive release reads the same phase helper. Vowel sustain, independent voice/style and MIDI remain intact.

Compiler: consonants receive class-specific millisecond budgets converted at the current BPM, with a vowel reservation for short words. The dictionary preserves CMU 0/1/2 lexical syllable stress; explicit user stress overrides it. Weak function words default to 48 ticks, content words 96; default inter-word gap is 6 ticks instead of 24, with explicit duration/breath/melisma controls retained. No lyric text changes.

Evidence: tests/test_articulation.c checks fixed phase timing over 100/500ms events, short bounds, actual PCM closure and burst, identical early PCM at four pitches and clipping safety. tests/vocal_timing.mjs checks lexical primary/unstressed syllables, explicit override, vowel reservation and 60/120/180 BPM consonant timing. Optimized and ASan/UBSan core/feature tests pass.

Audio: python3 tools/build_dictionary.py, then python3 tools/vocal_comparison.py creates three baseline/updated English phrases, WAVs, comparison.wav and metrics in build/vocal-comparison (included in the checkpoint ZIP). Each pair uses the baseline/updated compiler and C DSP; each phrase plays before then after with one second silence. Exact hashes and peak/RMS/adjacent-step/callback values are in metrics.json. Optional tools/transcribe_comparison.py uses faster-whisper tiny.en without a supplied lyric prompt.

Measured local host callback median: 10.862us baseline, 11.688us updated (~7.6% increase). Phrase peaks stay 0.263–0.273 updated, with no clipping; this is not an FM-1 performance claim. Maximum adjacent sample step did not consistently fall, so no crackle-removal claim is made. Independent native size/performance acceptance is still required.

**Intelligibility acceptance remains OPEN.** The available tiny.en recognizer produced empty text for both baseline and updated singing on all three phrases. This is inconclusive, not evidence of improved word recognition. The changes establish measurable articulation/stress corrections, not a certified natural or intelligible English voice. Further acoustic improvement and listening/transcription evidence remain release blockers; physical speaker/headphone assessment belongs to the owner.
