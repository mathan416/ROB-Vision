#!/bin/sh
# RetroPie invokes this immediately before starting the selected game.
case "$1:$2" in
    nes:lr-robvision-*|famicom:lr-robvision-*)
        # A physical controller may have connected after the receiver started.
        # Refresh the udev slot before RetroArch reads its NES configuration.
        sudo -n /usr/bin/python3 /home/pi/rob-vision/scripts/install.py player2 >/dev/null ||
            echo 'R.O.B. Vision: could not refresh RetroArch Player 2 mapping.' >&2
        ;;
esac
. /home/pi/.config/rob-vision/receiver.env
ROB_VISION_URL="$ROB_VISION_URL" ROB_VISION_TOKEN_FILE="$ROB_VISION_TOKEN_FILE" \
    /usr/bin/python3 /home/pi/rob-vision/tools/notify_game.py start "$@" >/dev/null || :
