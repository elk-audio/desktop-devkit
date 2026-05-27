# Building Plugins for Stomp

This guide covers cross-compiling audio plugins for the Elk Stomp board. For a more in-depth reference, see the [Elk documentation](https://elk-audio.github.io/elk-docs/html/embedded/building_plugins_for_elk.html).

***Note: The Elk Stomp SDK is not public but if you have purchased a Development Board you should have received a link to download it***.


## Prerequisites

- **Docker** installed and running or a **linux machine** (native or virtual)
- The **Elk Stomp Builder SDK** (distributed separately as a Docker context)
- **Apple Silicon users**: enable Rosetta 2 in Docker Desktop settings before proceeding

### Building the Docker image

From the SDK directory:

```bash
# Intel/AMD
docker image build -t elk-builder-stomp .

# Apple Silicon
docker image build --platform linux/amd64 -t elk-builder-stomp .
```

### Installing the SDK (native or virtual linux machine)

The SDK is distributed as a self-installing shell script. Execute it and follow the instructions. If neccesary, add executable permissions before.
```bash
chmod +x ./elk-glibc-x86_64-audio-os-image-xxxx-toolchain-vx.y.x.sh
./elk-glibc-x86_64-audio-os-image-xxxx-toolchain-vx.y.x.sh
```

## Compiling a plugin

Mount your plugin source into the container and run the build. The SDK environment must be sourced before CMake.

### JUCE plugins (VST3 / LV2)

```bash
docker run -it --platform linux/amd64 --rm \
  -v /path/to/your/plugin:/workdir \
  elk-builder-stomp
```

Then inside the docker container or linux machine you can run:

```bash
# set up the cross-compilation environment
source /SDKs/elk-stomp-dev/environment-setup-cortexa7t2hf-neon-vfpv4-elk-linux-gnueabi

# build as normal with cmake
cd /workdir && mkdir -p build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)
```

Your CMakeLists.txt should use `find_package(JUCE CONFIG REQUIRED)` (not `add_subdirectory`) and include `VST3_AUTO_MANIFEST FALSE`.

The Docker image ships with JUCE 8 pre-built against the Elk sysroot.

### Important note for VST3
After cross-compilation, ensure that the folder *"plugin.vst3/Contents"* is named correctly, it should match your target Elk device architecture and not a general **arm64-linux**. For the Raspberri Pi 4 image the correct architecture should be **aarch64-linux**, for Elk Stomp it should be **armv7l-linux** or else the plugin will not work correctly - rename it yourself if neccesary.

## Copying the plugin to the board

Once built, copy the `.vst3` or `.lv2` bundle to the board over SSH:

```bash
scp -r build/MyPlugin.vst3 mind@<board-ip>:plugins/
```

Then reference it in your Sushi config JSON and restart Sushi.

## Building with an AI coding agent

Elk Stomp supports building plugins with the help of AI coding agents. If you're using one, you can ask it directly:

> *Help me build and test a plugin on the Stomp board.*

The agent can help scaffold the plugin, set up the CMake config, run the Docker build, and iterate on the code.
