from ambit.flags import FLAGS

import json
import msgpack

from typing import Any, Callable, Dict, List, Tuple

MESSAGE_FORMAT_JSON = 0
MESSAGE_FORMAT_MSGPACK = 1


def message_encode(messages: List[str], message_format: int, extra_data: bytes=bytes(())) -> memoryview:
    if message_format == MESSAGE_FORMAT_MSGPACK:
        return message_encode_msgpack(messages, extra_data)

    return message_encode_json(messages, extra_data)


def message_encode_json(messages: List[str], extra_data: bytes=bytes(())) -> memoryview:
    json_messages = []
    for message in messages:
        json_message = json.dumps(message, separators=(',', ':'))
        json_messages.append(json_message)
    data = "".join(json_messages)
    return memoryview(bytes(data, 'utf8') + extra_data)


def message_encode_msgpack(messages: List[str], extra_data: bytes=bytes(())) -> memoryview:
    msgpack_messages = []
    for message in messages:
        msgpack_message = msgpack.dumps(message)
        msgpack_messages.append(msgpack_message)
    data = b'~' + b'~~'.join(msgpack_messages) + b'~'
    if extra_data:
        extra_data += b'~'
    return memoryview(data + extra_data)


def message_decode(data: memoryview, message_format: int) -> Tuple[List[str], bytes]:
    # Parse out data bytes from the rest of the message.
    data_bytes = data.tobytes()

    if message_format == MESSAGE_FORMAT_MSGPACK:
        return message_decode_msgpack(data_bytes)

    return message_decode_json(data_bytes)


def message_decode_json(data_bytes: bytes) -> Tuple[List[str], bytes]:
    extra_data = bytes([])

    if data_bytes.startswith(b'{"screen_write":'):
        extra_data_start = data_bytes.index(b'}') + 1
        extra_data = data_bytes[extra_data_start:]
        data_bytes = data_bytes[:extra_data_start]

    try:
        read_str = data_bytes.decode()
    except:
        print('[!] Failed to decode bytes:', data_bytes);
        return [], extra_data

    # FIXME: this is an awful, terrible hack which will fail as soon
    # as it encounters }{ inside of a string.
    json_data = '[' + read_str.strip().replace('\n', ',').replace('}{', '},{') + ']'

    try:
        messages = json.loads(json_data)
    except json.decoder.JSONDecodeError as err:
        if FLAGS.debug:
            print('[!] JSON DECODE FAILED:', json_data, '--', err)
        messages = []

    return messages, extra_data


def message_decode_msgpack(data_bytes: bytes) -> Tuple[List[str], bytes]:
    # FIXME: handle bulk data transfers properly for msgpack
    data_parts = data_bytes.split(b'~')
    extra_data = data_parts[-1]
    msgpack_data = data_parts[1:-1]

    if extra_data:
        extra_data = b'~' + extra_data

    messages = []
    for msgpack_item in msgpack_data:
        try:
            message = msgpack.loads(msgpack_item)
        except ValueError as err:
            print('[!] MSGPACK DECODE FAILED:', msgpack_item, '--', err)
        else:
            messages.append(message)

    return messages, extra_data
