#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p build
# One noninteractive owner per checkout; the descriptor closes automatically on exit.
exec 9>build/verify.lock
flock -n 9 || { echo 'Another verification owns this checkout'; exit 75; }
./tools/test.sh
python3 platform/tools/build.py app --host
mkdir -p build/panel
app/build/host/kira-9_host tests/panel.txt build/panel
app/build/host/kira-9_host tests/midi_recovery.txt build/panel
if [ "${1:-}" != "--vocal" ]; then
app/build/host/kira-9_host tests/library_safety.txt build/panel
cc -O2 -std=c99 -Wno-unused-function -Iplatform/include tests/storage.c -o build/storage-app
build/storage-app
fi
cc -shared -fPIC -Wl,--no-undefined -O2 -ffp-contract=off -Icore core/engine.c core/codec.c core/library.c core/tables.c core/face.c studio/bridge.c -o build/libkira.so
python3 tools/audio_fixture.py
if [ "${1:-}" != "--vocal" ]; then
cc -std=c99 -Wall -Wextra -Werror -Wno-misleading-indentation -O2 -Icore tests/transfer_device.c core/transfer.c core/library.c core/codec.c -o build/transfer-device
node tests/transfer.mjs
fi
./tools/build_web.sh
node tests/parity.mjs
python3 tools/build_dictionary.py
node tests/web.mjs
python3 tools/vocal_comparison.py
python3 platform/tools/build.py app --web
python3 platform/tools/build.py app
python3 tools/package_checkpoint.py
