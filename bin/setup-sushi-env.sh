#!/bin/bash -e

if [ $(uname -o) = "Msys" ]; then
    export LV2_PATH=$PWD/plugins/gxplugins-win/
    export VSTPLUGINS_PATH=$PWD/plugins/vstplugins-win/
elif [ $(uname -o) = "Darwin" ]; then
    export LV2_PATH=$PWD/plugins/gxplugins-macos-universal/
    export VSTPLUGINS_PATH=$PWD/plugins/vstplugins-macos/
else
    export LV2_PATH=/home/mind/plugins/gxplugins-stomp/
    export VSTPLUGINS_PATH=/home/mind/plugins/
fi
