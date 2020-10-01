# CONFIG

Upstream PLP files are partially supported.

The majority of ambit functionality uses a new `mapping_module` section
`actionMap`. The actions defined here are not supported by upstream PaletteApp.

## tabType

Used by Ambit to choose screen image.

May have other behavior with upstream PaletteApp.

type: string

implemented: partial

valid options (upstream): Palette, Joystick, Keyboard, Media

valid options (ambit): Palette, Joystick, Keyboard, Media, Home, Shell

## title

type: string

String to display on the screen.

Length should be <= 11 bytes.

## orientation

Set the base orientation for the entire layout.

type: int

valid options: 0, 90, 180, 270

default: 0

ambit-only: true

0 degrees means toward the USB connector and progresses clockwise.

## module\_mappings

implemented: partial

type: dict

keys: keyMap, colorMap, mediaMap, actionMap

```
"module_mappings": {
  "keyMap": { },
  "colorMap": { },
  "actionMap": { }
}
```

### actionMap

Map behaviors to components.

implemented: true

ambit-only: true

```
"actionMap": {
  "<query>": {
    "<input_type>": { "action": "<action_type>", [params] }
  }
}
```

#### query

Query used to choose the component this action should be assigned to.

If the query is not enclosed by `[ ]` it will be intepreted as the
raw uid of the component.

Queries can match a component based on its position and other
attributes, both ephemeral and persistent.

This supports any search string supported by `ComponentLayout.query()`

See also: [QUERY.md](QUERY.md)

For example `[kind=Slider | rowwise | select(1)]` would refer to the slider
which was second from the top left (rowwise).

When a query returns multiple components, the first will be selected by default.

Queries are resolved to uids each time the layout changes.

#### input\_type

The particular input to assign this action to.

type: string

Supported inputs differ by component kind.

 * pressed (Button, Dial)
 * released (Button, Dial)
 * rotation\_right (Dial)
 * rotation\_left (Dial)
 * set (Dial, Slider)

#### action\_type

type: string

Must be a registered action. Actions registered by the default
ambit Controller are documented below.

##### previousFunction

supported behaviors: TRIGGER, ACCUMULATE

Switch to the previous configuration if multiple are loaded,
looping around to the end.

##### nextFunction

supported behaviors: TRIGGER, ACCUMULATE

Switch to the next configuration if multiple are loaded,
looping around to the start.

##### switchFunctions

supported behaviors: TRIGGER, ACCUMULATE

Cycle through configurations if multiple are loaded. Honors
the `invert` behavior parameter, thus behaves predictably for
Dial right and left rotation.

##### setColor{Red,Green,Blue}

supported behaviors: TRIGGER, ACCUMULATE

Set the RGB color of all attached component LEDs.

##### executeCommand

supported behaviors: TRIGGER, ACCUMULATE, DELTA

Invokes the specified `argv` (list of str) as a subprocess.

environment: `AMBIT_VALUE` set to the current component value.

other environment variables are passed through unmodified.

argv will substitute any instance of `%AMBIT_VALUE%` with the
current value.

Anything printed to stdout will be displayed to the device screen.

Could be combined with something lik https://github.com/mel00010/OmniPause
for system wide media control.

##### cycleMapping

supported behaviors: CYCLE

Cycle through alternative actionMaps on a `target` component..

fields: target (component uid), map (dict)

`map` supports the same values as `actionMap`.

#### params

##### threshold

Threshold for invoking callbacks.

type: int

default: 1

supported behaviors: (ALL)

If defined, callbacks will only be invoked when the cumulative change
is greater than the threshold.

##### items

supported behaviors: CYCLE

##### value

supported behaviors: (ALL)

##### default

supported behaviors: (ALL)

##### limits

supported behaviors: ACCUMULATE, TRIGGER, CYCLE

##### loop

supported behaviors: CYCLE

##### discrete

use discrete (integer) values

supported behaviors: TRIGGER

type: bool

##### behavior

Set the behavior of a component.

type: string

valid options: TRIGGER, DELTA, ACCUMULATE, CYCLE

default: varies by component kind and action definition.

See also: [BEHAVIOR.md](BEHAVIOR.md)

### mediaMap

Map meta functionality to components.

implemented: partial

```
"mediaMap": {
  "<uid>": {
    "key": "<action>",
    "sensitivity": 9 }
  }
}
```

actions: togglePreview, switchFunctions

#### switchFunctions

Switch to the next configuration profile.

implemented: true

See also: actionMap > switchFunctions

#### togglePreview

Display the currently selected layout as a GUI overlay.

implemented: false

### joystickMap

Map joystick behavior to components.

implemented: false

### shortcutsMap

Human friendly name for components.

implemented: false

```
"shortcutsMap": { "<uid>": "<string>" }
```

### macroMap

implemented: false

### menuBarMap

implemented: false

### colorMap

Specify the default color for component LEDs.

implemented: false

```
"colorMap": {
  "<uid>": "#ffffff"
}
```

### keyMap

Bind HID keys to component input.

implemented: partial

```
"keyMap": {
  "<uid>": {
    <input_id>: {
      "code": "<string>",
      "label": "<string>",
      "modifier_codes": [<int>, ...],
      "virtual_code": "PK_<string>",
    }
  }
}
```

## os

Define the operating system for binding values.

implemented: false

type: string

valid options: windows, mac

## priorities

Unknown.

type: list of string (uid)

implemented: false

## tabUuid

Unique ID to represent this configuration.

type: string

implemented: false

UUID is of the form: `\{[a-z0-9]{3}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{12}\}`

## app\_version

The version of PaletteApp used to create this config.

type: string

implemented: false

## midiChannel

MIDI channel used when mapping USB MIDI notes.

implemented: false

type: int

default: -1

## layout

Define the expected layout of the physical device.

type: dict

implemented: false

