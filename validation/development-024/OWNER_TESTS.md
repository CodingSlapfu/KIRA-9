# KIRA-9 v0.2.4-dev hardware checks

Export a device backup before updating. The testing ZIP includes the prior
v0.2.3 firmware and rollback page. Older firmware may reset settings written
by this build. Restore the pre-update backup after rolling back.

1. On the SONG page, select each demo with K1 and use PLAY. Listen across two
   loop boundaries. On the PLAY page, press SEL for vocals only, then toggle
   music back on mid-phrase. Check that the singer and tempo keep going.
2. On PLAY, K1 controls vocal level and K2 music level. K3 selects the root
   (C through B) and K4 selects major, natural minor or major pentatonic.
   Select LIVE on the SONG page to play the voice with the FM-1 keyboard.
3. On VOCAL FX, ALGO selects Off, Natural, Pop or Hard. PRESET adjusts
   strength. Hold SEL while turning PRESET to adjust retune speed.
   SEL toggles Perfect Key. K1–K4 control chorus, echo, delay and reverb.
   Turn up each effect separately and try the controls while a demo plays.
4. On MIDI, enable BLE and pair a wireless controller using SEL. In Live,
   play a chromatic line, hold sustain, release and disconnect. Check for
   stuck notes. Reconnect with the second role also connected if available.
   With an external BLE clock, test Start/Stop and repeated demo looping.
5. Compare a lyrics demo to v0.2.3 at the same volume. Listen for
   intelligibility, sustained vowel tone and expression. Watch the mouth
   during plosives, singing and closed-mouth humming. Check Performance
   for overruns with BLE, animation and vocal FX active.

Host tests cover transport, pitch targeting paths, FX routing, bounded output
and source ownership. Device pairing, audio timing, flash/recovery and
subjective voice and visual acceptance require a physical orange FM-1.
