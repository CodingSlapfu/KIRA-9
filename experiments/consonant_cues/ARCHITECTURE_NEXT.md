# Architecture reassessment after actual human evidence

The 15/48 single-listener result is poor for both engines. Six bands, calibrated gain and differentiated excitation did not solve English phoneme identity. More resonators alone are not a justified route. Head/had and heed/hid confusions require accurate time-varying vowel identity; consonant confusion also implicates release/aspiration/transition timing. These are hypotheses, not causal conclusions from one observation per cell. Naturalness was not measured at all.

The new consonant-only trial improves physical cue separation and retains byte-identical vowel control recordings, but fails the full raw-headroom gate inherited from baseline. It is not a new accepted voice. Its /s/ centroid (~12.9kHz) is high and the measured separation alone is not a desirable-human-spectrum or intelligibility pass. Stop here rather than tune noise until an acoustic metric looks better.

## Recorded English transitions/residuals: qualified next direction

Primary references inspected November 6, 2026:

- CMU ARCTIC technical report, Appendix A: https://festvox.org/cmu_arctic/cmu_arctic_report.pdf . Search-retrieved primary report states BSD-style use/modification/distribution conditions and recording-talent distribution waivers. Direct PDF fetching timed out/502; this is NOT an independently downloaded selected-voice license receipt. Before importing any bank, fetch that exact bank's COPYING, immutable source/version and hashes. Retain required notices and identify modifications. No external recording was downloaded/imported in this run.
- FestVox diphone construction chapter: https://www.cs.cmu.edu/afs/cs/user/lenzo/html/areas/papers/festvox/festvox_5.html . Inspected primary text: diphones model phone-to-phone transitions, coverage grows roughly as inventory squared, residual-excited LPC requires waveform, pitchmark and coefficient preparation. Natural coarticulation extends further than one transition; concatenation does not guarantee natural singing.
- Flite runtime COPYING: https://github.com/festvox/flite/blob/master/COPYING . Primary license inspected. Runtime licensing and a selected voicebank's licensing are separate. No Flite implementation copied. Avoid assuming any downloadable MBROLA/HTS/other converted bank inherits a generic runtime license.

Proposed original tiny prototype: offline extract a SMALL verified-licensed, single-speaker set of /hVd/ and /s,sh,p,b/→/iy/ transitions. Fit stable LPC envelopes offline, retain the recording's residual/aperiodic release, implement original pitch-synchronous residual overlap/add plus stable reflection-coefficient interpolation at 16kHz, then bounded resampling to44.1kHz. Sustain a representative vowel residual/envelope region; preserve onset and coda durations while changing sustain pitch/duration. Do not simply play a phrase recording faster to change pitch. Keep the existing phoneme/event interface behind an isolated adapter. No whole-language TTS runtime, lexicon/editor/MIDI rewrite or sampled-song workaround.

## Explicit prospective budget (assumptions, not measured capacity)

| Item | Bounded pilot target | Full-inventory illustration |
|---|---:|---:|
| Transition count | 16 | 40×40 =1600 before phonotactic pruning |
| Stored mean duration | .12s | .12s |
| 16kHz, 8-bit residual | 30,720B | 3,072,000B |
| LPC12, 100Hz, int16 coefficients | 4,608B | 460,800B |
| 16-byte unit index | 256B | 25,600B |
| Total before pitchmarks/headers | 35,584B | 3,558,400B |

Pilot storage ceiling64KiB including notices, pitchmarks and metadata; runtime extra RAM ceiling8KiB; 2×1024-sample int16 overlap buffers consume4KiB, leaving4KiB for resampler/filter/unit state and flash read staging. LPC12 at16kHz means192k coefficient multiply-accumulates/s before interpolation, residual pitch work or resampling. These arithmetic counts do NOT prove FM-1 timing. Target host median incremental cost <=1.25×baseline, zero heap allocation/audio blocking, kernel R3 evidence and eventually physical callback under5.805ms with existing face/radio workloads.

Existing development linker receipt: validation/NATIVE_DEVELOPMENT.md reports historical data+BSS52,472/98,304B and pool19,204/344,064B, not a current guarantee. A multi-megabyte full bank cannot be assumed to fit firmware/flash; inspect current native map and immutable flash partitions before expanding the pilot. Preserve existing storage and update/recovery areas. Runtime-RAM budgets and voice-data flash capacity are distinct.

Evidence gates before promotion: offline reconstruction error and filter stability; forward/reverse transitions and full-velocity raw headroom<.90 across supported pitches/timbres; no hidden limiter hits; held-out word/phrase recognition; NEW blinded human consonant/vowel identification plus free-text unfamiliar phrases and naturalness ratings; pitch/duration changes without changed phoneme identity; native code/RAM/flash measurements; physical callback/flash latency. Same listener can compare but must be reported as repeated within-listener evidence, not another independent participant. No recognition-model reinstall or old trial replay.
