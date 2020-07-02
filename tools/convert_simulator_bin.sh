#!/bin/bash

set -e

[[ -z "$1" ]] && echo "Usage: $0 <name>" && exit 1

simulator="bin/ambit_$1_simulator"
native="bin/ambit_$1"

sed 's/ambit\.simulator\.Controller/ambit.Controller/g; /import ambit\.simulator/d' "$simulator" > "$native"

chmod +x "$native"

echo "[*] Converted ${simulator} to ${native}!"
