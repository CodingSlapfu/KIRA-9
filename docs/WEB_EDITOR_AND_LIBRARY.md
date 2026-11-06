# KIRA-9 Web Songwriting Studio, Library, and Transfer

## Independent editor and website
Separate KIRA-9 brand/site/release from AQUORA: landing page, original character preview, browser voice+face emulator, editor, firmware installer and documented recovery. All standalone singing works offline without web/network.

## Two equally important lyric paths
**Idea → full song:** genre/mood/story/keywords/length into original verse/chorus/bridge/outro lyrics. Allow section edits/rewrite and preserve human edits. If AI service is used, disclose provider, obtain necessary keys/permission and provide honest template fallback. **Lyrics alone are NOT 'ready to sync'** until phonemes, vocal melody, note lengths, expression and timed phrase alignment are prepared.

**My lyrics:** paste/import owner's own text, preserve wording by default. Parse sections, add editable phonemes and syllable breaks, per-word pronunciation overrides, breath marks, phoneme lengths, note assignment via piano roll or optional MIDI import. Never rewrite user lyrics unless requested.

## Musical and facial preview
Editable section grid, notes and timing, tempo/key, phoneme track, stress, voice identity, style, emotional delivery, harmony, morphing, phrase cues, quantize, undo/redo. Browser preview must produce genuine rendered vocal audio (e.g. the same DSP in WASM) and viseme animation, not fabricated waveform visuals. Distinguish browser proof from physical hardware.

## Device library and capacity
Factory 8–12 demo goal after actual flash measurement, user **songs, phrases, words, ad-libs, pronunciation entries, voice presets** and tagged performance scenes. Compact reusable phoneme/note/event assets; device free-space meter, safe overwrite warnings, user deletion, factory-demo restore, versioned CRC/length, interrupted-write recovery, migration and flash-wear protection. Website can hold larger archives through export/import; don't claim cloud backups without a connected provider and explicit persistence.

## Transfer and song synchronization
Reliable framed website-to-device transfer over suitable supported USB MIDI/SysEx data protocol, with ACK/retry/CRC, bounded chunk size and no audio-ISR blocking; optional BLE transfer if proven technically feasible. Device songs are editable and reimportable. KIRA-9 can still sing without a USB cable after transferring. In MIDI Follow, local lyric phrase cues are selected by standard program/CC assignments while externally supplied transport and melody coordinate the singer. Any MIDI-capable peer is allowed.

## Verification
Original/demo/user lyrics roundtrip, bulk transfer, corruption/power-cut scenarios, actual preview-to-device phoneme/viseme parity, full-capacity behavior and recovered library after reboot. Audio/UI/installer all traced to an accepted source commit, exact build version and tested package.