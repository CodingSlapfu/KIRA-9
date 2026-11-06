# Browser QA — development studio
Executed in Chrome at the managed local preview, not a public deployment.
- Shared C/WASM preview reached SINGING and Playing the shared C vocal engine.
- Preview failed initially because AudioWorklet was unavailable in the HTTP preview context. Added a real shared-WASM render-to-AudioBuffer fallback; playback then succeeded. It limits fallback preview to 120 seconds to bound memory.
- Pronunciation/melody grid rendered per-word edits and validation succeeded.
- Unknown word qzxwvv was rejected with an explicit pronunciation-needed message.
- Found and fixed numeric option values (voice/style select controls initially appeared blank).
- Found and fixed Undo history capture on text editing; restored the prior draft.
- Reload preserved the exact restored lyric text.

Not certified: perceptual English intelligibility, musical quality, full voice/style repertoire, responsive mobile interaction, actual device transfer or public deployment. Browser evidence is not physical FM-1 evidence.
