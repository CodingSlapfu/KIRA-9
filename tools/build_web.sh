#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
: "${EMCC:=emcc}"
"$EMCC" -O2 -ffp-contract=off -Icore core/engine.c core/codec.c core/tables.c studio/bridge.c --no-entry -sSTANDALONE_WASM -sINITIAL_MEMORY=2097152 -sSTACK_SIZE=65536 -Wl,--export=web_init -Wl,--export=web_input -Wl,--export=web_load -Wl,--export=web_demo -Wl,--export=web_stop -Wl,--export=web_voice -Wl,--export=web_render -Wl,--export=web_viseme -Wl,--export=web_tick -Wl,--export=web_playing -o studio/kira.wasm
