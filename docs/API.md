# API

Typical usage of the ambit module overview:

 * Create a `Configuration`
 * Create and initialize a `Controller`
 * [Optional] Attach a `Display`

## Create a Configuration

The simplest way to create a Configuration is to use the
`StandardConfiguration` helper. This will parse standard
ambit command line flags and return a `Configuration`
instance with all paths preloaded.

```
import ambit

config = ambit.StandardConfiguration()
```

For more control over the Configuration, you use the
`Configuration` class directly.

```
import ambit

config = ambit.Configuration(paths=['./first.plp', './second.plp'])

conf.profile.icon = ambit.Configuration.ICON_HOME
```

## Create a Controller

Now that we have a Configuration, we can create a Controller.

```
import ambit

config = ambit.StandardConfiguration()

ctrl = ambit.Controller(config)
ctrl.open()
ctrl.connect()
ctrl.communicate()
ctrl.close()
```

This will create the Controller, initialize the Palette device,
enter an event loop and clean up when interrupted.

# Attach a Display

A Display is a graphical view of the Palette, which
continuously shows the current state your device.

When the Display is closed, the Controller will also be closed.

```
config = ambit.StandardConfiguration()

ctrl = ambit.Controller(config)
ctrl.open()
ctrl.connect()

display = ambit.render.Display(ctrl, shutdown_event=ctrl.shutdown_event)
display.run()

ctrl.communicate()
ctrl.close()
```
