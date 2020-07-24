#!/usr/bin/env python3

import sys

import intelhex

if len(sys.argv) != 3:
    print('usage:', sys.argv[0], '<bin> <hex>')
    sys.exit(1)

ih = intelhex.IntelHex()

ih.loadbin(sys.argv[1])

with open(sys.argv[2], 'w') as f:
    ih.write_hex_file(f)

