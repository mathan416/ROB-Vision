#!/bin/sh
# Always clear the virtual game when the emulator exits.
ROB_VISION_URL=http://arduiain.local \
ROB_VISION_TOKEN_FILE=/home/pi/.config/rob-vision/token \
    /usr/bin/python3 /home/pi/rob-vision/tools/notify_game.py end "$@" >/dev/null || :
