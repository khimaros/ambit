# LAYOUT

Component layout can be represented as a DAG (directed acyclic graph)

Each component has one male and three female connectors.

The male connectors lead to the root node.

female connectors are ordered clockwise starting from the male connector

For square components, including the base:

```
   F0
M0[  ]F1
   F2
```

For the base, M0 represents the microusb input to the computer.

For rectangular components (sliders):

```
   F0
M0[  ]F1
F4[  ]F2
   F3
```

Female connectors which are empty are represented with `null`
in JSON layout messages.

If another component is connected to F2, you'd have:

```
"c":[null,null,{"u":...}]
```

## attributes

"u" is the uuid, config differs from what's sent by device
"i" is the index
"t" is type of component
"c" is connections (female/children)

## uuid

in the layout commands from device, uuid is prefixed with two spaces (0x20)

the prefix spaces are not present in the config

base always has `{"u":"00000","i":1}`

## type

0 = base
1 = button
2 = dial
3 = slider


## indexes

start with base i=1, increment for each connection, breadth first

```
     F0        F0        F0
  M0[I1]F1::M0[I2]F1::M0[I4]F1
     F2        F2        F2
     ::
     M0
  F2[I3]F0
     F1
```
