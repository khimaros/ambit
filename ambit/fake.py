"""Fake device for testing."""

import ambit

import io
import queue
import random
import time
import usb


DEFAULT_COMPONENT_LAYOUT = {
        'u': '00000', 'i': 1, 't': ambit.Component.KIND_BASE, 'c': [
            None,
            {'u': '  49d', 'i': 2, 't': ambit.Component.KIND_DIAL, 'c': [
                {'u': '  4FH', 'i': 3, 't': ambit.Component.KIND_DIAL, 'c': [
                    {'u': '  4lf', 'i': 8, 't': ambit.Component.KIND_BUTTON, 'c': [None, None, None]},
                    {'u': '  4}=', 'i': 4, 't': ambit.Component.KIND_SLIDER, 'c': [None, None, None, None, None]},
                    None]},
                None,
                {'u': '  4A0', 'i': 5, 't': ambit.Component.KIND_DIAL, 'c': [
                    None,
                    None,
                    {'u': '  4ls', 'i': 6, 't': ambit.Component.KIND_BUTTON, 'c': [
                        {'u': '  4}M', 'i': 7, 't': ambit.Component.KIND_SLIDER, 'c': [None, None, None, None, None]},
                        None,
                        None]}]
                }]
            },
            None]}

BASE_ONLY_LAYOUT = {
        'u': '00000', 'i': 1, 't': ambit.Component.KIND_BASE,
        'c': [None, None, None]}


def make_quad(cur):
    index1 = len(cur) + 1
    index2 = index1 + 1
    index3 = index2 + 1
    index4 = index3 + 1
    uid1 = '  4%.2x' % index1
    uid2 = '  4%.2x' % index2
    uid3 = '  4%.2x' % index3
    uid4 = '  4%.2x' % index4
    kind1 = random.choice([
        ambit.Component.KIND_BUTTON,
        ambit.Component.KIND_DIAL,
    ])
    kind2 = random.choice([
        ambit.Component.KIND_BUTTON,
        ambit.Component.KIND_DIAL,
    ])
    kind3 = random.choice([
        ambit.Component.KIND_BUTTON,
        ambit.Component.KIND_DIAL,
    ])
    kind4 = random.choice([
        ambit.Component.KIND_BUTTON,
        ambit.Component.KIND_DIAL,
    ])
    quad = {
        'u': uid1, 'i': index1, 't': kind1, 'c': [
            {'u': uid2, 'i': index2, 't': kind2, 'c': [None, None, None]},
            {'u': uid3, 'i': index3, 't': kind3, 'c': [
                {'u': uid4, 'i': index4, 't': kind4, 'c': [None, None, None]},
                None,
                None,
            ]},
            None,
        ]}
    cur.extend([1,1,1,1])
    return quad


def make_slider_quad(cur):
    index1 = len(cur) + 1
    index2 = index1 + 1
    uid1 = '  4%.2x' % index1
    uid2 = '  4%.2x' % index2
    kind = ambit.Component.KIND_SLIDER
    quad = {
        'u': uid1, 'i': index1, 't': kind, 'c': [
            None,
            None,
            None,
            {'u': uid2, 'i': index2, 't': kind, 'c': [None, None, None, None, None]},
            None,
        ]}
    cur.extend([1,1])
    return quad


def make_component_layout():
    cur = []
    layout = make_quad(cur)
    layout['u'] = '00000'
    layout['i'] = 1
    layout['t'] = ambit.Component.KIND_BASE

    # attach right
    layout['c'][1]['c'][0]['c'][1] = make_quad(cur)
    # attach below
    layout['c'][1]['c'][1] = make_quad(cur)
    # attach left
    layout['c'][2] = make_quad(cur)

    # attach below-right
    layout['c'][1]['c'][0]['c'][1]['c'][2] = make_slider_quad(cur)
    # attach below-left
    layout['c'][2]['c'][1]['c'][0]['c'][1] = make_slider_quad(cur)

    # attach below-right x 2
    #layout['c'][1]['c'][0]['c'][1]['c'][2]['c'][3]['c'][1] = make_slider_quad(cur)
    # attach below-left x 2
    #layout['c'][2]['c'][1]['c'][0]['c'][1]['c'][4] = make_slider_quad(cur)

    return layout


RANDOM_COMPONENT_LAYOUT = make_component_layout()


# NOTE: it is best to rely on as little functionality from the main
# ambit library as possible here.

class Handle:
    PHASE_CONTROL_0 = 'CONTROL_0'
    PHASE_CONTROL_1 = 'CONTROL_1'
    PHASE_CONTROL_2 = 'CONTROL_2'
    PHASE_CONTROL_3 = 'CONTROL_3'
    PHASE_CONTROL_4 = 'CONTROL_4'
    PHASE_CONTROL_5 = 'CONTROL_5'
    PHASE_BULK = 'BULK'
    PHASE_READY = 'READY'
    PHASE_INPUT = 'INPUT'

    # TODO: scale these with number of attached components
    # based on analysis in docs/PERFORMANCE.md
    # TODO: consider merging this with the consts in ambit.Controller
    DELAY_SCREEN_STRING_SECONDS = 1 / 20
    DELAY_LED_SECONDS = 1 / 60

    # TODO: reduce the max queue depth once we have a
    # reasonable way to kick off test inputs after we are
    # sure the Controller read thread is ready.
    WRITE_QUEUE_DEPTH = 32

    def __init__(self, layout):
        self._write_queue = queue.Queue(Handle.WRITE_QUEUE_DEPTH)
        self._layout = layout
        self._last_check = 0
        self._dropped_writes = 0
        self.messages = {}
        self.leds = {}
        self.phase = None
        self.screen_display = None
        self.screen_string = None
        self.screen_images = {}
        self._set_phase(Handle.PHASE_CONTROL_0)

    def _process_input(self, message, data):
        for message_type in message:
            if message_type not in self.messages:
                self.messages[message_type] = []
            self.messages[message_type].append(message[message_type])
        if 'start' in message:
            self._process_start(message['start'])
        if 'led' in message:
            self._process_led(message['led'])
        if 'check' in message:
            self._process_check(message['check'])
        if 'screen_display' in message:
            self.screen_display = message['screen_display']
        if 'screen_string' in message:
            time.sleep(Handle.DELAY_SCREEN_STRING_SECONDS)
            self.screen_string = message['screen_string']
        if 'screen_write' in message:
            self._process_screen_write(message['screen_write'], data)

    def _process_check(self, check):
        #print('[F] Processing check message')
        if self.phase == Handle.PHASE_READY:
            self._set_phase(Handle.PHASE_INPUT)
        self._last_check = time.time()

    def _process_screen_write(self, index, image_bytes):
        fd = io.BytesIO(image_bytes)
        self.screen_images[index] = image_bytes

    def _process_start(self, start):
        #print('[F] Processing start message')
        if self.phase == Handle.PHASE_BULK:
            self._set_phase(Handle.PHASE_READY)
        self._write_layout()

    def _process_led(self, leds):
        #print('[F] Processing led message', leds)
        time.sleep(Handle.DELAY_LED_SECONDS)
        for led in leds:
            self.leds[led['i']] = (led['r'], led['g'], led['b'])

    def _write_layout(self):
        #print('[F] Sending layout')
        self.write_messages([
            {'l': self._layout},
        ])

    def write_messages(self, messages):
        data = ambit.message_encode(messages)
        self._write(data)

    def _write(self, data):
        if self._write_queue.full():
            for _ in range(int(self._write_queue.qsize() / 8)):
                self._write_queue.get()
                self._write_queue.task_done()
                self._dropped_writes += 1
                #print('DROPPED:', self._dropped_writes)
        self._write_queue.put(data)

    def _set_phase(self, phase):
        if phase == self.phase:
            return
        self.phase = phase
        if ambit.FLAGS.debug:
            print('[F] Device Phase Change:', self.phase)

    def bulkWrite(self, ep, data, size, timeout=0):
        messages, extra_data = ambit.message_decode(data)
        if ambit.FLAGS.debug:
            print('[F] Handle.bulkWrite()', ep, messages, size, timeout)
        for message in messages:
            self._process_input(message, extra_data)
        return len(data)

    def bulkRead(self, ep, size, timeout=0):
        data = ''
        start_time = time.time()
        while (not timeout) or (time.time() - start_time) * 1000 < timeout:
            try:
                data = self._write_queue.get(timeout=0.01)
                break
            except queue.Empty:
                pass
        if ambit.FLAGS.debug:
            print('[F] Handle.bulkRead()', ep, size, timeout, '=>', data)
        if not data:
            raise usb.USBError('no data to read')
        return data

    def controlMsg(self, ep, ctrl, size):
        if ambit.FLAGS.debug:
            print('[F] Handle.controlMsg()', ep, ctrl, size)
        if self.phase == Handle.PHASE_CONTROL_0:
            self._set_phase(Handle.PHASE_CONTROL_1)
            return
        if self.phase == Handle.PHASE_CONTROL_1:
            self._set_phase(Handle.PHASE_CONTROL_2)
            return
        if self.phase == Handle.PHASE_CONTROL_2:
            self._set_phase(Handle.PHASE_CONTROL_3)
            return
        if self.phase == Handle.PHASE_CONTROL_3:
            self._set_phase(Handle.PHASE_CONTROL_4)
            return
        if self.phase == Handle.PHASE_CONTROL_4:
            self._set_phase(Handle.PHASE_CONTROL_5)
            return
        if self.phase == Handle.PHASE_CONTROL_5:
            self._set_phase(Handle.PHASE_BULK)
            return

    def reset(self):
        if ambit.FLAGS.verbose:
            print('[F] Handle.reset()')

    def releaseInterface(self):
        if ambit.FLAGS.verbose:
            print('[F] Handle.releaseInterface()')


class Device:
    def __init__(self, device_id, interface_id):
        if ambit.FLAGS.verbose:
            print('[F] Device.__init__()', device_id, interface_id)
        self.device_id = device_id
        self.interface_id = interface_id
        self._layout = {}
        self.values = {}
        self.kinds = {}
        self.handle = None

    def components_connected(self, layout=DEFAULT_COMPONENT_LAYOUT):
        if ambit.FLAGS.debug:
            print('[F] Layout set to', layout)
        self._layout = layout
        self.values = {}
        self.initialize_values(self._layout)

    # TODO: consolidate this with components_connected?
    def layout_changed(self, layout):
        self.components_connected(layout)
        self.handle._layout = layout
        self.handle._write_layout()

    def initialize_values(self, component):
        if not component:
            return
        index = component['i']
        self.values[index] = [0,0,0,0,0,0,0,0]
        self.kinds[index] = component['t']
        for c in component['c']:
            self.initialize_values(c)

    def open(self):
        if ambit.FLAGS.verbose:
            print('[F] Device.open()')
        self.handle = Handle(self._layout)
        return self.handle

    def input_pressed(self, index):
        if self.kinds[index] not in (
                ambit.Component.KIND_DIAL,
                ambit.Component.KIND_BUTTON):
            return
        values = self.values[index]
        values[0] = 1
        values[1] = 0
        values[2] = 0
        self.values[index] = values
        self.handle.write_messages([
                {'in': [{'i': index, 'v': values}]},
        ])

    def input_released(self, index):
        if self.kinds[index] not in (
                ambit.Component.KIND_DIAL,
                ambit.Component.KIND_BUTTON):
            return
        values = self.values[index]
        values[0] = 0
        values[1] = 0
        values[2] = 0
        self.values[index] = values
        self.handle.write_messages([
                {'in': [{'i': index, 'v': values}]},
        ])

    def input_slide_up(self, index, amount=8):
        if self.kinds[index] != ambit.Component.KIND_SLIDER:
            return
        values = self.values[index]
        if values[0] == 255:
            return
        values[0] += amount
        if values[0] > 255:
            values[0] = 255
        self.values[index] = values
        self.handle.write_messages([
                {'in': [{'i': index, 'v': values}]},
        ])

    def input_slide_down(self, index, amount=8):
        if self.kinds[index] != ambit.Component.KIND_SLIDER:
            return
        values = self.values[index]
        if values[0] == 0:
            return
        values[0] -= amount
        if values[0] < 0:
            values[0] = 0
        self.values[index] = values
        self.handle.write_messages([
                {'in': [{'i': index, 'v': values}]},
        ])

    def input_rotation_left(self, index, amount=8):
        if self.kinds[index] != ambit.Component.KIND_DIAL:
            return
        values = self.values[index]
        values[1] = amount
        values[2] = 0
        values[3] -= amount
        if values[3] < 0:
            values[3] = 0
        self.values[index] = values
        self.handle.write_messages([
                {'in': [{'i': index, 'v': values}]},
        ])

    def input_rotation_right(self, index, amount=8):
        if self.kinds[index] != ambit.Component.KIND_DIAL:
            return
        values = self.values[index]
        values[1] = 0
        values[2] = amount
        values[3] += amount
        if values[3] > 255:
            values[3] = 255
        self.values[index] = values
        self.handle.write_messages([
                {'in': [{'i': index, 'v': values}]},
        ])
