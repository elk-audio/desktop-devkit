#!/bin/bash -e

# enable this for extra logging to /tmp/sushi.log and /tmp/sensei.log
#EXTRA_LOGGING="-l debug --log-flush-interval=1"

if [ $(uname -o) = "Msys" ]; then
    SUSHI_BIN="bin/win/sushi.exe --portaudio"

    # uncomment this line and change the audio device IDs to the ones from
    # --dump-audio-devices if the default devices don't work
    #SUSHI_BIN="bin/sushi.exe --portaudio --audio-output-device=2 --audio-input-device=3"
    GLUE_RUNNER="uv run"
    SUSHI_CONFIG="sushi_config.json"
elif [ $(uname -o) = "Darwin" ]; then
    SUSHI_BIN="bin/macos/sushi --coreaudio"
    GLUE_RUNNER="uv run"
    SUSHI_CONFIG="sushi_config.json"
else
    # stomp board
    SUSHI_BIN="sushi -r"
    GLUE_RUNNER="python3"
    SUSHI_CONFIG="sushi_config_stomp.json"
    ON_BOARD=1
fi

export EXAMPLE_PATH="$1"
if [ -z "$EXAMPLE_PATH" -o ! -d "$EXAMPLE_PATH" ]; then
    echo "usage: $0 <path_to_example>"
    exit 1
fi

source bin/setup-sushi-env.sh

cleanup() {
  echo "Stopping all processes..."
  kill 0
}

trap cleanup INT

# Start sensei (on the board)
if [ ! -z "$ON_BOARD" ]; then
    echo "Starting sensei..."
    sensei -f /home/mind/sensei_config.json $EXTRA_LOGGING &
    sleep 2
fi

# Start Sushi
echo "Starting sushi..."
$SUSHI_BIN -c "$EXAMPLE_PATH/$SUSHI_CONFIG" --base-plugin-path="$VSTPLUGINS_PATH" $EXTRA_LOGGING &

sleep 2

# Guru is installed in the home folder on the board for easy modification
if [ ! -z "$ON_BOARD" ]; then
    export PYTHONPATH=$PYTHONPATH:/home/mind/guru/src
fi

# Needed for the generated sushi gRPC bindings
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Start the glue app
echo "Starting glue app..."
$GLUE_RUNNER "$EXAMPLE_PATH/glue.py" &

echo "Press Ctrl+C to stop all processes"
wait
