#!/usr/bin/env python3

from ambit.configuration import Configuration
from ambit.flags import FLAGS

import ambit.coordinates

import copy

from typing import Any, Callable, Dict, List, Tuple


class ComponentInvocation(object):
    input_type: int
    action_name: str
    behavior: Any
    function: Callable
    vindex: int
    action_config: Any
    persistent_state: Dict[str, Any]
    threshold: int
    data: Any
    cumulative_change: int

    def __init__(self, input_type, action_name, behavior, callback, vindex, action_config, persistent_state):
        self.input_type = input_type
        self.action_name = action_name
        self.behavior = behavior
        self.function = callback
        self.vindex = vindex
        self.action_config = action_config
        self.persistent_state = persistent_state

        if not 'stored_value' in self.persistent_state:
            self.persistent_state['stored_value'] = self.behavior.default

        self.threshold = self.behavior.threshold
        self.data = behavior.data

        self.cumulative_change = 0

    def callback_value(self, value):
        callback_value = value

        change = self.cumulative_change

        if self.behavior.behavior == ComponentBehavior.CYCLE:
            change = 1

        if self.behavior.invert:
            change = -change

        if self.behavior.behavior == ComponentBehavior.TRIGGER:
            callback_value = value
            if self.input_type == Configuration.INPUT_SET and self.behavior.limits:
                step = 255 / (self.behavior.limits[1] - self.behavior.limits[0])
                callback_value = self.behavior.limits[0] + value / step

        if self.behavior.behavior == ComponentBehavior.CYCLE:
            callback_value = self.persistent_state['stored_value'] + change
            if self.input_type == Configuration.INPUT_SET and self.behavior.limits:
                step = 255 / (self.behavior.limits[1] - self.behavior.limits[0])
                callback_value = int(value / step)

        if self.behavior.behavior == ComponentBehavior.DELTA:
            callback_value = self.cumulative_change
            if self.behavior.invert:
                callback_value = -callback_value

        if self.behavior.value is not None:
            callback_value = self.behavior.value

        if self.behavior.behavior == ComponentBehavior.ACCUMULATE:
            change = self.threshold
            if self.behavior.value:
                change = self.behavior.value
            if self.behavior.invert:
                change = -change
            callback_value = self.persistent_state['stored_value'] + change

        if self.behavior.loop:
            if callback_value < self.behavior.limits[0]:
                callback_value = self.behavior.limits[1]
            if callback_value > self.behavior.limits[1]:
                callback_value = self.behavior.limits[0]
        elif self.behavior.outside(callback_value):
            if callback_value < self.behavior.limits[0]:
                callback_value = self.behavior.limits[0]
            if callback_value > self.behavior.limits[1]:
                callback_value = self.behavior.limits[1]

        if self.behavior.discrete:
            callback_value = int(callback_value)

        return callback_value

    def value_delta(self, value, previous_value):
        if self.input_type == Configuration.INPUT_ROTATION_LEFT:
            return abs(value)
        if self.input_type == Configuration.INPUT_ROTATION_RIGHT:
            return abs(value)
        if self.input_type == Configuration.INPUT_SET:
            return abs(value - previous_value)
        if self.input_type == Configuration.INPUT_PRESSED:
            return 1
        if self.input_type == Configuration.INPUT_RELEASED:
            return 1

    def mandatory(self, value):
        if (self.behavior.behavior == ComponentBehavior.TRIGGER and
                self.behavior.limits and value in self.behavior.limits):
            return True

    def redundant(self, value):
        if (self.behavior.behavior == ComponentBehavior.CYCLE and
                value == self.persistent_state['stored_value']):
            return True

        if (self.behavior.behavior == ComponentBehavior.ACCUMULATE and
                value == self.persistent_state['stored_value']):
            return True

    def run(self, value, previous_value):
        change = self.value_delta(value, previous_value)

        self.cumulative_change += change

        if FLAGS.debug:
            print('[0] Evaluating callback %s %s (%s/%s) value %s change %s' % (
                self.input_type, self.action_name,
                self.cumulative_change, self.threshold, value, change))

        callback_value = self.callback_value(value)

        if not self.mandatory(callback_value) and self.cumulative_change < self.threshold:
            return

        if self.redundant(callback_value):
            return

        print('[0] Triggered %s callback %s %s callback_value %s' % (
            self.behavior.behavior, self.input_type, self.action_name, callback_value))

        self.cumulative_change = 0
        self.persistent_state['stored_value'] = callback_value

        if self.behavior.nested:
            callback_value = (callback_value, self.behavior.items[callback_value])

        self.function(callback_value, *self.data)

        return callback_value


class ComponentBehavior(object):
    CYCLE = 'CYCLE'
    TRIGGER = 'TRIGGER'
    ACCUMULATE = 'ACCUMULATE'
    DELTA = 'DELTA'

    behavior: int
    items: Any
    limits: Tuple[int, int]
    loop: bool
    invert: bool
    nested: bool
    discrete: bool
    threshold: int
    value: Any
    default: Any
    data: Any
    action_config: Dict[Any, Any]

    def __init__(self, behavior=None, items=None, limits=None,
            loop=None, invert=None, nested=None, discrete=None,
            threshold=None, value=None, default=None, action_config=None,
            data=None):
        self.behavior = behavior
        self.items = items
        self.limits = limits
        self.loop = loop
        self.invert = invert
        self.nested = nested
        self.discrete = discrete
        self.threshold = threshold
        self.value = value
        self.default = default
        self.data = data
        self.action_config = action_config

    def finalize(self):
        if not self.data:
            self.data = ()
        if not self.items:
            self.set_items(())
        if not self.default:
            self.default = 0
        if self.discrete is None:
            self.discrete = True
        if not self.action_config:
            self.action_config = {}
        if not self.threshold:
            self.threshold = 1
        self.set_items(self.items)
        self.merge_config()

    def merge_config(self):
        if 'value' in self.action_config:
            self.value = self.action_config['value']
        if 'invert' in self.action_config:
            self.invert = self.action_config['invert']
        if 'loop' in self.action_config:
            self.loop = self.action_config['loop']
        if 'default' in self.action_config:
            self.default = self.action_config['default']
        if 'discrete' in self.action_config:
            self.discrete = self.action_config['discrete']
        if 'items' in self.action_config:
            self.set_items(self.action_config['items'])
        if 'limits' in self.action_config:
            self.limits = self.action_config['limits']
        if 'threshold' in self.action_config:
            self.threshold = self.action_config['threshold']

    def __repr__(self):
        return '<ComponentBehavior %s items=%s limits=%s loop=%s invert=%s threshold=%s>' % (
                self.behavior, self.items, self.limits,
                self.loop, self.invert, self.threshold)

    def __add__(self, other):
        ret = copy.deepcopy(self)
        if other.behavior is not None:
            ret.behavior = other.behavior
        if other.limits is not None:
            ret.limits = other.limits
        if other.items is not None:
            ret.set_items(self.items + other.items)
        if other.loop is not None:
            ret.loop = other.loop
        if other.invert is not None:
            ret.invert = other.invert
        if other.nested is not None:
            ret.nested = other.nested
        if other.discrete is not None:
            ret.discrete = other.discrete
        if other.threshold is not None:
            ret.threshold = other.threshold
        if other.value is not None:
            ret.value = other.value
        if other.default is not None:
            ret.default = other.default
        if other.data is not None:
            ret.data = other.data
        if other.action_config is not None:
            ret.action_config = other.action_config
        ret.finalize()
        return ret

    def set_items(self, items):
        self.items = items
        if len(items):
            self.limits = (0, len(items) - 1)

    def outside(self, value):
        if not self.limits:
            return False
        if self.limits[0] is not None and value < self.limits[0]:
            return True
        if self.limits[1] is not None and value > self.limits[1]:
            return True
        return False


# FIXME: duck pattern probably makes sense for this
class Component(object):
    KIND_BASE = 0
    KIND_BUTTON = 1
    KIND_DIAL = 2
    KIND_SLIDER = 3

    KIND_NAME_MAP = {
        KIND_BASE: "Base",
        KIND_BUTTON: "Button",
        KIND_DIAL: "Dial",
        KIND_SLIDER: "Slider",
    }

    def __init__(self, index, uid, kind, flip=False):
        self.index = index
        self.uid = uid
        self.kind = kind
        self.flip = flip
        self.persistent_state = {}

        self.screen_string = ''
        self.screen_display = Configuration.ICON_BLANK

        self.values = [0, 0, 0, 0, 0, 0, 0, 0]
        self.previous_values = [0, 0, 0, 0, 0, 0, 0, 0]

        self.callbacks = None
        self.hidkeys = None
        self.num_ports = None

        # FIXME: do these belong in ComponentLayout?
        self.children = {}
        self.parent = None
        self.parent_port = None
        self.slot = None
        self.orientation = None
        self.led = (255, 255, 255)

        self.reset()

        self.set_sensitivity(9)

    def __repr__(self):
        return '<%s index=%d uid="%s" value="%s" orientation=%d flip=%s>' % (
                self.kind_name(), self.index, self.uid, self.values, self.orientation, self.flip)

    def reset(self):
        # TODO: should we also reset persistent_state here?
        self.callbacks = {}
        self.hidkeys = []

    def set_sensitivity(self, sensitivity):
        self.sensitivity = sensitivity

    def dominant_value(self, input_type):
        vindex = self.determine_vindex(input_type)
        return self.values[vindex]

    def determine_vindex(self, input_type):
        if input_type == Configuration.INPUT_PRESSED:
            return 0
        if input_type == Configuration.INPUT_RELEASED:
            return 0
        if self.kind == Component.KIND_DIAL:
            if input_type == Configuration.INPUT_SET:
                return 3
            if input_type == Configuration.INPUT_ROTATION_LEFT:
                return 1
            if input_type == Configuration.INPUT_ROTATION_RIGHT:
                return 2
        if self.kind == Component.KIND_SLIDER:
            return 0
        return 0

    def determine_input_types(self):
        input_types = set()

        if self.value_changed(0) and self.kind != Component.KIND_SLIDER:
            if self.values[0] == 1:
                input_types.add(Configuration.INPUT_PRESSED)
            if self.values[0] == 0:
                input_types.add(Configuration.INPUT_RELEASED)

        if self.kind == Component.KIND_DIAL:
            if self.value_changed(3):
                input_types.add(Configuration.INPUT_SET)
            if self.values[2] > 0:
                input_types.add(Configuration.INPUT_ROTATION_RIGHT)
            if self.values[1] > 0:
                input_types.add(Configuration.INPUT_ROTATION_LEFT)

        if self.kind == Component.KIND_SLIDER:
            input_types.add(Configuration.INPUT_SET)

        return list(input_types)

    def set_callback(self, input_type, action_name, behavior, callback, action_config):
        if behavior is None:
            return
        vindex = self.determine_vindex(input_type)
        print('[0] Bound callback %s %s (%s) to component %s' % (input_type, action_name, behavior.behavior, self.uid))
        invocation = ComponentInvocation(
                input_type, action_name, behavior,
                callback, vindex, action_config, self.persistent_state)
        self.callbacks[input_type] = invocation

    def invoke_callback(self, input_type):
        if input_type not in self.callbacks:
            return
        invocation = self.callbacks[input_type]
        vindex = self.determine_vindex(input_type)
        return invocation.run(self.values[vindex], self.previous_values[vindex])

    def set_hidkey(self, control, key, mod, repeat):
        self.hidkeys.append((control, key, mod, repeat))

    def set_orientation(self, orientation):
        self.orientation = orientation
        self.flip = False
        if self.kind == Component.KIND_SLIDER and orientation in (90, 180):
            self.flip = True

    def kind_name(self):
        return Component.KIND_NAME_MAP[self.kind]

    def value_changed(self, vindex):
        if len(self.previous_values) < vindex + 1:
            return True
        return self.previous_values[vindex] != self.values[vindex]


class ComponentLayout(object):
    components: Dict[str, Component]
    components_index: Dict[int, Component]
    components_slot: Dict[Tuple[int, int], Component]

    def __init__(self, layout_dict=None, orientation=0):
        self.base_orientation = orientation
        self.components = {}
        self.components_index = {}
        self.components_slot = {}
        self.layout_dict = {}
        if layout_dict:
            self.update(layout_dict)

    def __len__(self):
        return len(self.components)

    def update(self, layout_dict):
        self.components_index = {}
        self.components_slot = {}
        self.traverse(layout_dict)
        self.layout_dict = layout_dict

    def traverse(self, layout_dict, parent=None, port=None):
        if not layout_dict:
            return None

        # FIXME: the leading "  " in uid may be significant.
        # Maybe these are meant to be parsed into a number?
        uid = layout_dict["u"].lstrip()
        kind = layout_dict["t"]
        index = layout_dict["i"]
        conns = layout_dict["c"]

        orientation = self.calculate_orientation(parent, port)
        slot = self.calculate_slot(parent, port)

        component = self.components.get(uid,
                Component(index, uid, kind))
        component.index = index

        # TODO: consider always creating a new Component
        #component.reset()
        component.set_orientation(orientation)
        component.num_ports = len(conns)

        # FIXME: move these to be parameters on ComponentLayout
        component.parent = parent
        component.parent_port = port
        component.slot = slot
        component.children = {}

        for port, c in enumerate(conns):
            component.children[port] = self.traverse(c, component, port)

        self.components[uid] = component
        self.components_index[index] = uid
        self.components_slot[slot] = uid

        return component

    def calculate_slot(self, parent, port):
        if not parent:
            return (0,0)
        slot_calculator = ambit.coordinates.calculate_female_slots
        if parent.num_ports == 5:
            slot_calculator = ambit.coordinates.calculate_female_slots_wide
        return slot_calculator(parent.slot, parent.orientation)[port]

    def calculate_orientation(self, parent, port):
        if port is None:
            return self.base_orientation

        # this is arcane magic.
        # on a double-width component (5 female ports),
        # ports 2 and 3 face the same orientation as port 1 on square
        # port 4 has same orientation as port 2 on square
        # port 1 has same orientation as port 0 on square
        # port 0 has no equivalent but we need it to rotate -90 degrees
        if parent.num_ports == 5:
            if port == 0:
                port = -1
            else:
               port = int(port / 2.0)

        orientation = (parent.orientation - 90) + (port * 90)

        return orientation % 360

    def connected(self):
        components = []
        for index in sorted(self.components_index):
            uid = self.components_index[index]
            components.append(self.components[uid])
        return components

    def connected_rowwise(self):
        return sorted(self.connected(), key=lambda x: x.slot)

    # TODO: this does not need to be a class method
    def parse_query(self, query):
        if not (query.startswith('[') and query.endswith(']')):
            return {'uid': query}, None

        search_kwargs = {}

        # Parse the matcher portion of the query.
        matcher, *filters = query.lstrip('[').rstrip(']').split(' | ')
        matcher_parts = matcher.split(' ')
        for mp in matcher_parts:
            k, _, v = mp.partition('=')
            if k == 'kind':
                for kind, kind_name in Component.KIND_NAME_MAP.items():
                    if v == kind_name:
                        v = kind
                        break
            if k == 'index':
                v = int(v)
            if k == 'orientation':
                v = int(v)
            if k == 'slot':
                x, y = v.lstrip('(').rstrip(')').split(',')
                v = (int(x), int(y))
            search_kwargs[k] = v

        # Parse the filters.
        select = None
        for f in filters:
            if f == 'rowwise':
                search_kwargs['rowwise'] = True
            if f.startswith('select('):
                select = int(f.lstrip('select(').rstrip(')'))

        return search_kwargs, select

    def query(self, query):
        search_kwargs, select = self.parse_query(query)
        components = self.search(**search_kwargs)
        if select is not None:
            if len(components) < select:
                # FIXME: need better error handling for this case.
                print('[!] Query contains select with invalid index.')
            components = [components[select - 1]]
        #print('[D] Query %s matched components: %s' % (query, components))
        return components

    def search(self, uid=None, kind=None, index=None, slot=None, orientation=None, rowwise=False):
        components = []
        for component in self.connected():
            if uid is not None and component.uid != uid:
                continue
            if kind is not None and component.kind != kind:
                continue
            if slot is not None and component.slot != slot:
                continue
            if index is not None and component.index != index:
                continue
            if orientation is not None and component.orientation != orientation:
                continue
            components.append(component)
        if rowwise:
            components = sorted(components, key=lambda x: x.slot)
        return components

    def find_component(self, index):
        if index not in self.components_index:
            return None
        uid = self.components_index[index]
        if uid not in self.components:
            return None
        return self.components[uid]

    def extrema(self):
        min_x, min_y = max_x, max_y = (0,0)
        for component in self.connected():
            x, y = component.slot
            # TODO: move this into component.dimensions?
            # in general, consolidate the uses of
            # component.orientation to fewer places.
            if component.num_ports == 5:
                if component.orientation == 0:
                    x += 1
                if component.orientation == 90:
                    y -= 1
                if component.orientation == 180:
                    x -= 1
                if component.orientation == 270:
                    y += 1
            if x < min_x:
                min_x = x
            if y < min_y:
                min_y = y
            if x > max_x:
                max_x = x
            if y > max_y:
                max_y = y
        return min_x, min_y, max_x, max_y

    def component_in_slot(self, slot):
        if slot not in self.components_slot:
            return None
        uid = self.components_slot[slot]
        return self.components[uid]
