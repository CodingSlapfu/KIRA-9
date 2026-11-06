# Frozen listening kit access — 2026-11-06

Download KIRA-9-listening.html and open it in a browser locally. This is an offline research test, not a firmware, website or installer publication. Use headphones at a comfortable low starting volume. Choose the word heard or Unclear. Complete all 48 trials (or three blocks of 16). Progress is stored in the same browser. Export responses when done and return the JSON to the conversation; no answers are uploaded automatically. Avoid viewing the separate answer key before finishing.

Saved access: https://chatgpt.com/library?file_id=libfile_daa066d1c9fc819187398ba5dbe4d599&account_id=personal

Standalone HTML SHA-256: 59116b50a58c6ef490eca760eabaee2e96705b9b9d1d4c435d74359be2c10db0
Frozen source checkpoint: 919a713ab3ae7ba5ab56af63e4a217b2b282939d
Durable GitHub copy: `kira-9-development-backups`, `listening/919a713/KIRA-9-listening.html`.
All 48 embedded WAVs match the original answer-key hashes. No resynthesis, audio processing or recalibration was performed.

Validation: three synthetic grader tests passed (partial/confusion, complete/unclear, invalid/duplicate/unknown rejection). Node UI simulation passed 48 unique choices, progress recovery after 5 choices and completion. Simulation uses Unclear solely as synthetic tooling input and persists no participant response file. No human listening results or preference scores exist. Audio playback/headphone/device perception remains for the human evaluator.

Grading: `python3 tools/english6_grade.py responses.json --key build/english6/listening/answers.json`. Recover the frozen key from the verified experiment archive if absent. Preserve the original response file; report participant provenance, coverage, word confusions and register separately. Do not combine repeated exports as independent participants. One listener's forced-choice results are diagnostic, not a release pass. No synthesis changes until a specific perceptual finding supports a bounded experiment.
