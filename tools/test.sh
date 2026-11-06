#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p build
cc -std=c99 -Wall -Wextra -Werror -Wno-misleading-indentation -O2 -ffp-contract=off -Icore core/codec.c core/library.c core/engine.c core/tables.c tests/test_core.c -lm -o build/test-core
./build/test-core
cc -std=c99 -g -fsanitize=undefined,address -fno-omit-frame-pointer -Icore core/codec.c core/library.c core/engine.c core/tables.c tests/test_core.c -lm -o build/test-sanitized
ASAN_OPTIONS=detect_leaks=0 ./build/test-sanitized
cc -std=c99 -O2 -Icore tests/test_features.c core/engine.c core/tables.c core/codec.c core/library.c core/face.c -o build/test-features
./build/test-features
python3 tools/test_requirement_gate.py
python3 tools/requirement_gate.py --phase plan
