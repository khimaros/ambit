# QUERY

## Overview

Queries are enclosed in `[ ]` and consist of a **pattern**
with optional **filters**. If a query is not enclosed in `[ ]`,
it is assumed to be a component uid.

The overall syntax is:

```
[pattern | filters...]
```

a pattern is a space separated list of **matchers**. these matchers
consist of **parts** which are key=value pairs. they may not contain spaces.

here is a matcher with two parts:

`kind=Slider orientation=90`

parts are always interpreted as AND during matching

available keys:

 * kind
 * index
 * uid
 * orientation
 * slot

filters can be repeated and are chained using `|`

available filters

 * rowwise
 * select(n)

Here's a concrete example:

```
[kind=Slider orientation=90 | rowwise | select(1)]
```

This matches the rowwise first component which is both
of kind Slider AND at a 90 degree orientation.

## Examples

Match any component in slot (1,1):

```
[slot=(1,1)]
```

Match the rowwise first Dial component:

```
[kind=Dial | rowwise | select(1)]
```

Match the rowwise second Button component:

```
[kind=Button | rowwise | select(2)]
```

Match component at index 3:

```
[index=3]
```
