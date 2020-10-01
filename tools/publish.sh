#!/bin/bash

set -e

rsync -av --exclude-from=.gitignore \
	--exclude=.git/ \
	--exclude=.gitmodules \
	--exclude=docs/captures/ \
	--exclude=reference/firmware/ \
	--exclude=example/scripts/ \
	--exclude=firmware/ \
	--exclude=docs/trailer.* \
	./ ../../../github.com/khimaros/ambit/
