#!/bin/bash

set -e

# FIXME: this script should be merged into bin/ambit_image_display
find "$@" -type f -name '*.raw' | sort -V | while read asset; do
	echo "[*] Displaying asset $asset"
	bin/ambit_image_display "$asset"
done
