#!/bin/sh
# RetroPie invokes this immediately before starting the selected game.
ROB_VISION_URL=http://arduiain.local \
ROB_VISION_TOKEN_FILE=/home/pi/.config/rob-vision/token \
    /usr/bin/python3 /home/pi/rob-vision/tools/notify_game.py start "$@" >/dev/null || :
