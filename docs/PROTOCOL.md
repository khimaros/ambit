# PROTOCOL

## CONTROL HANDSHAKE

```
HANDSHAKE PAYLOAD := E0 93 04 00 00 00 08
```

In the event of an unexpected disconnect, it can be useful to
perform a `BULK IN` read on startup and discard the result.

### [MESSAGE 1]

```
SEND => URB_CONTROL (IN):
	Endpoint: 0x80 (IN)
	Device setup request: relevant (0x00)
	Data: not present (0x3c)
	URB type: URB_SUBMIT ('S')
	URB length [bytes]: 7
	Data length [bytes]: 0
	Setup Data:
		bmRequestType: 0xa1
		bRequest: 0x21
```
```
RECV <= URB_CONTROL (IN):
	Endpoint: 0x80 (IN)
	URB type: URB_COMPLETE ('C')
	URB status: Success (0)
	URB length [bytes]: 7
	Data length [bytes]: 7
	CONTROL response data: {{ CONTROL PAYLOAD }}
```

### [MESSAGE 2]

```
SEND => URB_CONTROL (OUT):
	Endpoint: 0x00 (OUT)
	Device setup request: relevant (0x00)
	Data: present (0x00)
	URB type: URB_SUBMIT ('S')
	URB length [bytes]: 7
	Data length [bytes]: 7
	Setup Data:
		bmRequestType: 0x21
		bRequest: 0x20
		Data Fragment: {{ CONTROL PAYLOAD }}
```
```
RECV => URB_CONTROL (OUT):
	Endpoint: 0x00 (OUT)
	Device setup request: not relevant (0x2d)
	Data: not present (0x3e)
	URB type: URB_COMPLETE ('C')
	URB status: Success (0)
	URB length [bytes]: 7
	Data length [bytes]: 0
```

### [MESSAGE 3]

```
SEND => URB_CONTROL (IN):
	Endpoint: 0x80 (IN)
	Device setup request: relevant (0x00)
	Data: not present (0x3c)
	URB type: URB_SUBMIT ('S')
	URB length [bytes]: 7
	Data length [bytes]: 0
	Setup Data:
		bmRequestType: 0xa1
		bRequest: 0x21
```
```
RECV <= URB_CONTROL (IN):
	Endpoint: 0x80 (IN)
	Device setup request: not relevant (0x2d)
	Data: present (0x00)
	URB type: URB_COMPLETE ('C')
	URB status: Success (0)
	URB length [bytes]: 7
	Data length [bytes]: 7
	CONTROL response data: {{ CONTROL PAYLOAD }}
```

### [MESSAGE 4]

```
SEND => URB_CONTROL (OUT):
	Endpoint: 0x00 (OUT)
	Device setup request: relevant (0x00)
	Data: present (0x00)
	URB type: URB_SUBMIT ('S')
	URB length [bytes]: 7
	Data length [bytes]: 0
	Setup Data:
		bmRequestType: 0x21
		bRequest: 0x22
```
```
RECV <= URB_CONTROL (OUT):
	Endpoint: 0x00 (OUT)
	Device setup request: not relevant (0x2d)
	Data: not present (0x3e)
	URB type: URB_COMPLETE ('C')
	URB status: Success (0)
	URB length [bytes]: 0
	Data length [bytes]: 0
```

### [MESSAGE 5]

```
SEND => URB_CONTROL (OUT):
	Endpoint: 0x00 (OUT)
	Device setup request: relevant (0x00)
	Data: present (0x00)
	URB type: URB_SUBMIT ('S')
	URB length [bytes]: 7
	Data length [bytes]: 7
	Setup Data:
		bmRequestType: 0x21
		bRequest: 0x20
		Data Fragment: {{ CONTROL PAYLOAD }}
```
```
RECV <= URB_CONTROL (OUT):
	Endpoint: 0x00 (OUT)
	Device setup request: not relevant (0x2d)
	Data: not present (0x3e)
	URB type: URB_COMPLETE ('C')
	URB status: Success (0)
	URB length [bytes]: 0
	Data length [bytes]: 0
```

### [MESSAGE 6]

```
SEND => URB_CONTROL (IN):
	Endpoint: 0x80 (IN)
	Device setup request: relevant (0x00)
	Data: not present (0x3c)
	URB type: URB_SUBMIT ('S')
	URB length [bytes]: 7
	Data length [bytes]: 0
	Setup Data:
		bmRequestType: 0xa1
		bRequest: 0x21
```
```
RECV <= URB_CONTROL (IN):
	Endpoint: 0x80 (IN)
	Device setup request: not relevant (0x2d)
	Data: present (0x00)
	URB type: URB_COMPLETE ('C')
	URB status: Success (0)
	URB length [bytes]: 7
	Data length [bytes]: 7
	CONTROL response data: {{ CONTROL PAYLOAD }}
```

## BULK MODE

Messages are essentially minified JSON, except that dictionaries
can be concatenated together in a single message.

Messages can be concatenated, eg. `{"hidmap":[]}{"joymap":[]}`

### Start the device

SEND => BULK OUT (start)
RECV <= BULK OUT (empty)

### Request current layout

SEND => BULK IN (empty)
RECV <= BULK IN (layout) # requires explicit read

### Initialize configuration

SEND => BULK OUT (hidmap/joymap/midimap/led)
RECV <= BULK OUT (empty)

### Send new configuration

...

### Continue throughout connection lifetime:

SEND => BULK OUT (check)
RECV <= BULK OUT (empty)

SEND => BULK IN (empty)
RECV <= BULK IN (layout/input)

## === MSGPACK payload details ===

Entirely uninformative msgpack spec is here: https://github.com/msgpack/msgpack/blob/master/spec.md

MSGPACK payloads are of the form:

```
7E <MESSAGE> 7E
```

MESSAGE is of the form:

```
<TYPE> <DATA>
```

Messages can be concatenated to a single bulk transfer and can span multiple messages.

TYPE is 1 byte in length.

  - 81: tuple (str => bytes...)
  - 82: list of typed objects
  - 84: map (str => typed object)
  - 89: tuple (str => bytes, not length encoded) -- odd, maybe custom parsing

When TYPE == 81, DATA is of the form:

```
<LEN> <KEY> <VAL>
```

`<LEN>` is a single byte containing 160 + the length of the key in bytes.

For example `A9` means the key is 9 bytes long, `AA` means 12 bytes, `B2` means...

`<KEY>` is interpreted as an ASCII string.

When TYPE == 82, <DATA> is a list and each element is encoded as...

```
<ITEMTYPE> <ITEMDATA>
```

ITEMDATA follows the same rules as DATA above.

When TYPE == 84:

`C0 C0 C0` denotes end of map.

When TYPE == 89, <VAL> is a list

### HOST => DEVICE

#### 81 A9 `get_check`

Length: 1 byte

Sent every few seconds as a keepalive.

```
C3
```

Device responds with `l_time`

#### 81 A9 `get_state`

```
01
```

#### 81 AC `clear_action`

Length: 1 byte

Seen values:

```
00
01
02
```

BYTE 0: index of action to clear

#### 81 AA `get_layout`

Length: 1 byte

```
C3
```

#### 81 AB `get_version`

Length: 1 byte

```
C3
```

#### 81 AA `set_module`

Length: 8 bytes, varies

Likely includes function and color information?

Hypothesis:

```
BYTE 0: 0x93 == set color
BYTE 1: module index
BYTE 2: number of LEDs???
BYTE 3: 0xCE == set RGB
	BYTE 4: input index
	BYTE 5,6,7: BGR color
BYTE 3: 0xCC == set lower bit / red?
	BYTE 4: value for R (G,B=0)
BYTE 3: 0xCD == set lower two bits
	BYTE 4,5: value for G,R (B=0)
BYTE 3: 0x00 == all off / black
```

```
# core module
93 00 02 CE 00 FF FF FF		# white
93 00 02 CE 00 36 3B EF		# rose
93 00 02 CE 00 40 00 FF		# hot pink
93 00 02 CE 00 FF 00 FF		# magenta
93 00 02 CC FF			# red
93 00 02 CD 40 FF		# orange
93 00 02 CD 8F FF		# yellow
93 00 02 CE 00 71 1C 3A		# violet
93 00 02 CE 00 FF 00 00		# blue
93 00 02 CE 00 EB EB 0C		# sky blue
93 00 02 CE 00 7D 5D FF 00	# teal ???
93 00 02 CD FF 00		# green
93 00 02 CE 00 25 8B 68		# sea foam
93 00 02 00			# black
93 00 02 CE 00 FF FF FF		# white

# dial module (left)
93 01 05 CE 00 FF FF FF		# white
93 01 05 CE 01 FF FF FF		# white
93 01 05 CE 02 FF FF FF		# white
93 01 05 CE 7F 00 00 00		# finished?

93 01 05 CE 00 FF FF FF		# white
93 01 05 CE 01 FF FF FF		# white
93 01 05 CE 02 36 3B EF		# rose
93 01 05 CE 7F 00 00 00		# finished?

should figure out how red is represented here.

...

# orbiter
93 02 02 CE 00 FF FF FF		# white
93 02 02 CE 00 36 3B EF		# rose
93 02 02 CE 00 40 00 FF		# hot pink
93 02 02 CE 00 FF 00 FF		# magenta
93 02 02 CC FF			# red
93 02 02 CD 40 FF		# orange
93 02 02 CD 8F FF		# yellow
93 02 02 CE 00 71 1C 3A		# violet
93 02 02 CE 00 FF 00 00		# blue
93 02 02 CE 00 EB EB 0C		# sky blue
93 02 02 CE 00 7D 5D FF 00	# teal (WTF?!)
93 02 02 CD FF 00		# green
93 02 02 CE 00 25 8B 68		# sea foam
93 02 02 00			# black
93 02 02 CE 00 FF FF FF		# white
```

#### 81 B2 `write_display_slow`

Send display image to the device.

#### 81 A4 `flip`

Length: 8 bytes

BYTE 0: 0x91
BYTE 1: 0x82 encoded map follows?
BYTE 2: 0xA1 string follows (1 byte)
BYTE 3: 0x69 'i'
BYTE 4: ???
BYTE 5: 0xA1 string follows (1 byte)
BYTE 6: 0x6D 'm'
BYTE 7: ???

```
91 82 A1 69 02 A1 6D 02
```

### DEVICE => HOST

#### 81 A2 `in`

NOTE: The length of this message changes based on direction of rotation.

`94 82 A1 69 <MODULE> A1 76 98 <PRESS> <ROT_R> <ROT_M> <ROT_L> 00 00 ?? C0 C0 C0` 

BYTE 0: 0x94
BYTE 1: 0x82 encoded map follows
BYTE 2: 0xA1 string follows (1 byte)
BYTE 3: 0x69 'i'
BYTE 4: module index
BYTE 5: 0xA1 string follows (1 byte)
BYTE 6: 0x76 'v'
BYTE 7: 0x98
BYTE 8: 0x00 if no buttons pressed, 0x01 for button #1, 0x02 for button #2, ... (bitmask?)

```
# no buttons pressed on core
94 82 A1 69 00 A1 76 98 00 00 00 00 00 00 00 00 C0 C0 C0
# button (top) pressed on core
94 82 A1 69 00 A1 76 98 01 00 00 00 00 00 00 00 C0 C0 C0
# button (bottom) pressed on core
94 82 A1 69 00 A1 76 98 02 00 00 00 00 00 00 00 C0 C0 C0
# both buttons pressed on core
94 82 A1 69 00 A1 76 98 03 00 00 00 00 00 00 00 C0 C0 C0

# no rotation or press on dial module
94 82 A1 69 01 A1 76 98 00 00 00 00 00 00 00 00 C0 C0 C0

# left dial rotating right
94 82 A1 69 01 A1 76 98 00 00 00 01 00 00 00 00 C0 C0 C0
# left dial rotating left
94 82 A1 69 01 A1 76 98 00 00 00 CC FF 00 00 00 00 C0 C0 C0
# left dial being pressed
94 82 A1 69 01 A1 76 98 04 00 00 00 00 00 00 00 C0 C0 C0
# left dial rotating left while pressed
94 82 A1 69 01 A1 76 98 04 00 00 CC FF 00 00 00 00 C0 C0 C0

# middle dial rotate right
94 82 A1 69 01 A1 76 98 00 00 01 00 00 00 00 00 C0 C0 C0
# middle dial rotate left
94 82 A1 69 01 A1 76 98 00 00 CC FF 00 00 00 00 00 C0 C0 C0
# middle dial pressed
94 82 A1 69 01 A1 76 98 02 00 00 00 00 00 00 00 C0 C0 C0

# right dial rotate right
94 82 A1 69 01 A1 76 98 00 01 00 00 00 00 00 00 C0 C0 C0
# right dial rotate left
94 82 A1 69 01 A1 76 98 00 CC FF 00 00 00 00 00 00 C0 C0 C0
# right dial pressed
94 82 A1 69 01 A1 76 98 01 00 00 00 00 00 00 00 C0 C0 C0

# orbiter wheel stopped
94 82 A1 69 02 A1 76 98 00 00 00 00 00 00 00 00 C0 C0 C0
# orbiter wheel right
94 82 A1 69 02 A1 76 98 01 00 00 00 00 00 00 00 C0 C0 C0
# orbiter wheel right (faster?)
94 82 A1 69 02 A1 76 98 02 00 00 00 00 00 00 00 C0 C0 C0
# orbiter wheel left
94 82 A1 69 02 A1 76 98 CC FF 00 00 00 00 00 00 00 C0 C0 C0
# orbiter wheel left (faster?)
94 82 A1 69 02 A1 76 98 CC FE 00 00 00 00 00 00 00 C0 C0 C0
```

BYTE 8: 00 = none, 01 = top, 02 = bottom, 03 = both

#### 81 A6 `l_time`

Length: 3 bytes

Seen values: `CD 07 2C`

#### 81 A7 `in_noop`

Likely reminder of component values when value hasn't changed.

Should be the same as `in`

#### 82 A1 'l'

0x95 means has children? 0x97 means no children?

```
82 A1 'l'
	84 A1 'u' A5 '?-LED' A1 'i' 00 A1 't' 19 A1 'c' 95 C0 C0 C0
		84 A1 'u' A5 '?=hu5' A1 'i' 01 A1 't' 09 A1 'c' 95 C0 C0 C0
			84 A1 'u' A5 '?;>77' A1 'i' 02 A1 't' 18 A1 'c' 97 C0 C0 C0
		C0 C0 C0
	C0 C0 C0

81 A6 'l_time' CD 07 2C
```

#### 89 A6 uptime

BYTE 0: 0xCE

```
CE 01 15 3B 2E
AB 'charge_port' 01
AC 'version_core' A6 '2.0.17'
AD 'build_machine' AD 'linux ...
```

## === JSON payload details ===

### HOST => DEVICE

#### {"start":1}

Request the current layout and begin receiving input events.

#### {"stop":1}

Stop receiving input events.

#### {"hidmap":[]}

configure USB HID profile for device

"k" codes map to usb hid key values

Official reference on page 53:

https://www.usb.org/sites/default/files/documents/hut1_12v2.pdf

Modifier keys are better documented here:

https://gist.github.com/MightyPork/6da26e382a7ad91b5496ee55fdc73db2

and a converter implemented in python:

https://gist.github.com/willwade/30895e766273f606f821568dadebcc1c#file-keyboardhook-py-L42

the "m" codes come from Qt: https://doc.qt.io/qt-5/qt.html#Key-enum

i = index
c = control
	dial (0, 1, 2) (press, right, left)
	button 0 (press)
r = repeat / threshold probably
m = modifier, added together

bind dial press to left-shift (0x02) + "s"

```
{"hidmap":[{"i":2,"s":[{"c":0,"k":22,"m":2,"r":8,"rp":8}],"t":0}]]
```

bind dial right rotation to left-ctrl (0x01) + left-alt (0x04) + right arrow

```
{"i":2,"s":[{"c":1,"k":79,"m":5,"r":8,"rp":8}],"t":0},
```

bind dial left rotation to left-ctrl + left-alt + left arrow

```
{"i":2,"s":[{"c":2,"k":80,"m":5,"r":8,"rp":8}],"t":0},
```

#### {"boot":1}

Put the device into DFU bootloader mode.

#### {"screen\_ready":1}

Device will send `{"scr_ready":1}` in response.

Presumably this is only true if the screen is "ready".

#### {"send\_version":1}

Device will send the current core and screen versions:

`{"version_core":"1.3.1","version_screen":0}`

#### {"set\_version\_screen":<int>}

Sets the `version_screen` number to the specified integer.

Unknown effect. This is sent during image push by PaletteApp.

#### {"contrast":<int>}

Seems to cause the device to reset without dropping USB connection.

#### {"joymap":[]}

#### {"midimap":[]}

Configure component MIDI note mappings.

#### {"screen\_display":1}

Display the image with index 1 on the screen.

#### {"screen\_write":2}

Store image data on the device at index 2.

See [IMAGE.md](IMAGE.md) for more detail.

An image header follows in the next 48 bytes.

Then a 128x128 pixel image, then a footer.

#### {"led":[]}

Configure component LED colors.

#### {"flip":[{"i":2,"m":0]}

Used only for sliders. Should use `"m":0` when male connector is on top or left, otherwise `"m":1`

#### {"check":1}

Sent as a keepalive. Possible device reduces power when not received for some time.

### DEVICE => HOST

#### {"in":[{"i":7,"v":[0,0,0,0,0,0,0,0]}]}

Represents input, typically only sent on change.

i: component index
v: value

buttons:
	v[0] is press state
		0 is default, 1 is pressed

dials:
	v[0] is press state
	v[1] left turn velocity (>=1 when turning left, higher means faster)
	v[2] right turn velocity (>=1 when turning right, higher means faster)
	v[3] current absolute position value (0-255)

	Note: velocity is delta between current position previous position
	and velocity continues beyond absolute bounds.

sliders:
	v[0] current absolute value (0-254)

#### {"l":{}}

Tell host about current component layout.

Sent on any layout change and when receiving `{"start":1}`.

Uses same format as config with two exceptions.

- key `layout` becomes `l` in protocol
- uuids are prefixed with two spaces `[0x20,0x20]` in protocol

See [LAYOUT.md](LAYOUT.md) for more detail.

### OTHER SIGNIFICANT STRINGS

#### Likely commands

force\_reboot
reset\_reboot\_log
enable\_debug

rotate
timeout

#### Likely parameters

debug
error
info

#### Likely internal values

err\_id
setting\_flags\_1
debug\_return
reboot\_count
led\_array

reboot\_historical\_MCUSR
DEBUG\_ENABLE
SETTING\_FLAGS\_1
MCUSR\_SAVED

