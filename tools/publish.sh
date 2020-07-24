#!/bin/bash

set -e

rsync -av --exclude-from=.gitignore \
	--exclude=.git/ \
	--exclude=.gitmodules \
	--exclude=docs/captures/ \
	--exclude=docs/FIRMWARE.md \
	--exclude=docs/HARDWARE.md \
	--exclude=reference/firmware/ \
	--exclude=example/scripts/ \
	--exclude=firmware/ \
	--exclude=docs/palette_* \
	--exclude=docs/trailer.* \
	./ ../../../github.com/khimaros/ambit/
