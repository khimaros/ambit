# CONCEPTS

## component (ambit.Component)

The building blocks of a Palette device, connected by magnets.

Each component has a **kind**.

A component has many **input types**.

A component has one **behavior**.

Components are identifed by a **uid**.

## component uid

The unique identifier for a single Palette component.

These are assigned at manufacturing time and are of the form `  [a-z0-9]{3}`.

The leading space is not treated as significant by ambit.

Components of kind Base typically have a uid of the form `0000[0-9]`

## component input

When a user presses a button or turns a dial on a **component**.

Input can be categorized into one of several **input types**.

## component behavior (ambit.ComponentBehavior)

Defines how a **component** should behave when it receives input.

See also: [BEHAVIOR.md](BEHAVIOR.md)

## screen string

The string displayed on a Base **component**.

## screen image

The icon displayed on a Base **component**.

## action

The specific action that should be taken based on component **input**.

Examples: execute a command, switch profiles, simulate a key press

See also: [CONFIG.md#actionmap](CONFIG.md#actionmap) 

## input type

A **component** can support one or more input types.

Example input types: set, rotation\_right, rotation\_left, pressed, released.

## component kind

The specific type of a **component**, eg. Slider, Button, Dial, Base.

## layout (ambit.ComponentLayout)

A **component** arrangement where each component is attached to
a particular **port** in a specific **orientation** and **slot**.

See also: [LAYOUT.md](LAYOUT.md)

## layout query

A specially formed search string for choosing **components** in a **layout**.

See also: [QUERY.md](QUERY.md)

## rowwise

A way of referencing components by starting at the top left and counting
from left to right and top to bottom.

The numbers in the figure below correspond to the relative rowwise position:

```
      [1][2]
[3][4][5][6]
      [7][8][9]
```

## component orientation

The physical orientation of a **component** in a **layout**.

These are expressed in 90 degree increments.

See also: [TOPOLOGY.md](TOPOLOGY.md)

## component slot

The Cartesian coordinates of a **component** in a **layout**.

These are expressed as (x, y) vectors.

## component port

The magnetic attachment points on a **component**.

Each component has a single male ports and three female ports.

See also: [LAYOUT.md](LAYOUT.md)

## component invocation (ambit.ComponentInvocation)

Binds a **callback** to a **component**. Also used to store
**persistent state** related to callback invocation.

## controller (ambit.Controller)

A single USB connected Palette device.

A controller contains a **config** and a **layout** consisting of one or more **components**.

The config may be empty.

## controller config (ambit.Configuration)

Each **controller** has a config, which determines how each **component**
should respond to **input**.

See also: [CONFIG.md](CONFIG.md)

## simulator (ambit.simulator.Controller)

A special type of **controller** which uses a fake, in-memory device instead of
a physical USB connected device. Users interact with these using
their keyboard and a graphical interface.

