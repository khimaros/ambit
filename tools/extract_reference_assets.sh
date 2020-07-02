#!/bin/bash

set -e -o pipefail

SCREEN_WRITE_REGEX='^{"screen_write":[[:digit:]]*}'

PCAP_PATH="$1"
OUT_DIR="$2"

# FIXME: this is pretty inefficient. it parses the entire
# pcapng file three times per image extraction.
i=0
tshark -r "$PCAP_PATH" -2 -R 'usb.data_len > 16000' | while read line; do
	(( i += 1 ))
	echo "[*] Processing capture frame #$i ..."
        screen_number=$(tshark -r "$PCAP_PATH" -2 -T fields -e usb.capdata \
                -R 'usb.data_len > 16000' -Y "frame.number == $i" \
		| xxd -r -ps | grep -a -o -P "${SCREEN_WRITE_REGEX}" | jq .screen_write)
	echo "[*] Found screen image ${screen_number} in frame ${i}!"
	raw_path=$(realpath --relative-to=${PWD} "${OUT_DIR}/${screen_number}.raw")
        tshark -r "$PCAP_PATH" -2 -T fields -e usb.capdata \
                -R 'usb.data_len > 16000' -Y "frame.number == $i" \
                | xxd -r -ps | sed "s/${SCREEN_WRITE_REGEX}//" > "${raw_path}"
	echo "[*] Finished writing screen image to ${raw_path}"
done
