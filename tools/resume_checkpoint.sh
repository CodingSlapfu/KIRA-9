#!/bin/sh
# Reconstruct missing artifacts after 13aca33's native-only failure, preserving passed tests.
set -eu
cd "$(dirname "$0")/.."
mkdir -p build
exec 9>build/verify.lock
flock -n 9 || exit 75
# The failed run passed these exact core/editor/test inputs. Refuse stale reuse.
git fetch origin 13aca33db7491a67df6de3fbc912c48da3462c92 --depth=1
git diff --exit-code 13aca33db7491a67df6de3fbc912c48da3462c92 HEAD -- core studio tests factory
python3 platform/tools/build.py app --host
mkdir -p build/panel
app/build/host/kira-9_host tests/midi_recovery.txt build/panel
cc -shared -fPIC -Wl,--no-undefined -O2 -ffp-contract=off -Icore core/engine.c core/codec.c core/library.c core/tables.c core/face.c studio/bridge.c -o build/libkira.so
python3 tools/audio_fixture.py
./tools/build_web.sh
python3 tools/build_dictionary.py
python3 platform/tools/build.py app --web
python3 platform/tools/build.py app
python3 tools/package_checkpoint.py
