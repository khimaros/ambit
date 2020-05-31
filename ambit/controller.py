#!/usr/bin/env python3

from ambit.component import Component, ComponentBehavior, ComponentLayout
from ambit.configuration import Configuration
from ambit.message import message_decode, message_encode
from ambit.flags import FLAGS

import subprocess
import sys
import threading
import time
import usb
import queue

from typing import Any, Callable, Dict, List, Tuple


class Device:
    def __init__(self, device_id, interface_id) :
        vendor_id, product_id = device_id.split(':')
        self.vendor_id = int(vendor_id, 16)
        self.product_id = int(product_id, 16)
        self.interface_id = interface_id
        self._device = self._discover()
        self.handle = None

    def _discover(self):
        buses = usb.busses()
        for bus in buses:
            for device in bus.devices:
                if device.idVendor == self.vendor_id:
                    if device.idProduct == self.product_id:
                        return device
        return None

    def open(self):
        if not self._device:
            print('[!] Failed to read from device, check cable and permissions!')
            sys.exit(1)
        handle = self._device.open()
        try:
            handle.detachKernelDriver(self.interface_id)
        except:
            pass
        handle.claimInterface(self.interface_id)
        self.handle = handle
        return handle


class Controller:
    BULK_WRITE_TIMEOUT_MS = 1000
    BULK_READ_TIMEOUT_MS = 1000
    BULK_READ_SIZE_BYTES = 4096
    QUEUE_TIMEOUT_SECONDS = 0.5

    DEFAULT_WAIT_SECONDS = 0.5

    # Above 20 updates per second, the screen will hard reset
    # if the string length is larger than ~3 bytes.
    SCREEN_STRING_DELAY_SECONDS = 1 / 20
    SCREEN_STRING_QUEUE_DEPTH = 8
    LED_DELAY_SECONDS = 1 / 60
    LED_QUEUE_DEPTH = 64

    KEEPALIVE_TIMEOUT_SECONDS = 5
    SCREEN_RESET_SECONDS = 3

    USB_INTERFACE_ID = 0
    USB_ENDPOINT_BULK_IN = 0x84
    USB_ENDPOINT_BULK_OUT = 0x05

    # Magic string used during control handshake.
    HANDSHAKE_BYTES = [0xe0, 0x93, 0x04, 0x00, 0x00, 0x00, 0x00, 0x08]

    BEHAVIOR_KIND_DEFAULTS = {
            Component.KIND_SLIDER: ComponentBehavior(
                behavior=ComponentBehavior.TRIGGER,
                limits=(0,255), invert=False),
    }
    BEHAVIOR_INPUT_DEFAULTS = {
            Configuration.INPUT_PRESSED: ComponentBehavior(
                behavior=ComponentBehavior.TRIGGER),
            Configuration.INPUT_RELEASED: ComponentBehavior(
                behavior=ComponentBehavior.TRIGGER),
            Configuration.INPUT_ROTATION_LEFT: ComponentBehavior(
                behavior=ComponentBehavior.ACCUMULATE, invert=True),
            Configuration.INPUT_ROTATION_RIGHT: ComponentBehavior(
                behavior=ComponentBehavior.ACCUMULATE, invert=False),
            Configuration.INPUT_SET: ComponentBehavior(
                behavior=ComponentBehavior.TRIGGER, invert=False, limits=(0,255)),
    }
    BEHAVIOR_ACTION_DEFAULTS = {
            Configuration.ACTION_SET_COLOR_RED: ComponentBehavior(
                limits=(0, 255), default=255, threshold=8),
            Configuration.ACTION_SET_COLOR_GREEN: ComponentBehavior(
                limits=(0, 255), default=255, threshold=8),
            Configuration.ACTION_SET_COLOR_BLUE: ComponentBehavior(
                limits=(0, 255), default=255, threshold=8),

            Configuration.ACTION_CYCLE_MAPPING: ComponentBehavior(
                ComponentBehavior.CYCLE, loop=True, nested=True),

            Configuration.ACTION_PROFILE_NEXT: ComponentBehavior(
                ComponentBehavior.TRIGGER),
            Configuration.ACTION_PROFILE_PREV: ComponentBehavior(
                ComponentBehavior.TRIGGER),
            Configuration.ACTION_PROFILE_SWITCH: ComponentBehavior(
                ComponentBehavior.CYCLE, loop=True),

            Configuration.ACTION_TEST_CYCLE: ComponentBehavior(
                ComponentBehavior.CYCLE, loop=True, nested=True),
            Configuration.ACTION_TEST_DELTA: ComponentBehavior(
                ComponentBehavior.DELTA),
            Configuration.ACTION_TEST_ACCUMULATE: ComponentBehavior(
                ComponentBehavior.ACCUMULATE),
            Configuration.ACTION_TEST_TRIGGER: ComponentBehavior(
                ComponentBehavior.TRIGGER),
    }

    device: Device
    handle: Any
    config: Configuration
    layout: ComponentLayout
    lock: threading.Lock
    shutdown_event: threading.Event
    write_queue: queue.Queue
    action_callback_map: Dict[str, Callable]

    def __init__(self, config=None, device=None):
        self.device = device or Device(FLAGS.device, Controller.USB_INTERFACE_ID)
        self.handle = None
        self.config = config
        self.layout = ComponentLayout(orientation=config.profile.orientation)

        # TODO: do we need more than one lock?
        self.lock = threading.Lock()
        self.shutdown_event = threading.Event()

        self.write_queue = queue.Queue()
        self.screen_string_queue = queue.Queue(Controller.SCREEN_STRING_QUEUE_DEPTH)
        self.led_queue = queue.Queue(Controller.LED_QUEUE_DEPTH)

        self.bulk_read_thread = threading.Thread(target=self.bulk_read_worker)
        self.bulk_write_thread = threading.Thread(target=self.bulk_write_worker)
        self.screen_string_thread = threading.Thread(target=self.screen_string_worker)
        self.led_thread = threading.Thread(target=self.led_worker)
        self.keepalive_thread = threading.Thread(target=self.keepalive_worker)

        self.failed_writes = 0
        self.failed_reads = 0
        self.dropped_screen_strings = 0
        self.dropped_leds = 0

        self.last_led_time = 0
        self.last_write_time = 0
        self.last_screen_string_time = 0

        # FIXME: this doesn't feel like the right home
        self.current_led_values = (255, 255, 255)
        self.current_cycle_mappings = {}
        self.current_screen_string_value = ''

        default_action_callbacks = {
            Configuration.ACTION_PROFILE_PREV: self.callback_profile_prev,
            Configuration.ACTION_PROFILE_NEXT: self.callback_profile_next,
            Configuration.ACTION_PROFILE_SWITCH: self.callback_profile_switch,
            Configuration.ACTION_SET_COLOR_RED: self.callback_set_color_red,
            Configuration.ACTION_SET_COLOR_GREEN: self.callback_set_color_green,
            Configuration.ACTION_SET_COLOR_BLUE: self.callback_set_color_blue,
            Configuration.ACTION_EXECUTE_COMMAND: self.callback_execute_command,
            Configuration.ACTION_CYCLE_MAPPING: self.callback_cycle_mapping,
            Configuration.ACTION_TOGGLE_PREVIEW: lambda x: None,
            Configuration.ACTION_TEST_CYCLE: self.callback_test_cycle,
            Configuration.ACTION_TEST_DELTA: self.callback_test_delta,
            Configuration.ACTION_TEST_ACCUMULATE: self.callback_test_accumulate,
            Configuration.ACTION_TEST_TRIGGER: self.callback_test_trigger,
        }

        self.action_callback_map = {}
        for action_name in default_action_callbacks:
            action_callback = default_action_callbacks[action_name]
            self.register_action_callback(action_name, action_callback)

    def register_action_callback(self, action_name, callback):
        self.action_callback_map[action_name] = callback

    def open(self):
        self.handle = self.device.open()

    def close(self):
        """ Release device interface """
        print('[0] Joining threads and releasing USB interface.')
        self.join()
        try:
            self.handle.reset()
            self.handle.releaseInterface()
            #self.handle.attachKernelDriver(self.device.interface_id)
        except Exception as err:
            print(err)
        self.handle, self.device = None, None

    # TODO: turn these hex values into descriptive constants
    def control_handshake(self):
        # URB_CONTROL in (empty)
        self.handle.controlMsg(0xa1, 0x21, 7)

        # URB_CONTROL out (handshake)
        self.handle.controlMsg(0x21, 0x20, Controller.HANDSHAKE_BYTES)

        # URB_CONTROL in (empty)
        self.handle.controlMsg(0xa1, 0x21, 7)

        # URB_CONTROL out (empty)
        self.handle.controlMsg(0x21, 0x22, 0)

        # URB_CONTROL out (handshake)
        self.handle.controlMsg(0x21, 0x20, Controller.HANDSHAKE_BYTES)

        # URB_CONTROL in (empty)
        self.handle.controlMsg(0xa1, 0x21, 7)

    def bulk_write_worker(self):
        while not self.shutdown_event.is_set():
            try:
                data = self.write_queue.get(timeout=Controller.QUEUE_TIMEOUT_SECONDS)
            except queue.Empty:
                pass
            else:
                self.bulk_write(data)
                self.write_queue.task_done()

    def bulk_write_messages(self, messages):
        if not messages:
            return
        if FLAGS.debug:
            print("[@] BULK WRITE:", messages)
        data = message_encode(messages)
        self.write_queue.put(data, Controller.QUEUE_TIMEOUT_SECONDS)

    def bulk_write(self, data):
        try:
            self.handle.bulkWrite(
                    Controller.USB_ENDPOINT_BULK_OUT,
                    data,
                    Controller.BULK_WRITE_TIMEOUT_MS)
        except usb.USBError:
            self.failed_writes += 1
        else:
            self.lock.acquire()
            self.last_write_time = time.time()
            self.lock.release()

    def bulk_read_worker(self):
        while not self.shutdown_event.is_set():
            messages = self.bulk_read()
            for message in messages:
                self.process_bulk_message(message)

    def bulk_read(self):
        try:
            data = self.handle.bulkRead(
                    Controller.USB_ENDPOINT_BULK_IN,
                    Controller.BULK_READ_SIZE_BYTES,
                    Controller.BULK_READ_TIMEOUT_MS)
        except usb.USBError:
            self.failed_reads +=  1
            return []
        else:
            messages, _ = message_decode(data)
            if FLAGS.debug:
                print("[@] BULK READ:", messages)
            return messages

    def start(self):
        self.bulk_write_messages([
            {"start": 1},
        ])

    def check(self):
        self.bulk_write_messages([
            {"check": 1},
        ])

    def led_worker(self):
        while not self.shutdown_event.is_set():
            if self.led_queue.full():
                # TODO: should we be clearing the entire queue when full, or just some of it?
                for _ in range(self.led_queue.qsize() - 2):
                    self.led_queue.get()
                    self.led_queue.task_done()
                    self.dropped_leds += 1
            if time.time() - self.last_led_time < Controller.LED_DELAY_SECONDS:
                wait = Controller.LED_DELAY_SECONDS - (time.time() - self.last_led_time)
                time.sleep(wait)
            try:
                # TODO: look ahead in the queue to find duplicates or
                # ways that we can join multiple updates into a single
                # bulk write?
                leds = self.led_queue.get(timeout=Controller.QUEUE_TIMEOUT_SECONDS)
            except queue.Empty:
                pass
            else:
                data = message_encode([
                    {"led": leds},
                ])
                self.bulk_write(data)
                # FIXME: this feels like a pretty inefficient way to
                # update the component state, but fixing may require
                # changing the API surface provided by Controller.led()
                for led in leds:
                    component = self.layout.find_component(led['i'])
                    if component:
                        component.led = (led['r'], led['g'], led['b'])
                self.last_led_time = time.time()
                self.led_queue.task_done()

    def led(self, leds):
        try:
            self.led_queue.put(leds, timeout=Controller.QUEUE_TIMEOUT_SECONDS)
        except queue.Full:
            self.dropped_leds += 1

    def clear(self):
        # Reset mappings to empty
        self.bulk_write_messages([
            { "hidmap": [] },
            { "joymap": [] },
            { "midimap": [] },
            { "led": [] },
        ])

    def cycle(self):
        # Cycle through each LED and reset to white.
        for component in self.layout.connected():
            self.led([
                {"b": 0, "g": 0, "i": component.index, "m": 0, "r": 255},
            ])
            self.led([
                {"b": 255, "g": 255, "i": component.index, "m": 0, "r": 255},
            ])
            cr, cg, cb = self.current_led_values
            self.led([
                {"b": cb, "g": cg, "i": component.index, "m": 0, "r": cr},
            ])

    def print_stats(self):
        print('[@] Cumulative dropped_leds:', self.dropped_leds)
        print('[@] Cumulative dropped_screen_strings:', self.dropped_screen_strings)
        print('[@] Cumulative failed_writes:', self.failed_writes)

    def screen_string_worker(self):
        while not self.shutdown_event.is_set():
            if time.time() - self.last_screen_string_time < Controller.SCREEN_STRING_DELAY_SECONDS:
                wait = Controller.SCREEN_STRING_DELAY_SECONDS - (time.time() - self.last_screen_string_time)
                time.sleep(wait)
            if self.screen_string_queue.full():
                # TODO: should we be clearing the entire queue when full, or just some of it?
                for _ in range(self.screen_string_queue.qsize() - 2):
                    self.screen_string_queue.get(timeout=Controller.QUEUE_TIMEOUT_SECONDS)
                    self.screen_string_queue.task_done()
                    self.dropped_screen_strings += 1
            try:
                title = self.screen_string_queue.get(timeout=Controller.QUEUE_TIMEOUT_SECONDS)
            except queue.Empty:
                pass
            else:
                data = message_encode([
                    { "screen_string": str(title) },
                ])
                self.bulk_write(data)
                component = self.layout.find_component(1)
                component.screen_string = str(title)
                self.last_screen_string_time = time.time()
                self.current_screen_string_value = title
                self.screen_string_queue.task_done()

    def screen_string(self, title):
        if title == self.current_screen_string_value:
            return
        try:
            self.screen_string_queue.put(title, timeout=Controller.QUEUE_TIMEOUT_SECONDS)
        except queue.Full:
            self.dropped_screen_strings += 1

    def screen_write(self, path, index):
        print('[0] Uploading image %s to index %d' % (path, index))
        with open(path, 'rb') as f:
            data = message_encode([{'screen_write': index}], f.read())
            flen = f.tell()
        self.handle.bulkWrite(Controller.USB_ENDPOINT_BULK_OUT, data, 10000)
        print('[0] Image upload to index %d (%d bytes) complete!'  % (index, flen))

    def screen_display(self, index):
        self.bulk_write_messages([
            {"screen_display": index}
        ])
        component = self.layout.find_component(1)
        component.screen_display = index

    def initialize(self):
        # TODO: initialize layout using configuration and set up
        # callbacks before the first layout update.
        #self.layout.update(self.config.profile.layout)
        #self.configure_component_callbacks()

        self.start()

        self.clear()

        print("[0] Waiting for initial layout ...")
        self.wait_for_layout()

        self.check()

    def configure_orientation(self):
        messages = []
        for component in self.layout.connected():
            flip = 1 if component.flip else 0
            messages.append({"flip": [ {"i": component.index, "m": flip } ]})
        self.bulk_write_messages(messages)

    def configure_images(self):
        if len(self.layout.connected()) > 1:
            print('[0] Skipping image upload, too many components connected.')
            return

        self.check()
        self.clear()

        #for index in range(25):
        #    self.screen_write('./reference/assets/%d.raw' % index, index)
        #    self.screen_display(index)
        #    time.sleep(1)

        for index in (23, 24, 25):
            self.screen_write('./example/assets/%d.raw' % index, index)
            self.screen_display(index)
            time.sleep(1)

        self.bulk_write_messages([ { "set_version_screen": 0 } ])

        self.start()

    def led_draw(self, pixels, x, y, w, h):
        leds = []
        for cy in range(y, y - h, -1):
            for cx in range(x, x + w):
                component = self.layout.component_in_slot((cx, cy))
                if not component:
                    continue
                r, g, b = pixels.pop(0)
                leds.append({"b": b, "g": g, "i": component.index, "m": 0, "r": r})
        self.led(leds)

    def configure_leds(self, red=None, green=None, blue=None):
        if red is None: red = self.current_led_values[0]
        if green is None: green = self.current_led_values[1]
        if blue is None: blue = self.current_led_values[2]

        leds = []
        for component in self.layout.connected():
            leds.append({"b": blue, "g": green, "i": component.index, "m":0, "r": red})
        self.led(leds)

        # FIXME: this may not represent current state as self.led() is asynchronous
        self.current_led_values = (red, green, blue)

    def configure_midimap_dial(self, component):
        #rotate_note = component.index
        #pressed_note = component.index * 12
        rotation_note = self.component_hash(component)
        pressed_note = self.component_hash(component)
        self.bulk_write_messages([
            {"midimap":[{
                "i": component.index,
                "s": [
                    # dial dial rotation
                    {"c":3, "d": rotation_note, "m":1, "mc":0, "t":2},
                    # dial button press
                    {"c":0, "d": pressed_note, "m":0, "mc":0, "t":1}
                ],
            }]},
        ])

    def configure_midimap_slider(self, component):
        #note = component.index * 12
        note = self.component_hash(component)
        self.bulk_write_messages([
            {"midimap": [{"i": component.index, "s": [{ "c": 0, "d": note, "m" :0, "mc": 0, "t": 2 }]}]},
        ])

    def configure_midimap_button(self, component):
        #note = component.index * 12
        note = self.component_hash(component)
        self.bulk_write_messages([
            {"midimap": [{
                "i": component.index,
                "s": [
                    { "c": 0, "d": note, "m": 0, "mc": 0, "t": 1 },
                ]},
            ]},
        ])

    def component_hash(self, component):
        # possible component.uid are 32 through 126 (94 possible values)
        # with 2 characters, 94 * 94 = 8836 possible combinations.
        # but there are only 127 possible note values in MIDI, so we need
        # to find a way to compress.
        table = list(range(0, 128))
        h = len(component.uid[1:2]) % 128
        for i in component.uid[1:]:
            h = table[h ^ ord(i)]
        return h

    # FIXME: keep consistent mapping across disconnect/reconnect
    # need to remove reliance on index (use uid instead)
    def configure_midimap(self):
        for component in self.layout.connected():
            if component.kind == Component.KIND_DIAL:
                self.configure_midimap_dial(component)
            if component.kind == Component.KIND_BUTTON:
                self.configure_midimap_button(component)
            if component.kind == Component.KIND_SLIDER:
                self.configure_midimap_slider(component)

    def configure_hidmap(self):
        hidmaps = []
        for component in self.layout.connected():
            print('HIDKEYS:', component.hidkeys)
            for control, key, mod, repeat in component.hidkeys:
                hm = { "i": component.index, "s": [{
                    "c": control, "k": key, "m": mod, "r": repeat, "rp": repeat}], "t": 0 }
                self.bulk_write_messages([{ "hidmap": [hm] }])
                hidmaps.append(hm)
        #self.bulk_write_messages([{ "hidmap": hidmaps }])

    def configure_display(self):
        orientation = int((180 + self.config.profile.orientation) % 360 / 90)
        self.bulk_write_messages([
            { "screen_orientation": orientation },
            { "screen_display": self.config.profile.icon },
            { "screen_string": self.config.profile.title },
        ])
        component = self.layout.find_component(1)
        component.screen_string = self.config.profile.title
        component.screen_display = self.config.profile.icon

    def configure_component_hidkeys(self):
        for component in self.layout.connected():
            self.set_component_hidkeys(component)

    def set_component_hidkeys(self, component):
        for control, key, mod, repeat in self.config.component_hidkeys(component.uid):
            component.set_hidkey(control, key, mod, repeat)

    # TODO: this function could be moved to out of Controller along with the maps.
    # could be a static method eg. ComponentBehavior.from_action(...) and might
    # be possible to remove action_config param from ComponentBehavior.__init__()
    def make_action_behavior(self, action_config, component_kind, input_type, action_name):
        behavior = ComponentBehavior(action_config=action_config)
        if component_kind in Controller.BEHAVIOR_KIND_DEFAULTS:
            behavior += Controller.BEHAVIOR_KIND_DEFAULTS[component_kind]
        if input_type in Controller.BEHAVIOR_INPUT_DEFAULTS:
           behavior += Controller.BEHAVIOR_INPUT_DEFAULTS[input_type]
        if action_name in Controller.BEHAVIOR_ACTION_DEFAULTS:
            behavior += Controller.BEHAVIOR_ACTION_DEFAULTS[action_name]
        return behavior

    # TODO: Move this (and callback methods) to outside of Ambit class
    # and instead allow subclasses to set them up. We can have a common
    # subclass which is the default behavior.
    def configure_component_callbacks(self):
        for component in self.layout.connected():
            component.reset()
        for uid_query in self.config.components():
            components = self.layout.query(uid_query)
            if components:
                component = components[0]
                self.set_component_callbacks(uid_query, component)

    def set_component_callbacks(self, uid_query, component):
        for input_type, action_name, action_config in self.config.component_actions(uid_query):
            if action_name not in self.action_callback_map:
                print('[0] Unrecognized action type:', action_name)
                continue
            callback = self.action_callback_map[action_name]

            behavior = self.make_action_behavior(action_config, component.kind, input_type, action_name)
            if action_name == Configuration.ACTION_EXECUTE_COMMAND:
                behavior.data = [action_config['argv']]
            if action_name == Configuration.ACTION_CYCLE_MAPPING:
                behavior.data = [action_config['target']]
            if action_name == Configuration.ACTION_PROFILE_SWITCH:
                behavior.set_items(self.config.profiles)

            component.set_callback(input_type, action_name, behavior, callback, action_config)

    def callback_test_cycle(self, value):
        _, value = value
        self.screen_string('C: %s' % value)

    def callback_test_delta(self, value):
        self.screen_string('D: %s' % value)

    def callback_test_accumulate(self, value):
        self.screen_string('A: %s' % value)

    def callback_test_trigger(self, value):
        self.screen_string('T: %s' % value)

    def callback_cycle_mapping(self, value, target):
        index, action_config = value
        self.config.set_component_actions(target, action_config)
        self.set_component_callbacks(target, self.layout.components[target])
        self.screen_string(['Red', 'Green', 'Blue'][index])

    def callback_execute_command(self, value, argv):
        p = subprocess.run(
                argv, env={'AMBIT_VALUE': str(value)},
                stdout=subprocess.PIPE)
        result = p.stdout.decode().split('\n')[0].strip()
        self.screen_string(result)

    def callback_set_color_red(self, value):
        value = int(value)
        self.configure_leds(red=value)
        self.screen_string('Red: %d' % value)

    def callback_set_color_green(self, value):
        value = int(value)
        self.configure_leds(green=value)
        self.screen_string('Green: %d' % value)

    def callback_set_color_blue(self, value):
        value = int(value)
        self.configure_leds(blue=value)
        self.screen_string('Blue: %d' % value)

    def callback_profile_switch(self, value):
        value = int(value)
        self.config.switch(value)
        self.start()

    def callback_profile_prev(self, unused_value):
        self.config.prev()
        self.start()

    def callback_profile_next(self, unused_value):
        self.config.next()
        self.start()

    def print_layout(self):
        for component in self.layout.connected():
            bound_inputs = []
            for input_type, action_name, _ in self.config.component_actions(component.uid):
                bound_inputs.append('%s (%s)' % (input_type, action_name))
            print('[0] Component attached: %s (%d) %s %s - %s - %s :: %s' % (
                component.kind_name(), component.index, component.uid,
                component.slot, component.orientation, component.flip,
                ', '.join(bound_inputs)))

    def print_input(self, component, input_type, value, raw_value):
        if not FLAGS.verbose:
            return
        print('[%d] Input %s %s: %s (%d)!' % (
            component.index, component.kind_name(),
            input_type, value, raw_value))

    def display_input(self, component, input_type, value, raw_value):
        if not FLAGS.verbose:
            return
        sv = str(value) if value is not None else str(raw_value)
        self.screen_string('%s: %s' % (component.kind_name(), sv))

    # FIXME: this function is reaching into all kinds of private areas
    def rotate(self, rotation):
        orientation = (self.layout.base_orientation + rotation) % 360
        self.config.profile.orientation = orientation
        self.layout.base_orientation = orientation
        self.process_layout(self.layout.layout_dict)

    def process_bulk_message(self, message):
        if "l" in message:
            self.process_layout(message["l"])
        elif "in" in message:
            self.process_input(message["in"])

    def process_layout(self, layout_dict):
        self.layout.update(layout_dict)

        self.print_layout()
        self.clear()
        self.cycle()

        self.configure_component_callbacks()
        self.configure_orientation()
        self.configure_leds()
        self.configure_component_hidkeys()
        self.configure_display()

        # TODO: support layout change callback
        #self.layout_changed_callback()

        # TODO: maybe enable these as flags?
        #self.configure_midimap()
        #self.configure_hidmap()

        print('[0] Processed layout, ready for input!')

    def process_input(self, input_messages):
        for input_dict in input_messages:
            i = input_dict["i"]
            v = input_dict["v"]
            component = self.layout.find_component(i)
            if not component:
                return
            component.previous_values = component.values
            component.values = v
            for input_type in component.determine_input_types():
                raw_value = component.dominant_value(input_type)
                value = component.invoke_callback(input_type)
                self.print_input(component, input_type, value, raw_value)
                self.display_input(component, input_type, value, raw_value)

    def wait_for_layout(self):
        while not self.layout:
            time.sleep(Controller.DEFAULT_WAIT_SECONDS)

    def wait(self):
        while self.led_queue.qsize() > 0:
            time.sleep(Controller.DEFAULT_WAIT_SECONDS)
        while self.screen_string_queue.qsize() > 0:
            time.sleep(Controller.DEFAULT_WAIT_SECONDS)
        while self.write_queue.qsize() > 0:
            time.sleep(Controller.DEFAULT_WAIT_SECONDS)

    def join(self):
        self.shutdown_event.set()
        if self.bulk_read_thread.is_alive():
            self.bulk_read_thread.join()
        if self.bulk_write_thread.is_alive():
            self.bulk_write_thread.join()
        if self.screen_string_thread.is_alive():
            self.screen_string_thread.join()
        if self.led_thread.is_alive():
            self.led_thread.join()
        if self.keepalive_thread.is_alive():
            self.keepalive_thread.join()

    def spawn(self):
        self.bulk_read_thread.start()
        self.bulk_write_thread.start()
        self.screen_string_thread.start()
        self.led_thread.start()

    def connect(self):
        self.bulk_read()
        self.control_handshake()
        self.spawn()
        self.initialize()
        self.keepalive_thread.start()

    def keepalive_worker(self):
        while not self.shutdown_event.is_set():
            cur_time = time.time()
            self.lock.acquire()
            last_write_time = self.last_write_time
            last_screen_string_time = self.last_screen_string_time
            screen_title = self.config.profile.title
            self.lock.release()
            if cur_time - last_screen_string_time > Controller.SCREEN_RESET_SECONDS:
                if self.config.profile.title is not None:
                    self.screen_string(screen_title)
            if cur_time - last_write_time > Controller.KEEPALIVE_TIMEOUT_SECONDS:
                self.check()
            time.sleep(Controller.DEFAULT_WAIT_SECONDS)

    def communicate(self):
        try:
            while not self.shutdown_event.is_set():
                time.sleep(Controller.DEFAULT_WAIT_SECONDS)
        except KeyboardInterrupt:
            print('\r[0] Received interrupt, shutting down...')
        except Exception as err:
            self.close()
            raise err


# TODO: make this a thing! (maybe subclass?)
class StandardAmbit:
    def __init__(self, config_path):
        pass
