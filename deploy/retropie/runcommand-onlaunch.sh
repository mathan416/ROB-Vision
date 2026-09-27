#!/bin/sh
# RetroPie invokes this immediately before starting the selected game.
# Game launches only notify the UNO Q; they never edit RetroArch configuration.
. /home/pi/.config/rob-vision/receiver.env
ROB_VISION_URL="$ROB_VISION_URL" ROB_VISION_TOKEN_FILE="$ROB_VISION_TOKEN_FILE" \
    /usr/bin/python3 /home/pi/rob-vision/tools/notify_game.py start "$@" >/dev/null || :
