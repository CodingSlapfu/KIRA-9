# KIRA-9 — Vocal Engine and Physical Cybernetic Animation

## Performance DSP
English lyrics/words → normalized phoneme inventory → timed syllables and visemes → melodic note events → sample-accurate synthesis. Build an offline, bounded source-filter/formant English singer, with consonants, plosives, fricatives, nasals, diphthongs, coarticulation, stress, breath and natural consonant transitions. The web editor prepares detailed language timing; the FM-1 runs precompiled compact streams. No online model needed for standalone playback.

Separate **voice identity**, **singing technique/style** and **emotion**. Original presets cover deep, bright, airy, smoky, youthful, mature, synthetic; IDM, pop, house, trip-hop, R&B, ethereal ambient, experimental, vocoder; articulation, rasp, breath, fry, portamento, vibrato and controlled melisma. Musician-inspired *techniques*, never an unauthorized clone of a recognizable celebrity voice. Measure audible PCM uniqueness and intelligibility, not just non-zero audio. Optimize at 44.1 kHz within FM-1 deadlines.

## Face, expression and cybernetics
Original highly expressive cyberpunk anime female singer in an intimate close-up on the 240×240 display. Eyes, pupils, eyebrows, lids, lips, cheek servo plates, jaw micro-pistons and neck actuators articulate; vowel mouth shapes and consonant lip closures must follow the exact **same phoneme timeline as the voice**. Glances, blinks, emotion and mechanics are visibly animated, not decorations.

Rare **physical/neural misfires**: brief independent pupil saccade, cheek spasm, jaw realignment, delayed eyelid, tiny neck correction. These happen on the *character*, not the display: **NO scanlines, holograms, chromatic screen tears or screen glitches**. Sparse events, low amplitudes, min-gap scheduler, OFF/LOW/NORMAL control. Keep voice and MIDI timing completely invariant: rendering takes snapshots and may drop frames under load. Use small reusable sprites, dirty regions and measured RAM/CPU. Provide actual animated 240×240 previews of multiple phonemes, expressions and involuntary movements.

## Starter demos — original only
Target 8–12 compact copyright-cleared demo vocal performances if the measured partition allows. Planning concepts: Neon Awakening (synth-pop), Glass Heart (dream-pop), Ghost Frequency (IDM), After the Rain (trip-hop), Circuit Bloom (house), Electric Lullaby (ambient), No Gravity (R&B), Pale Aurora (experimental), Runaway Signal (dance) and Machine Dreams (robotic). Demos are factory-restorable and never overwritten by user material.

## Tests
Speech intelligibility listening fixtures; pitch/RMS/peak/click tests, note off/Stop, phoneme timing, transition glitches, 1-core fallback, RAM/CPU; deterministic frames from real viseme events; hard assertion audio buffers and clock don't change when character twitches. Hardware subjective quality and delivered LCD FPS remain owner-unverified until performed.