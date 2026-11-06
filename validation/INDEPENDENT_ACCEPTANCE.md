# Independent development acceptance receipt
Source: 8d9226d5501c41c862291dd7bf0185a7494eda78 (tree 74d2e31e43f5da9cc114d25bab068ca9128b585e). Local and remote trees matched exactly.

GitHub Actions run: https://github.com/CodingSlapfu/KIRA-9/actions/runs/42164648668 — SUCCESS. Independent Ubuntu runner built host, shared-WASM voice, browser emulator and native firmware, ran normal/ASan/UBSan core regressions, panel/modes/local-clock/SAVE/reboot/source-authority checks, 725 actual-map power-cut injections, seven distinct voice fixtures, native/WASM PCM parity (51200 samples, error 0), and all eight full demo playbacks. The traceability release gate rejected all 23 unfinished P0 rows as intended. A successful DEVELOPMENT run is not release acceptance.

Native: 197424-byte app; development identity FM-1_7400; .fwsc 614938 bytes. Native FWSC SHA256 7c0ded6d7f6a4481a89069155805c344de3079101976e6bbf759c2365439d6ec matched the local build byte for byte. RAM code 5444/32768 bytes, .data+.bss 65624/98304, pool 121476/344064. These are linker numbers; physical CPU/FPS/DMA tests remain unverified.

Independent backup: branch kira-9-development-backups, checkpoints/8d9226d5501c41c862291dd7bf0185a7494eda78.zip (5651626 bytes). ZIP SHA256 ce2ee7834a1c2e0619a6cb7d1cd868a47a80ca127e68b5c74f04f4f308fae714. Downloaded separately from GitHub, verified ZIP digest and every one of the 737 manifest member hashes. Includes application/dependency source, native package/ELF, full local website/dictionary/WASM and emulator. Source checksum manifest marks release_accepted=false.

Run artifact 13478172272 is a second downloadable copy; versioned backup branch is independent of the artifact's 90-day expiry.

No production site, installer or accepted firmware release was published. Complete NEXT_BUILD_ACTIVE.md; do not restart passed implementation. The project owner is paused, with no active native build or publisher. Metadata-only checkpoint commits skip the expensive development workflow; feature changes still run it.
