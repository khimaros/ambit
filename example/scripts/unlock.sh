#!/bin/bash

BUZZ_HOST=""
BUZZ_SECRET=""
BUZZ_FROM=""

if [ "$1" = "set" ]; then
	echo "[+] Door unlock set to ${AMBIT_VALUE}" >&2
	echo "OPEN: ${AMBIT_VALUE}m"
	echo "${AMBIT_VALUE}" > /tmp/ambit-unlock-value
fi

if [ "$1" = "open" ]; then
	OPEN_MINUTES=$(cat /tmp/ambit-unlock-value)
	echo "[+] Door unlocked for ${OPEN_MINUTES}" >&2
	curl "https://${BUZZ_HOST}/protected/sms?Secret=${BUZZ_SECRET}&From=%2B${BUZZ_FROM}&Body=${OPEN_MINUTES}%20minutes" &>/dev/null
	echo "UNLOCKED!"
fi

