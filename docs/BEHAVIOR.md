# BEHAVIOR

## Parameters

behavior: one of CYCLE, ACCUMULATE, TRIGGER, DELTA
threshold (default: 1): number of inputs before triggering callback
timeout (default: 1.5): seconds before triggering delayed behavior
default: value to initialize component state with
items (default: []): items to cycle through for CYCLE behavior
limits (default: None): tuple of (min, max) values for a component
invert (default: False): negate change from component inputs
discrete (default: True): increment as whole integers (rather than float)
loop (default: False): loop back to start when limits are reached
nested (default: False): send a tuple of (item index, value) to callbacks, else just scalar value
value: override raw input value

Defaults are overridden in the following order:

 1. common defaults
 1. kind defaults
 1. input type defaults
 1. action defaults

### common defaults

threshold=1
timeout=1.5
items=[]
limits=None
invert=False
discrete=True
loop=False
nested=False

### kind defaults

Slider:
	behavior=TRIGGER
	limits=(0, 255)

### input type defaults

```
pressed:
	behavior=TRIGGER

released:
	behavior=TRIGGER

rotation_left:
	behavior=ACCUMULATE
	invert=True

rotation_right:
	behavior=ACCUMULATE
	invert=False

set:
	behavior=TRIGGER
	limits=(0, 255)
```

### action defaults

```
setColor{Red,Green,Blue}:
	limits=(0,255)
	default=255
	threshold=8

cycleMapping:
	behavior=CYCLE
	loop=True
	nested=True

{next,previous}Function:
	behavior=TRIGGER

profileSwitch:
	behavior=CYCLE
	loop=True

executeCommand:
	None

testCycle:
	behavior=CYCLE
	loop=True
	nested=True

testDelta:
	behavior=DELTA

testAccumulate:
	behavior=ACCUMULATE

testTrigger:
	behavior=TRIGGER
```

## Examples

These may not reflect current best practices.

See [../ambit/resources/configs/](../ambit/resources/configs/) instead.

### TRIGGER

callback args: (raw value or "value")

trigger on button press

```
"pressed": { "action": "executeCommand", "argv": [] }
```

trigger after five button presses

```
"pressed": { "action": "executeCommand", "argv": [], "threshold": 5 }
```

trigger every 20 degrees of relative rotation (unlimited)

```
"rotation_right": { "action": "executeCommand", "behavior": "trigger", "argv": [], "threshold": 20 }
```

trigger every 20 degrees of absolute movement

```
"set": { "action": "executeCommand", "argv": [], "threshold": 20 }
"set": { "action": "setColorRed", "threshold": 20 }
```

trigger with a specific value

```
"released": { "action": "setColorRed", "value": 255 }
```

value (default: raw value): set stored value to this number

### ACCUMULATE

invert (default: False): accumulate negative value
limits (default: None): a tuple of (min, max) for lower/upper bound of accumulation
callback args: (current stored value)

increase on rotation right, decrease on rotation left

```
"rotation_left": { "action": "setColorRed", "behavior": "accumulate", "limits": (0, 255), "invert": true },
"rotation_right": { "action": "setColorRed", "behavior": "accumulate", "limits": (0, 255) }
```

same as above, but simpler

```
"rotation": { "action": "setColorRed", "behavior": "accumulate" },
```

increase when button is pressed (default delta is raw value 1)

```
"pressed": { "action": "setColorRed", "behavior": "accumulate" }
```

increase by 8 when button is released (need to override raw value 0)

```
"released": { "action": "setColorRed", "behavior": "accumulate", "value": 8 }
```

decrease by 1 on button press

```
"pressed": { "action": "setColorRed", "behavior": "accumulate", "invert": true }
```

### DELTA

send negative delta when turned left, positive when turned right

```
"rotation_left": { "action": "adjustTemperature", "behavior": "delta", "invert": true }
"rotation_right": { "action": "adjustTemperature", "behavior": delta" }
```

same as above

```
"rotation": { "action": "adjustTemperature", "behavior": "delta" }
```

send negative delta 5 when pressed

"pressed": { "action": "adjustTemperature", "behavior": "delta", "invert": true, "value": 5 }

### CYCLE

send the next item when pressed

```
"pressed": { "action": "selectProfile", "behavior": "cycle" }
```

send previous item when pressed

```
"pressed": { "action": "selectProfile", "behavior": "cycle", "invert": true }
```

send next item when rotated 15 degrees, loop to start/end

```
"rotation": { "action": "setActionMap", "behavior": "cycle", "items": [
	         { "set": <one> },
                 { "set": <two> }],
              "target": "4{=", "loop": true, "threshold": 15 }
```

