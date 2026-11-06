# CI failure diagnosis — November 6, 2026
Failed run: 42168544653, source 8a0fba0, job 127730675260.

The backup error `cp: cannot stat build/checkpoint/KIRA-9-development-checkpoint.zip` was secondary. Verification stopped at `tools/audio_fixture.py`: its host shared library lacked `core/face.c`, leaving `k9_face_render` unresolved. The default GitHub shell was `bash -e`, and piping verification through tee without pipefail hid that failure. The native/package stages in that run did not execute. Its successful core, sanitizer, panel and 725 power-cut results remain valid only for that source; they are not a complete acceptance claim.

Corrections: include the actual shared renderer in the host library, reject unresolved symbols at link time, use explicit bash pipefail in CI, require and checksum the ZIP before declaring verification successful, and move preservation to a separate dependent job. That job verifies source identity and every member hash, never rebuilds, rejects replacing a different existing archive for the same SHA, and checks the pushed remote ref. ZIP member timestamps/order are deterministic. A failed preservation job can now be rerun alone using the existing accepted artifact.

The same existing owner/lock was resumed. Unpublished source changes were preserved. No AQUORA files were touched.
