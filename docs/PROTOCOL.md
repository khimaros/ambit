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

