# TOPOLOGY

Integer represents index, three digit alphanumeric is UID.

`> < v ^` represent the male connectors, pointing outward.

`: ...` represent female connectors.

Given the layout below, these indices should be stable on initial USB connection.

If pieces are moved after initialization, and they have children, the component and its children will be reindexed.

```
 _..._ _..._ _.^._ _..._ _..._
|     |  7  |  1  |  4  |     |
:     > 4lf : 000 : 4ls :     :
|  8  |_.v__|_.^._|_.v._|  5  |
| 4}= |  6  |  2  |  3  | 4}m |
:     : 4A0 > 49d < 4FH <     :
|_..._|_..._|_..._|_..._|_..._|

```

Layout will represent components in slots.

Base will always be at slot (0,0)

Square components take up 1 slot.

Wide components take up 2 slots.

## Slot cardinality

center is (0,0)
up/right is positive
down/left is negative

```
      (+)
       |
(-) ---|--- (+)
       |
      (-)
```

## Port positions

The slot which a port borders, assuming
the component is at position (0,0).

### Orientation 0

```
        (0,1)

        _.^._
       |     |
(-1,0) :     : (1,0)
       |_..._|

       (0,-1)
```

### Orientation 90

```
        (0,1)

        _..._
       |     |
(-1,0) :     > (1,0)
       |_..._|

       (0,-1)
```

### Orientation 0 (wide)

```
         (0,1)    (1,1)
            \     /
           _.^.__..._
          |          |
(0,-1) -- :          : -- (2,0)
          |_...__..._|
            /      \
         (0,-1)  (1,-1)
```

### Orientation 90 (wide)

```
               (0,1)
               / 
            _..._
           |     |
 (-1,0) -- :     > -- (1,0)
           |     |
           |     |
(-1,-1) -- :     : -- (1,-1)
           |_..._|
              \
             (0,-2)

```

wide components male ports share the same ordinal directions
as a square component. 0, 90, 180, 270.

however, depending on their orientation, their extra slot
extends in one direction or another.

The female positions also have one of four possible orientations.

M port position is identical for wide/narrow

Female ports map as follows:

W0 = (W2 w/ inverted Y axis)
W1 = (slot) + (2,0)
W2 =
W3 = N1
W4 = N2

orientation  0 == -(orientation 180)
orientation 90 == -(orientation 270)

Only female ports 0, 1, 2 differ.

## Wide orientation

Assuming component is at position (0,0)

  0 degrees: male ( 0, 1), female ( 1, 1), ( 2, 0), ( 1,-1), ( 0,-1), (-1, 0)
180 degrees: male ( 0,-1), female (-1,-1), (-2, 0), (-1, 1), ( 0, 1), ( 1, 0)

 90 degrees: male ( 1, 0), female ( 1,-1), ( 0,-2), (-1,-1), (-1, 0), ( 0, 1)
270 degrees: male (-1, 0), female (-1, 1), ( 0, 2), ( 1, 1), ( 1, 0), ( 0,-1)

## Narrow orientation

Assuming component is at position (0,0)

  0 degrees: male ( 0, 1), female ( 1, 0), ( 0,-1), (-1, 0)
180 degrees: male ( 0,-1), female (-1, 0), ( 0, 1), ( 1, 0)

 90 degrees: male ( 1, 0), female ( 0,-1), (-1, 0), ( 0, 1)
270 degrees: male (-1, 0), female ( 0, 1), ( 1, 0), ( 0,-1)

