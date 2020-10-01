# ROADMAP

```
[x] Ctrl+C should exit cleanly and close the device
[x] switching profiles via button press
[x] configuration loading
[x] infinite adjustment for led callbacks
[x] custom logos for screen display
[x] rename to something != Palette
[x] documentation for running as non-root user
[x] prepare python packaging
[x] clearer ontology for callback types (eg. "relative" vs. "absolute")
[x] config common action behaviors (toggle, cycle, absolute, relative)
[x] enable multi-threading to avoid read/write conflicts
[x] queue screen and led updates to avoid overloading, drop old updates when we're too far behind
[x] MIDI map hash consistently with component uid across restarts/disconnect
[x] some sort of visual layout topology rendering
[x] display current component state in graphical view
[x] add simulator for doing development without physical device
[x] create a FakeDevice to make testing possible
[x] full layout rotation
[x] enable user input from keyboard/mouse on rendered view
[x] spatial configuration ("button on right is pressed")
[x] increase test coverage to 80%
[x] interactive console for experimentation with live devices
[x] script to reboot Palette into bootloader
[-] full coverage of upstream mediaMap bindings
[-] support upstream keyMap bindings
[-] document configuration options
[-] increase type annotations to 15%
[ ] resolve queries at config load to preserve actionMap on orienation change
[ ] plugin system for component callback behavior
[ ] support long_pressed input type for buttons and dials
[ ] support pressed_rotation_{right,left} input type for dials
[ ] when config uses `rotation`, map to `rotation_left` and `rotation_right`
[ ] long running mode for midi map for layout/profile changes
[ ] add blocking/nonblocking mode to all major write operations
[ ] shared peristent state across components (eg. two buttons change same value)
[ ] move callbacks to subclass or equiv
[ ] code hygiene: make more use of private attributes on classes
[ ] increase test coverage to 90%
[ ] switch to an interrupt/callback driven system for rendering (performance)
[ ] graphical configuration interface
[ ] support for MIDI output profile (eg. control LEDs)
[ ] switch to subpackages and `extras_require` for render/simulator and dev deps
[ ] CLI based simulator, or just stick with tests?
```
