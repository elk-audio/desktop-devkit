# Elk Stomp dev kit: a tutorial

## Part 1: example 0 (`examples/ex0/`)

In this first part, we'll walk through the code for a single fx pedal product.
You'll learn:

- What Sushi is;
- How it's configured;
- How the "glue" app works;
- How you can map hardware controllers to audio parameters.

Open `examples/ex0/sushi_config.json`:

```JSON
// examples/ex0/sushi_config.json
{
  "host_config": {
    "samplerate": 48000
  },
  "tracks": [
    {
      "name": "TRACK",
      "channels": 2,
      "inputs": [
        {
          "engine_channel": 0,
          "track_channel": 0
        }
      ],
      "outputs": [
        {
          "engine_bus": 0,
          "track_bus": 0
        }
      ],
      "plugins": [
        {
          "uid": "sushi.testing.gain",
          "name": "gain",
          "type": "internal"
        }
      ]
    }
  ]
}
```

As mentioned earlier, Sushi is the host for your plugin. The preferred way to configure it - and the one you should explore first - is via a **JSON** file, like `sushi_config.json`.

The first object (`host_config`) sets up basic parameters like `samplerate` but also a bunch of other things that are not directly relevant for the purpose of this tutorial. 

> Please refer to [Sushi documentation](https://elk-audio.github.io/elk-docs/html/sushi/sushi_configuration_format.html) if you want to know more.

Then comes `tracks`, a list of objects, each declaring an audio track and its audio connections and plugin stack.

In this simple product, we only need one track. We call it "TRACK" and make it a stereo track with `channels: 2` (fyi, you can have up to 16 channels in a track).

Audio connections are declared in 2 different objects: `inputs` and `outputs`, both are lists of connections. In principle, audio connections map **one engine channel** (engine channels = the ones exposed by coreaudio or pulseaudio) to **one track channel**.

For instance, look at `inputs`: we have one single connection between engine channel 0 and track channel 0. That means that the first channel of the coreaudio device feeds the first channel of the newly created TRACK.

Note that:

- By default, Sushi will use your OS default audio device. You can specify another as a CLI argument to Sushi (more on that later);
- We have not connected anything to TRACK's 2nd channel! That's fine, this is a guitar pedal after all: we only need 1 input, right? In general, there are very few constraints on audio connections: you can declare as many or as few as you want, as long as you connect channels that actually exist...
- `outputs` use "busses" instead of channels like `inputs` do. Busses are nothing more than a convenience abstraction to handle pairs of adjacent channels. i.e. "track_bus 0" is short-hand for "track_channel 0 and 1". We could have declared the output connection as 2 separate channel connections as in:

```JSON
"outputs": [
  {
    engine_channel: 0,
    track_channel: 0
  },
  {
    engine_channel: 1,
    track_channel: 1
  }
]
```

Both methods are strictly equivalent.

Finally, we declare plugins to be hosted on our TRACK.

Depending on the plugin type (vst2, vst3, lv2 or internal), the declaration changes a bit but all plugins must be given:

- a **name**: a required unique string that will be the main identifier for that plugin;
- a **type**: "internal", "vst2x", "vst3x" or "lv2";
- then for internal plugins:
  - a **uid**
- for VST3 and VST2:
  - **uid**: the name of the plugin as set in its source code;
  - **path**: the absolute path to the `.vst3` bundle or a relative path to it (relative to Sushi's base plugin path)
- for LV2:
  - **uri**: an LV2 http-like identifier. LV2 does not allow you to directly point to an executable.

Let's try and run this on a Mac.

```shell
bin/macos/sushi --coreaudio -c examples/ex0/sushi_config.json
```

> The `--coreaudio` option specifies the audio front-end to use; `-c` lets you pass a path to the config file.

Now you should have Sushi running!
But before we move on, let's introduce 2 more useful things:

- **logs**: Sushi writes logs to `/tmp/sushi.log`. By default, it only writes the file at shutdown, but you can force it to write more often - let's say every second - with `--log-flush-interval=1`
- in `modules/sushi-gui/` you will find a neat Qt app that acts as a **GUI** for Sushi. Granted you have `uv` installed, simply running `uv run sushi-gui.py` will display it. In development, we realized that this tools was quite invaluable to fine-tune plugin parameters but it also serves quite well as a dynamic monitor for Sushi.

## Part 2.1: Extending the simple product: `examples/ex1/`

Starting from the product showed in part 1, we turn to extending its functionality. Indeed, the current app is quite poorly endowed: a single gain stage plugin, i.e. an extremely over-engineered volume control.

We will:

- add more plugins to the main audio track;
- add a second track with a reverb to which we will send some of the main signal to;
- add hardware controllers to control reverb parameters (aka "Introducing the glue app and Guru");
- extend the glue app with a system to manage presets and build 2 presets (a long lush reverb and a shorter roomy one). We'll also need to map a switch to toggle between presets;
- create a "combo" controller: a single slider to control multiple parameters

#### Sushi

First let's add to Sushi config:

```JSON
// examples/ex1/sushi_config.json
{
  "host_config": {
    "samplerate": 48000,
    "playing_mode": "playing"
  },
  "tracks": [
    {
      "name": "TRACK",
      "channels": 1,
      "inputs": [],
      "outputs": [
        {
          "engine_channel": 0,
          "track_channel": 0
        },
        {
          "engine_channel": 1,
          "track_channel": 0
        }
      ],
      "plugins": [
        {
          "uid": "sushi.testing.wav_streamer",
          "name": "Wave streamer",
          "type": "internal"
        },
        {
          "uri": "http://guitarix.sourceforge.net/plugins/gx_sd2lead_#_sd2lead_",
          "name": "SD2",
          "type": "lv2"
        }
      ]
    }
  ],
  "initial_state": [
    {
      "processor": "Wave streamer",
      "parameters": {
        "volume": 1.0,
        "loop": 1.0,
        "playing": 1.0
      },
      "properties": {
        "file": "wavfiles/elG_08.wav"
      }
    },
    {
      "processor": "SD2",
      "parameters": {
        "DRIVE": 0.8,
        "TONE": 0.8,
        "LEVEL": 0.8
      }
    }
  ]
}
```

**Note the following**:

- We changed the nr of channels to 1 for TRACK, making it a mono track;
- Accordingly, we changed the audio connections:
  - no inputs at all. Indeed we don't need them: our first plugin will be a wave file streamer;
  - outputs: the single track channel is connected to the 2 first engine channels, effectively patching our mono track to a stereo bus;

Furthermore, the plugin stack has changed: we put a wave streamer and a Boss SD2-like distortion.

We also introduce a new top-level object: `initial_state` which lets us declare a startup state for each processor. Specifically, note that plugins are indeed identified by the name we gave them in the `plugins` object and that parameter names MUST match their name as defined in their source code (hence the inconsistent capitalizing...). Also, remember that `initial_state` is optional. All plugins will initialize without it, albeit to a state that only their devs can be called responsible for.

Running this config with
```shell
bin/macos/sushi --coreaudio -c examples/ex1/sushi_config.json
```
will start playing the `elG_08.wav` file through a distortion:

- automatic playing is thanks to the `playing` parameter of `wav_streamer` (notice `loop` as well ;-)
- the file path is passed *not* via a parameter but via a `properties`;

#### A first glue app

At this point, we have audio but still no way to interact with it. Earlier we made a mention of the provided `sushi-gui`. We could certainly run it and use it to make parameter changes but that is never going to cut it for a real-life product. What we need is for Sushi to respond to Sensei events.

> Recall that Sensei is a sub/pub type of server that pushes events to subscribing processes whenever a hardware controller is interacted with. In the current desktop-first context, Sensei is in effect *mocked* by a Qt GUI app provided in `modules/board-gui/`

> As a side note, those with experience with gRPC and API development tools like Postman may want to run the provided `sensei_rpc.proto` found in `modules/board-gui/sensei-grpc-api/` as a monitoring tool for events emitted by Sensei.

Let's first get something out of the way and start `board-gui`: `uv run modules/board-gui/main.py`. You should see a GUI pop up with the same controllers as on the hw board. Interacting with it produces the exact same events as a "real" Sensei would on the actual hardware.

Now we need to turn these events into Sushi actions. That's where a Guru app comes in. So let's look at it:

```python
# examples/ex1/glue.py

import asyncio
import logging

from guru.app import GlueApp
from param_mappings import MAPPINGS


async def main():
    app = GlueApp(mappings=MAPPINGS, log_level=logging.INFO)
    await app.initialize()

    return await app.run()


if __name__ == "__main__":
    asyncio.run(main())

```

Important things to notice:

- Guru is built with `asyncio` (Sorry...);
- It's small. Indeed most comes with `GlueApp` and its `initialize` method.
- the meat of the app lies in the `MAPPINGS` object that we pass to `GlueApp`. So let's check it out:

```python
from guru.mappings import PluginParameterMapping, BypassMapping


MAPPINGS = [[
    # Example: Map a pot to a plugin parameter
    PluginParameterMapping(
        track_name="TRACK",
        plugin_name="SD2",
        parameter_name="DRIVE",
        controller_name="POT1",
        preprocessor=lambda x: x, 
    ),
    PluginParameterMapping(
        track_name="TRACK",
        plugin_name="SD2",
        parameter_name="TONE",
        controller_name="POT2",
        preprocessor=lambda x: x,
    ),
    PluginParameterMapping(
        track_name="TRACK",
        plugin_name="SD2",
        parameter_name="LEVEL",
        controller_name="POT3",
        preprocessor=lambda x: x,
    ),
    BypassMapping(plugin_name="SD2", controller_name="SW1"),
]]
```

It turns out `MAPPINGS` is a **list of lists** of Guru objects. (

> The reason behind it being a list of lists is irrelevant for this tutorial.

`PluginParameterMapping` and `BypassMapping` should be self-explanatory but let's point out a couple of details:

- controller names come from Sensei itself. You can get those with an api endpoint called `GetControllerMap` but its easier to just read the Sensei config file included in `modules/board-gui/sensei_config.json`;
- `preprocessor` is the preferred way to apply transformations to the raw value before forwarding it to its plugin target. It must be a lambda but is entirely optional. As a matter of fact, those preprocessors shown here are completely useless and we included them for illustrative purposes only. We could as well have omitted the line entirely. In more advanced examples, we demonstrated how to use them to clamp, interpolate or otherwise change the raw input into a more suitable one for our application.

`PluginParameterMapping` maps a `controller_name` to a `parameter_name` of a `plugin_name` plugin.

`BypassMapping` assigns `plugin_name` bypass state to `controller_name`.

Guru offers more mapping classes. We'll get to them as our product exercise grows. But now that we have an app that actually
produces sound, let's run it.

---


## Part 2.2: Auxiliary tracks

Adding a reverb plugin to our pedal can be done in 2 main ways. The simpler way is to simply append it to the plugin list for our TRACK, provided the plugin we select exposes some "mix" or "dry/wet" parameter of course.

The other way is too put it on an auxiliary track and send some of our signal to it before mixing in back on the output bus. Let's do that.

The way Sushi implements aux tracks is as follows:

- aux tracks are normal tracks with no input connections;
- feeding an aux track happens through the use of a pair of internal plugins: `sushi.testing.send` and `sushi.testing.return`;
- `send` goes on the "sending" track;
- `return` goes on the "receiving" track as its very first plugin;
- connecting a `send` instance to a `return` is done via a `property` of the `send`.

In the config file for Sushi it looks like this:

```JSON
// examples/ex2/sushi_config.json

 "tracks": [
    {
      "name": "TRACK",
      "channels": 1,
      "inputs": [],
      "outputs": [
        {
          "engine_channel": 0,
          "track_channel": 0
        },
        {
          "engine_channel": 1,
          "track_channel": 0
        }
      ],
      "plugins": [
        {
          "uid": "sushi.testing.wav_streamer",
          "name": "Wave streamer",
          "type": "internal"
        },
        {
          "uri": "http://guitarix.sourceforge.net/plugins/gx_sd2lead_#_sd2lead_",
          "name": "SD2",
          "type": "lv2"
        },
        {
          "uid": "sushi.testing.send",
          "name": "Send_rev",
          "type": "internal"
        }
      ]
    },
    {
      "name": "AUX",
      "channels": 2,
      "inputs": [],
      "outputs": [
        {
          "engine_channel": 0,
          "track_channel": 0
        },
        {
          "engine_channel": 1,
          "track_channel": 1
        }
      ],
      "plugins": [
        {
          "uid": "sushi.testing.return",
          "name": "Return_rev",
          "type": "internal"
        },
        {
          "uid": "sushi.testing.freeverb",
          "name": "Reverb",
          "type": "internal"
        }
      ]
    }
  ],
...
```

- we added a second track called "AUX" with no inputs;
- we added a `sushi.testing.send` at the bottom of TRACK's plugin list;
- we added a `sushi.testing.return` at the top of AUX's plugin list;
- right after the `return`, AUX also gets our builtin reverb plugin (`sushi.testing.freeverb`)

Then we connect our `send` to our `return` in the `initial_state` object:

```JSON
// examples/ex2/sushi_config.json
...
    {
      "processor": "Send_rev",
      "properties": {
        "destination_name": "Return_rev"
      }
    }
```

And we do not forget to add 2 ui mappings:

```python
# examples/ex2/param_mappings.py
    
    PluginParameterMapping(
        track_name="TRACK",
        plugin_name="Send_rev",
        parameter_name="gain",
        controller_name="POT6",
    ),
    PluginParameterMapping(
        track_name="AUX",
        plugin_name="Reverb",
        parameter_name="room_size",
        controller_name="POT7",
    ),
```

Feel free to run and play around with this example: `uv run bin/run-example.sh examples/ex2`

---
## Part 2.3: Control mappings and Presets (ex3)

Our 3rd example introduces Guru's Preset system and the `Control` mapping class.

#### Presets

Guru presets are a convenient way to store and load specific parameter values.
Let's look at `examples/ex3/sushi_presets.py`:

```python
from guru.presets import Preset


preset_01 = Preset(
    "Short",
    initial_state=[
        {
            "processor": "Reverb",
            "parameters": {"dry": 0.0, "wet": 0.2, "room_size": 0.1, "width": 0.25, "damp": 0.9},
        },
    ],
)
...
```

Presets take a `name` (str) and an `initial_state`, which is the same kind as in Sushi configuration files: a list of dicts with parameter values for plugins.
Presets can hold any number of parameter/property values for any number of plugins (aka processors) but in the case
of ex3, we only use them for the reverb plugin, as short/medium/long presets.

Note that presets must be imported and initialized. Look at `ex3/glue.py`:

```python
...
    pm = PresetManager()
    from sushi_presets import preset_01, preset_02, preset_03

    pm.add_preset(preset_01)
    pm.add_preset(preset_02)
    pm.add_preset(preset_03)
    await pm.initialize_presets()
    await pm.load_preset(0)
...
```

See how after creating a `PresetManager`, we:

- imported the presets from `sushi_presets.py`;
- added each of them with `add_preset()`;
- initialized them with `initialize_presets()`;
- and finally loaded the first one with `load_preset(0)`

#### Control mappings
`Control` mappings are in a sense the most generic type of mapping that Guru offers.
Indeed, they allow you to trigger any function/method from a UI element.

Let's open `ex3/param_mappings.py`. At the very bottom we find:

```python
    Control(controller_name="SW2", cb=partial(observer.emit, "LoadNextPreset")),
```

A `Control` mapping takes a `controller_name` and a callback `cb`. The callback mechanism is comparable to other mappings preprocessors.
Here, we use the `partial` method from `functools` but we could also have passed a `lambda`.

In this case, we simply emit a "LoadNextPreset" signal that PresetManager subscribes to by default.

