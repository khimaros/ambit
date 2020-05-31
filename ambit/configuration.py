#!/usr/bin/env python3

import json

from typing import Any, Callable, Dict, List, Tuple


class Profile(object):
    title: str
    icon: int
    action_map: Dict
    orientation: int

    def __init__(self):
        self.title = "PALETTE"
        self.icon = Configuration.ICON_PALETTE
        self.action_map = {}
        self.media_map = {}
        self.joystick_map = {}
        self.color_map = {}
        self.key_map = {}
        self.layout = {}
        self.orientation = 0


class Configuration(object):
    ACTION_PROFILE_PREV = 'previousFunction'
    ACTION_PROFILE_NEXT = 'nextFunction'
    ACTION_PROFILE_SWITCH = 'switchFunctions'
    ACTION_TOGGLE_PREVIEW = 'togglePreview'
    ACTION_SET_COLOR_RED = 'setColorRed'
    ACTION_SET_COLOR_GREEN = 'setColorGreen'
    ACTION_SET_COLOR_BLUE = 'setColorBlue'
    ACTION_EXECUTE_COMMAND = 'executeCommand'
    ACTION_CYCLE_MAPPING = 'cycleMapping'

    ACTION_TEST_CYCLE = 'testCycle'
    ACTION_TEST_ACCUMULATE = 'testAccumulate'
    ACTION_TEST_DELTA = 'testDelta'
    ACTION_TEST_TRIGGER = 'testTrigger'

    # FIXME: add behavior: keywords and mappings

    INPUT_PRESSED = 'pressed'
    INPUT_RELEASED = 'released'
    INPUT_LONG_PRESSED = 'long_pressed'
    INPUT_ROTATION_RIGHT = 'rotation_right'
    INPUT_ROTATION_LEFT = 'rotation_left'
    INPUT_ROTATION = 'rotation'
    INPUT_SET = 'set'
    INPUT_MIXED = 'mixed'

    INPUT_MAP = {
        0: INPUT_PRESSED,
        1: INPUT_ROTATION_RIGHT,
        2: INPUT_ROTATION_LEFT,
    }

    ICON_PALETTE = 0
    ICON_PHOTOSHOP = 1
    ICON_LIGHTROOM = 2
    ICON_AE = 3
    ICON_MIDI = 4
    ICON_KEYS = 5
    ICON_AI = 6
    ICON_JOYSTICK = 7
    ICON_COPYRIGHT = 8
    ICON_ID = 9
    ICON_PR = 10
    ICON_VIDEO = 11
    ICON_AU = 12
    ICON_CAPITAL_ONE = 13
    ICON_CHROME = 14
    ICON_SPOTIFY = 15
    ICON_MUSIC = 16
    ICON_VLC = 17
    ICON_CH = 18
    ICON_MEDIA = 19
    ICON_FLT = 20
    ICON_GEAR = 21
    #ICON_PALETTE = 22  # duplicate
    ICON_SHELL = 23
    ICON_HOME = 24
    ICON_BLANK = 25

    QT_KEY_MAP = {
        0x01000020: "PK_MOD_LSHIFT",
        0x01000021: "PK_MOD_LCTRL",
        0x01000022: "PK_MOD_LMETA",
        0x01000023: "PK_MOD_LALT",
    }

    HID_KEY_MAP = {
        "PK_MOD_LCTRL": 0x01,
        "PK_MOD_LSHIFT": 0x02,
        "PK_MOD_LALT": 0x04,
        "PK_MOD_LMETA": 0x08,
        "PK_MOD_RCTRL": 0x10,
        "PK_MOD_RSHIFT": 0x20,
        "PK_MOD_RALT": 0x40,
        "PK_MOD_RMETA": 0x80,
        "PK_NONE": 0x00,
        "PK_ERR_OVF": 0x01,
        "PK_A": 0x04,
        "PK_B": 0x05,
        "PK_C": 0x06,
        "PK_D": 0x07,
        "PK_E": 0x08,
        "PK_F": 0x09,
        "PK_G": 0x0a,
        "PK_H": 0x0b,
        "PK_I": 0x0c,
        "PK_J": 0x0d,
        "PK_K": 0x0e,
        "PK_L": 0x0f,
        "PK_M": 0x10,
        "PK_N": 0x11,
        "PK_O": 0x12,
        "PK_P": 0x13,
        "PK_Q": 0x14,
        "PK_R": 0x15,
        "PK_S": 0x16,
        "PK_T": 0x17,
        "PK_U": 0x18,
        "PK_V": 0x19,
        "PK_W": 0x1a,
        "PK_X": 0x1b,
        "PK_Y": 0x1c,
        "PK_Z": 0x1d,
        "PK_1": 0x1e,
        "PK_2": 0x1f,
        "PK_3": 0x20,
        "PK_4": 0x21,
        "PK_5": 0x22,
        "PK_6": 0x23,
        "PK_7": 0x24,
        "PK_8": 0x25,
        "PK_9": 0x26,
        "PK_0": 0x27,
        "PK_RETURN": 0x28,
        "PK_ESCAPE": 0x29,
        "PK_BACKSPACE": 0x2a,
        "PK_TAB": 0x2b,
        "PK_SPACE": 0x2c,
        "PK_MINUS": 0x2d,
        "PK_EQUAL": 0x2e,
        "PK_LEFTBRACE": 0x2f,
        "PK_RIGHTBRACE": 0x30,
        "PK_BACKSLASH": 0x31,
        "PK_HASHTILDE": 0x32,
        "PK_SEMICOLON": 0x33,
        "PK_APOSTROPHE": 0x34,
        "PK_GRAVE": 0x35,
        "PK_COMMA": 0x36,
        "PK_DOT": 0x37,
        "PK_SLASH": 0x38,
        "PK_CAPSLOCK": 0x39,
        "PK_F1": 0x3a,
        "PK_F2": 0x3b,
        "PK_F3": 0x3c,
        "PK_F4": 0x3d,
        "PK_F5": 0x3e,
        "PK_F6": 0x3f,
        "PK_F7": 0x40,
        "PK_F8": 0x41,
        "PK_F9": 0x42,
        "PK_F10": 0x43,
        "PK_F11": 0x44,
        "PK_F12": 0x45,
        "PK_SYSRQ": 0x46,
        "PK_SCROLLLOCK": 0x47,
        "PK_PAUSE": 0x48,
        "PK_INSERT": 0x49,
        "PK_HOME": 0x4a,
        "PK_PAGEUP": 0x4b,
        "PK_DELETE": 0x4c,
        "PK_END": 0x4d,
        "PK_PAGEDOWN": 0x4e,
        "PK_RIGHT": 0x4f,
        "PK_LEFT": 0x50,
        "PK_DOWN": 0x51,
        "PK_UP": 0x52,
        "PK_NUMLOCK": 0x53,
        "PK_KPSLASH": 0x54,
        "PK_KPASTERISK": 0x55,
        "PK_KPMINUS": 0x56,
        "PK_KPPLUS": 0x57,
        "PK_KPENTER": 0x58,
        "PK_KP1": 0x59,
        "PK_KP2": 0x5a,
        "PK_KP3": 0x5b,
        "PK_KP4": 0x5c,
        "PK_KP5": 0x5d,
        "PK_KP6": 0x5e,
        "PK_KP7": 0x5f,
        "PK_KP8": 0x60,
        "PK_KP9": 0x61,
        "PK_KP0": 0x62,
        "PK_KPDOT": 0x63,
        "PK_102ND": 0x64,
        "PK_COMPOSE": 0x65,
        "PK_POWER": 0x66,
        "PK_KPEQUAL": 0x67,
        "PK_F13": 0x68,
        "PK_F14": 0x69,
        "PK_F15": 0x6a,
        "PK_F16": 0x6b,
        "PK_F17": 0x6c,
        "PK_F18": 0x6d,
        "PK_F19": 0x6e,
        "PK_F20": 0x6f,
        "PK_F21": 0x70,
        "PK_F22": 0x71,
        "PK_F23": 0x72,
        "PK_F24": 0x73,
        "PK_OPEN": 0x74,
        "PK_HELP": 0x75,
        "PK_PROPS": 0x76,
        "PK_FRONT": 0x77,
        "PK_STOP": 0x78,
        "PK_AGAIN": 0x79,
        "PK_UNDO": 0x7a,
        "PK_CUT": 0x7b,
        "PK_COPY": 0x7c,
        "PK_PASTE": 0x7d,
        "PK_FIND": 0x7e,
        "PK_MUTE": 0x7f,
        "PK_VOLUMEUP": 0x80,
        "PK_VOLUMEDOWN": 0x81,
        "PK_KPCOMMA": 0x85,
        "PK_RO": 0x87,
        "PK_KATAKANAHIRAGANA": 0x88,
        "PK_YEN": 0x89,
        "PK_HENKAN": 0x8a,
        "PK_MUHENKAN": 0x8b,
        "PK_KPJPCOMMA": 0x8c,
        "PK_HANGEUL": 0x90,
        "PK_HANJA": 0x91,
        "PK_KATAKANA": 0x92,
        "PK_HIRAGANA": 0x93,
        "PK_ZENKAKUHANKAKU": 0x94,
        "PK_KPLEFTPAREN": 0xb6,
        "PK_KPRIGHTPAREN": 0xb7,
        "PK_LEFTCTRL": 0xe0,
        "PK_LEFTSHIFT": 0xe1,
        "PK_LEFTALT": 0xe2,
        "PK_LEFTWINDOWS": 0xe3,
        "PK_NOT_A_KEY": 0xe3,
        "PK_RIGHTCTRL": 0xe4,
        "PK_RIGHTSHIFT": 0xe5,
        "PK_RIGHTALT": 0xe6,
        "PK_RIGHTMETA": 0xe7,
        "PK_MEDIA_PLAYPAUSE": 0xe8,
        "PK_MEDIA_STOPCD": 0xe9,
        "PK_MEDIA_PREVIOUSSONG": 0xea,
        "PK_MEDIA_NEXTSONG": 0xeb,
        "PK_MEDIA_EJECTCD": 0xec,
        "PK_MEDIA_VOLUMEUP": 0xed,
        "PK_MEDIA_VOLUMEDOWN": 0xee,
        "PK_MEDIA_MUTE": 0xef,
        "PK_MEDIA_WWW": 0xf0,
        "PK_MEDIA_BACK": 0xf1,
        "PK_MEDIA_FORWARD": 0xf2,
        "PK_MEDIA_STOP": 0xf3,
        "PK_MEDIA_FIND": 0xf4,
        "PK_MEDIA_SCROLLUP": 0xf5,
        "PK_MEDIA_SCROLLDOWN": 0xf6,
        "PK_MEDIA_EDIT": 0xf7,
        "PK_MEDIA_SLEEP": 0xf8,
        "PK_MEDIA_COFFEE": 0xf9,
        "PK_MEDIA_REFRESH": 0xfa,
        "PK_MEDIA_CALC": 0xfb,
    }

    ICON_TYPE_MAP = {
        'Keyboard': ICON_KEYS,
        'Joystick': ICON_JOYSTICK,
        'MIDI': ICON_MIDI,
        'Palette': ICON_PALETTE,
        'Video': ICON_VIDEO,
        'Settings': ICON_GEAR,
        'Media': ICON_MEDIA,
        'Music': ICON_MUSIC,
        'Shell': ICON_SHELL,
        'Home': ICON_HOME,
    }

    profile_index: int
    profile: Profile
    profiles: List[Profile]

    def __init__(self, paths=None):
        self.profile_index = 0
        self.profile = Profile()
        self.profiles = []
        if not paths:
            return
        for path in paths:
            with open(path, 'r') as f:
                config_bytes = f.read()
            config_dict = json.loads(config_bytes)
            profile = Profile()
            profile.title = config_dict['title']
            profile.icon = Configuration.ICON_TYPE_MAP[config_dict['tabType']]
            profile.action_map = config_dict['module_mappings'].get('actionMap', {})
            profile.media_map = config_dict['module_mappings'].get('mediaMap', {})
            profile.key_map = config_dict['module_mappings'].get('keyMap', {})
            profile.layout = config_dict.get('layout', {})
            profile.orientation = config_dict.get('orientation', 0)
            self.profiles.append(profile)
        self.switch(0)

    def switch(self, index):
        self.profile_index = index
        self.profile = self.profiles[index]
        print('[0] Switched to profile %d: %s' % (index, self.profile.title))

    def prev(self):
        index = self.profile_index - 1
        if index < 0:
            index = len(self.profiles) - 1
        self.switch(index)

    def next(self):
        index = self.profile_index + 1
        if index > len(self.profiles) - 1:
            index = 0
        self.switch(index)

    def component_hidkeys(self, uid):
        component_hidkeys = []
        for control in self.profile.key_map.get(uid, {}):
            bind_config = self.profile.key_map[uid].get(control, {})
            key = Configuration.HID_KEY_MAP[bind_config['virtual_code']]
            mod = 0
            for mc in bind_config['modifier_codes']:
                if type(mc) is int:
                    mc = Configuration.QT_KEY_MAP[mc]
                mod += Configuration.HID_KEY_MAP[mc]
            repeat = bind_config.get('dial_sensitivity', 1)
            if repeat != 1:
                repeat = 8
            component_hidkeys.append((control, key, mod, repeat))
        return component_hidkeys

    def components(self):
        """Return the list of configured components."""
        matchers = set()
        for uid_query in self.profile.action_map:
            matchers.add(uid_query)
        for uid_query in self.profile.media_map:
            matchers.add(uid_query)
        return sorted(list(matchers))

    def component_actions(self, uid):
        component_actions = []
        for input_type in self.profile.action_map.get(uid, {}):
            action_config = self.profile.action_map[uid].get(input_type, {})
            if 'action' not in action_config:
                continue
            action_name = action_config['action']
            component_actions.append((input_type, action_name, action_config))
        media_action = self.profile.media_map.get(uid, {})
        if media_action:
            action_name = media_action['key']
            input_type = Configuration.INPUT_MIXED
            component_actions.append((input_type, action_name, media_action))
        return component_actions

    def set_component_actions(self, uid, mapping):
        self.profile.action_map[uid] = mapping
