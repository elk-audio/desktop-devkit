# AGENTS.md

Read the README.md file for additional info before proceeding.

## Primary Purpose

The main tasks in this repo are:
1. **Building audio plugins** — for desktop (macOS/Windows) or for the Elk Stomp board (cross-compiled via the Elk Audio OS SDK)
2. **Running examples** — on desktop (using the mock hardware GUI) or on the board over SSH

### Plugin build workflow

When asked to build a plugin, always ask the user:
1. The path to the plugin source directory
2. Whether to build for **desktop** or **the board** (board build requires the Elk Audio OS SDK — ask the user where they unpacked the SDK zip file elk-builder-stomp-$VER.zip and read the AGENTS.md file there)

After building, walk the user through:
1. **Creating an example** — copy the closest existing example (`cp -r examples/ex1/ examples/my-example/`), update `glue.py`, `param_mappings.py`, `sushi_config.json`, and `sushi_config_stomp.json` for the new plugin
2. **Running the example** — always run the example yourself and debug any issues rather than leaving it to the user. Run it for **15 seconds only**, say explicitly that you are doing so, then kill it (`killall sushi python3`). Check `/tmp/sushi.log` for errors.
3. **Connecting Sushi GUI** — once the example is running, walk the user through launching the Sushi GUI from `modules/sushi-gui/` to visualise and interact with the running audio engine

### Running examples — rules
- Always run `bin/run-example.sh` yourself after setting up an example; do not leave it to the user
- Start the example in the background (`nohup bin/run-example.sh examples/foo/ >> /tmp/run-example-out.txt 2>&1 &`), wait a few seconds for Sushi to initialise, then kill it (`kill -INT $(pgrep sushi)`) and read the **flushed** `/tmp/sushi.log` — the log only flushes to disk on clean exit, not while Sushi is running
- If the log contains no `[error]` or `[critical]` lines, the test is good
- Always check `/tmp/sushi.log` to diagnose Sushi errors (plugin load failures, parameter name mismatches, etc.)
- After confirming the example works, print the exact commands the user can run manually to start it themselves
- After a successful board run, always tell the user the exact SSH commands they can run manually to re-run the example without Claude

**Killing the example — SIGINT only, never SIGTERM:**
`run-example.sh` traps `INT` (not `TERM`) to run its cleanup and call `kill 0` on all children. Sending SIGTERM bypasses the trap and leaves things in a bad state that requires a board reboot. Always kill via:
```bash
ssh mind@<board-ip> "kill -INT \$(pgrep -f run-example.sh)"
```
Never use bare `killall sushi python3 sensei` (sends SIGTERM).

**Board example audio source — always use wav_streamer:**
In `sushi_config_stomp.json`, always use the internal `sushi.testing.wav_streamer` plugin as the audio source. Never wire up live board hardware inputs. Use a file from `wavfiles/` (e.g. `wavfiles/elG_08.wav`). This mirrors the desktop config and makes board testing self-contained.

## Project Overview

Elk STOMP DevKit is a desktop development environment for building audio pedal applications targeting the Elk STOMP hardware (STM32MP1 SoC running Elk Audio OS). It lets developers prototype on Mac/Windows by mocking the hardware controllers, then deploy to the board with minimal changes.

## Key Commands

```bash
# Install dependencies (uses uv — Python 3.12.8)
uv sync

# Run an example (launches all three components at once)
bin/run-example.sh examples/ex1/

# macOS: fix quarantine flags on binaries and plugins (required first run)
sudo xattr -rc .

# Run tests (Guru module)
uv run --extra dev pytest
uv run --extra dev pytest tests/test_sensei_client.py
```

**Running components individually** (in separate terminals):
```bash
uv run modules/board-gui/main.py          # Mock hardware controller GUI (gRPC server on :50051)
bin/macos/sushi --coreaudio -c examples/ex1/sushi_config.json   # Audio engine
uv run examples/ex1/glue.py              # Application logic (glue app)
```

Windows uses `bin/win/sushi.exe --portaudio` instead of `--coreaudio`.

## Architecture

The system has three processes communicating over gRPC:

```
Mock Sensei (board-gui)  ──gRPC:50051──►  Glue App (Python)  ──gRPC:51051──►  Sushi (audio engine)
     Qt6 GUI                                   Guru library                     VST/LV2 plugin host
 emulates hardware                          event-driven bridge                  actual DSP
```

### Guru Library (`modules/guru/`)

The central library users build their glue apps against. Key components:

- **`GlueApp` (`app.py`)** — top-level orchestrator; subclass this to build an application
- **`observer.py`** — async pub/sub event bus (no external broker); the foundation for all internal messaging
- **`SenseiClient`** — connects to hardware/mock Sensei via gRPC, publishes hardware events
- **`SushiClient`** — controls Sushi via `elkpy` (parameter set/get, transport, etc.)
- **`MappingManager` / `mappings.py`** — declarative controller→audio parameter bindings with optional preprocessors
- **`PresetManager`** — named effect configurations that can be switched at runtime
- **`DisplayManager`** — OLED/mock display output

Guru uses `grpc.aio` (async gRPC). All managers are async. The observer pattern is the main extensibility point — subscribe to event types to react to hardware changes.

### Example Structure

Each example in `examples/exN/` has:
- `sushi_config.json` — audio routing, plugin chain for desktop
- `sushi_config_stomp.json` — same config adapted for hardware board
- `glue.py` — `GlueApp` subclass with app logic
- `param_mappings.py` — `MappingManager` configuration

The examples are a learning progression: ex0 (minimal), ex1 (mappings), ex2 (aux send/return), ex3 (presets + mode switching).

### Sushi Config Format

Sushi (`bin/macos/sushi` or `bin/win/sushi`) is a prebuilt headless DAW binary. Its JSON config defines tracks, plugins, audio routing, and MIDI. Plugins live in `plugins/` (pre-built LV2 and VST2/3 for Mac/Windows/ARM). The config must list plugin paths as absolute or relative to the working directory.

### Submodules

`modules/guru`, `modules/board-gui`, and `modules/sushi-gui` are git submodules. After cloning, run `git submodule update --init --recursive`. Each has its own `pyproject.toml`; the root `pyproject.toml` pulls them in as workspace members. `modules/board-gui/` has a CLAUDE.md with threading and gRPC details specific to that module.

### Hardware vs Desktop

The only change between desktop and hardware deployment is:
1. Swap `sushi_config.json` → `sushi_config_stomp.json` (different plugin paths, audio backend)
2. Run on the board's Elk Audio OS where Sushi and Sensei are system services

## Building a Desktop VST3 Plugin (JUCE / CMake)

If a plugin uses JUCE as a submodule (a `JUCE/` directory at the root) rather than an installed copy, its `CMakeLists.txt` will have `find_package(JUCE CONFIG REQUIRED)` active and `add_subdirectory(JUCE)` commented out. Swap them — JUCE is not installed system-wide in this environment.

```bash
# Configure and build (from the plugin source directory)
mkdir build && cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release --parallel
```

The VST3 bundle lands at:
```
build/<PluginName>_artefacts/Release/VST3/<PluginName>.vst3
```

Copy it to the devkit's macOS plugin directory so Sushi can find it:
```bash
cp -r build/<PluginName>_artefacts/Release/VST3/<PluginName>.vst3 \
    /path/to/elk-stomp-devkit/plugins/vstplugins-macos/
```

In `sushi_config.json` reference it by filename only (Sushi is launched with `--base-plugin-path` pointing to `plugins/vstplugins-macos/`):
```json
{"path": "MyPlugin.vst3", "name": "MyPlugin", "type": "vst3x", "uid": "MyPlugin"}
```

After copying, clear macOS quarantine flags on the new bundle:
```bash
sudo xattr -rc plugins/vstplugins-macos/<PluginName>.vst3
```

If the CMakeCache is stale (e.g. built previously in a different location), delete the `build/` directory and reconfigure from scratch.

## Deploying to the Board

SSH credentials: username `mind`, password `elk` (or key-based auth). Default IP varies by setup.

```bash
ssh mind@<board-ip>
```

The board has these directories pre-populated at `/home/mind/`:
- `bin/` — `run-example.sh`, `setup-sushi-env.sh`, sushi binary
- `plugins/` — VST3/LV2 plugin bundles
- `wavfiles/` — audio samples for the wav streamer
- `guru/` — Guru library source

**Deploying an example** — create the destination directory first, then copy (scp will nest the folder if the target already exists):

```bash
ssh mind@<board-ip> "mkdir -p /home/mind/my-example"
scp -r examples/my-example/ mind@<board-ip>:/home/mind/my-example/
```

**Deploying a cross-compiled VST3 plugin** — Sushi on the board looks for `armv7l-linux/` inside the bundle (Steinberg's cmake outputs `x86_64-linux/` — rename on copy):

```bash
ssh mind@<board-ip> "mkdir -p /home/mind/plugins/myplugin.vst3/Contents/armv7l-linux"
scp build-elk/VST3/Release/myplugin.vst3/Contents/x86_64-linux/myplugin.so \
    mind@<board-ip>:/home/mind/plugins/myplugin.vst3/Contents/armv7l-linux/myplugin.so
```

**Running on the board:**

```bash
ssh mind@<board-ip>
cd /home/mind
bin/run-example.sh my-example   # path to the example directory
```

The script starts sensei, sushi, and the glue app in the background. `Ctrl+C` stops all three cleanly (SIGINT triggers the cleanup trap). If a session is orphaned, use `kill -INT $(pgrep -f run-example.sh)` — never `killall` (SIGTERM), as that leaves the audio driver in a bad state requiring a reboot.

## Creating a New Example

Clone the closest existing example and modify it:

```bash
cp -r examples/ex1/ examples/my-example/
```

The minimum set of files:
- `glue.py` — subclass `GlueApp`, wire up `MAPPINGS`, optionally use `DisplayManager`
- `param_mappings.py` — list of `PluginParameterMapping` and `BypassMapping` objects
- `sushi_config.json` — desktop config (CoreAudio/PortAudio backend)
- `sushi_config_stomp.json` — board config (real-time backend, different plugin paths)

`param_mappings.py` structure:
```python
from guru.mappings import PluginParameterMapping, BypassMapping

MAPPINGS = [[
    PluginParameterMapping(track_name="TRACK", plugin_name="MyPlugin",
        parameter_name="Gain", controller_name="POT1"),
    BypassMapping(plugin_name="MyPlugin", controller_name="SW1"),
]]
```

Controller names (`POT1`–`POT4`, `SW1`–`SW4`) correspond to the physical knobs and footswitches on the STOMP hardware, emulated by the board-gui on desktop.

## Sushi Config for the Board

`sushi_config_stomp.json` differences from the desktop config:
- No `"hw_config"` audio backend block — the board uses `-r` (real-time) mode
- Plugin paths are relative to `$VSTPLUGINS_PATH` (`/home/mind/plugins/`, set by `bin/setup-sushi-env.sh`) — just use the bundle filename
- Channel counts reflect the board's hardware I/O (typically 4-channel output from a mono source)

VST3 plugin entry:
```json
{"path": "myplugin.vst3", "name": "MyPlugin", "type": "vst3x", "uid": "MyPlugin"}
```

Mono-to-stereo output routing (duplicate mono track channel to all engine channels):
```json
"outputs": [
    {"engine_channel": 0, "track_channel": 0},
    {"engine_channel": 1, "track_channel": 0},
    {"engine_channel": 2, "track_channel": 0},
    {"engine_channel": 3, "track_channel": 0}
]
```

The `uid` field must match the plugin's internal FUID string — for Steinberg SDK plugins this is typically the class name registered in `vstentry.cpp`. For JUCE plugins it is the `PRODUCT_NAME` value from `juce_add_plugin()` in `CMakeLists.txt`.

## Board Connectivity

### Serial port discovery

The board exposes 4 serial ports over USB — always use the lowest-indexed one.

**macOS:**
```bash
ls /dev/tty.usbserial-*   # pick the one with the lowest number
picocom -b 115200 /dev/<port>
```

**Linux:**
```bash
ls /dev | grep ttyUSB      # pick the lowest index, e.g. ttyUSB0
picocom -b 115200 /dev/ttyUSB0
```

**Windows:** Open Device Manager → Ports (COM & LPT). Try each listed COM port in PuTTY with baud rate 115200.

Login: username `mind`, password `elk`

### Finding the board's IP address

Easiest if you already have serial access — run on the board:
```bash
ipconfig
```

Otherwise, scan your local network (replace subnet as needed):
```bash
nmap -sS -p 22 -sV --open 192.168.1.0/24
```

### WiFi setup

Supported adapters use the 88x2bu driver. Connect via serial first, then use `connmanctl`.

### Flashing a new OS image

Re-flashing wipes the board to factory state — back up any files first.

1. Check current version: `cat /etc/sw_version`
2. Download the latest image: [Stomp version 1.2.0](https://os-public-releases.elk.audio/download/elk-audio-os-builder-stm32mp157f-toolchain-v1.2.0.zip)
3. Flash to SD card with [balenaEtcher](https://etcher.balena.io/), then reboot.

## Known Issues

- **Unclean Sushi exit causes board reboot:** If Sushi is killed without going through `run-example.sh`'s cleanup trap (e.g. SIGTERM, SIGKILL, or a dropped SSH connection), the next Sushi launch will hang and force a reboot. This is a known audio driver bug. Always stop examples with `Ctrl+C` (SIGINT) via `run-example.sh`, or remotely with `kill -INT $(pgrep -f run-example.sh)`. Never use `killall` (sends SIGTERM). If it happens, reboot the board and wait for a clean start. This will be fixed in an upcoming release.
