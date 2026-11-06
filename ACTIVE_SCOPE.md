# KIRA-9 — Authoritative Product Scope
**Revision 2026-11-05.** Distinguish design requirements from actual implementation.

## Product vision
A complete **cybernetic female vocalist** on the orange FM-1. Close-up face fills the 240×240 LCD; expressive singing with synchronized English mouth shapes, lids/eyes, facial expressions, exposed mechanical jaw/eyelid/cheek/neck actuators and subtle physically motivated micro-spasms. The audio is a self-contained original vocal instrument, not dependent on playback of backing songs. A user can load and sing complete demo/custom songs, live-key play, words, hooks, or phrase banks. With optional MIDI, she follows AQUORA or any compatible MIDI host.

## Product pillars / mandatory first release
1. **Standalone:** on-device internal clock, sequence/song arranger, melody notes and timed lyrics, transport, keyboard live performance, song/phrase/word modes. Completely functional offline; preloaded original demo collection (target 8–12, subject to measured size/quality).
2. **English vocal DSP:** efficient phoneme→syllable→word→phrase source/filter synthesis, appropriate English consonants and transitions, timing/breath/glide/vibrato/dynamics/voice-type selection. High perceived intelligibility and musicality prioritized over claiming neural/TTS realism on restricted hardware.
3. **Voice/style repertoire:** independent voice identity, singing genre and emotion/expression; pop, house, IDM/glitch, trip-hop, ethereal/ambient, R&B/soul, experimental and robotic/vocoder with original presets. Musical technique may be influenced by named singers, but do not copy recordings, voicebanks, or present unauthorized exact celebrity impersonation as a bundled feature. Include voice-morphing only if stable/performance-safe.
4. **Living animated face:** expressive eyes, brows, eyelids, jaw/lips driven from actual phoneme envelopes; actuators visibly follow muscles. Independent occasional mechanical/neurological-looking twitches; no scanlines, hologram artifacts, full-screen corruption or audio degradation. High-quality optimized 240×240 render.
5. **Generic MIDI:** standard BLE MIDI peer discovery/connect/clock/notes/program/CC/expressive controls; optional iPad USB hub/CoreMIDI MIDI IN+OUT. External master and local master, deliberate sync takeover, clock-safe stop/continue and no hung notes. BLE direct doesn't require iPad.
6. **Website/editor:** separate KIRA-9 site with interactive face and voice emulator, lyric idea→original full song generator, custom lyric paste/import, edit verse/chorus, pronunciation corrections, notes/rhythm/phrase assignments, original demo library, export/import, bounded device transfer, app-independent flash installer and recovery instructions.
7. **Library:** immutable factory demos; independently saved songs, phrases, words, pronunciation overrides, voice settings and projects. Compact serialized phoneme/note events, index and dedupe as appropriate, CRC/versioning, capacity reporting, safe atomic-ish save with power interruption testing, export backup, flash partition isolation and migrations.
8. **Accessible workflow:** expressive face PLAY screen, clear pages and K1–K4 live labels/values; MENU/SONG/VOICE/LYRICS/PHRASES/MIDI/LIBRARY/PERFORMANCE/SETUP as implementable, quick-find, no duplicate parameters, SAVE saves, SEL confirms actions, critical changes protected. Startup identity and battery/performance indicators.
9. **Engineering/release:** audio interrupt always wins; bounded nonblocking BLE/USB; no memory leaks/radio starvation; DSP test WAV/phoneme intelligibility, emulator animation checks, native firmware, verified web deployment and GitHub backups. Physical FM-1 testing left to owner.

## Non-goals for initial version
- No generative backing band required (AQUORA supplies music when wanted).
- No dependence on internet to sing on device.
- No hologram/scanline/pixel-corruption effect representing a facial glitch.
- No unlimited flash promises, or arbitrary full-language neural voice clone on the device.
- No hard-coded pairing exclusively with AQUORA/KIRA-9 or bespoke non-interoperable MIDI transport.
- No direct physical TRS link between FM-1s required; USB hub/iPad route is valid.

## Two active projects only
- AQUORA: existing sound-healing generator. Radio ownership rule AIR ↔ BLE MIDI exclusive. Generic protocol work tracked at https://github.com/CodingSlapfu/AQUORA/issues/31.
- KIRA-9: new independent singer and website. Future devices can adopt the same generic MIDI spec, but do not create or resume other projects to fulfill this scope.