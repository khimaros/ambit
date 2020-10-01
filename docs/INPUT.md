# INPUTS

## set

kind: Dial, Slider

The control was moved to an absolute position.

## pressed

kind: Button, Dial

The control was pressed.

## released

kind: Button, Dial

The control was released.

## long\_pressed

kind: Button, Dial

The control was held in the pressed position for N seconds.

## long\_released

kind: Button, Dial

The control was held in the pressed position for N seconds and then released.

## rotation

kind: Dial

The control was rotated. Behavior will be influenced by the direction of rotation.

Anti-clockwise rotation will default to behavior `invert: true`.

## rotation\_right

kind: Dial

The control was rotated in a clockwise direction.

## rotation\_left

kind: Dial

The control was rotated in an anti-clockwise direction.

## pressed\_rotation

kind: Dial

Identical to **rotation** but while being pressed.

## pressed\_rotation\_right

kind: Dial

The control was rotated in a clockwise direction while being pressed.

## pressed\_rotation\_left

kind: Dial

The control was rotated in an anti-clockwise direction while being pressed.
