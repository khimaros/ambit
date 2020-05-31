#!/usr/bin/env python3

from ambit.flags import FLAGS

import json

from typing import Any, Callable, Dict, List, Tuple


def message_encode(messages: List[str], extra_data: bytes=bytes(())) -> memoryview:
    json_messages = []
    for message in messages:
        json_message = json.dumps(message, separators=(',', ':'))
        json_messages.append(json_message)
    data = "".join(json_messages)
    return memoryview(bytes(data, 'utf8') + extra_data)


def message_decode(data: memoryview) -> Tuple[List[str], bytes]:
    extra_data = bytes([])
    # Parse out data bytes from the rest of the message.
    data_bytes = data.tobytes()
    if data_bytes.startswith(b'{"screen_write":'):
        extra_data_start = data_bytes.index(b'}') + 1
        extra_data = data_bytes[extra_data_start:]
        data_bytes = data_bytes[:extra_data_start]

    read_str = data_bytes.decode()

    # FIXME: this is an awful, terrible hack which will fail as soon
    # as it encounters }{ inside of a string.
    json_data = '[' + read_str.strip().replace('\n', ',').replace('}{', '},{') + ']'

    try:
        messages = json.loads(json_data)
    except json.decoder.JSONDecodeError as err:
        if FLAGS.debug:
            print('[!] DECODE FAILED:', json_data, err)
        messages = []

    return messages, extra_data
