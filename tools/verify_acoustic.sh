#!/bin/sh
# Focused acceptance for DSP-only acoustic changes; no replay of repaired CI/storage gates.
set -eu
cd "$(dirname "$0")/.."
mkdir -p build/panel
exec 9>build/verify.lock
flock -n 9 || exit 75
cc -std=c99 -Wall -Wextra -Werror -Wno-misleading-indentation -O2 -ffp-contract=off -Icore core/codec.c core/library.c core/engine.c core/tables.c tests/test_core.c -lm -o build/test-core
build/test-core
cc -std=c99 -g -fsanitize=undefined,address -fno-omit-frame-pointer -Icore core/codec.c core/library.c core/engine.c core/tables.c tests/test_core.c -lm -o build/test-sanitized
ASAN_OPTIONS=detect_leaks=0 build/test-sanitized
cc -std=c99 -O2 -Icore tests/test_articulation.c core/engine.c core/tables.c core/codec.c core/library.c -o build/test-articulation
build/test-articulation
cc -O2 -ffp-contract=off -Icore tests/acoustic_headroom.c core/engine.c core/codec.c core/library.c core/tables.c -o build/acoustic-headroom
build/acoustic-headroom
python3 platform/tools/build.py app --host
app/build/host/kira-9_host tests/panel.txt build/panel
cc -shared -fPIC -Wl,--no-undefined -O2 -ffp-contract=off -Icore core/engine.c core/codec.c core/library.c core/tables.c core/face.c studio/bridge.c -o build/libkira.so
python3 tools/audio_fixture.py
./tools/build_web.sh
node tests/parity.mjs
python3 tools/build_dictionary.py
python3 tools/acoustic_comparison.py
python3 platform/tools/build.py app --web
python3 platform/tools/build.py app
python3 tools/package_checkpoint.py
