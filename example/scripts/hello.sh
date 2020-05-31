#!/bin/bash

PLACE="${1:-WORLD}"
VALUE="${AMBIT_VALUE}"

echo "[+] GREETING: ${PLACE}!" >&2
echo "[+] CURRENT VALUE: ${VALUE}" >&2

echo "${PLACE}!"
