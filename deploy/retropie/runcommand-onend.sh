#!/bin/sh
# Always clear the virtual game when the emulator exits.
. /home/pi/.config/rob-vision/receiver.env
ROB_VISION_URL="$ROB_VISION_URL" ROB_VISION_TOKEN_FILE="$ROB_VISION_TOKEN_FILE" \
    /usr/bin/python3 /home/pi/rob-vision/tools/notify_game.py end "$@" >/dev/null || :
