# Optional KIRA-9 performance profile v1
Ordinary standards-compliant MIDI peers need no extension. MIDI notes play the local voice; words are stored on KIRA-9, not carried as note text. Clock is 24 PPQN. USB and individual BLE links are distinct source authorities. Follow BLE accepts BLE only; Auto latches the first explicit Start, never an incidental clock. Stop in Auto releases the authority. USB, Bluetooth central and Bluetooth peripheral are not echoed into each other.

Optional CC assignments (zero-based values): CC20 saved phrase 0–7; CC21 saved word 0–7; CC22 factory song 0–7; CC23 voice identity 0–6; CC24 style 0–7; CC25 emotion 0–3. These are normal MIDI CCs, not proprietary pairing. Song/phrase cues start local phoneme timelines at receipt; a host can place cues on its chosen bar. MIDI Start/Continue/Stop, SPP, CC120/123 panic, CC1 vibrato, CC2 breath, program voice selection, and pitch bend are accepted.

Two linked BLE peers have distinct source IDs, so a second clock cannot double the selected clock. BLE disconnection releases following notes. USB clock loss times out after two seconds. Physical BLE latency/jitter, CoreMIDI/iPad routing and disconnect behavior remain owner-unverified.

Current limitations: local-master clock output runs from the 1 kHz timer and needs physical jitter acceptance. PRESET on the MIDI page chooses OMNI or input channel 1–16. Sync drift/jitter estimation and Auto behavior still need extended acceptance. Do not call this profile release-complete.
