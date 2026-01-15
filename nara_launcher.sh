#!/bin/bash
# Send errors to a file so we can see why it won't start
exec 2> /home/liz/GitHub/nara-pension-grabber/launcher_error.log
/home/liz/GitHub/nara-pension-grabber/venv/bin/python /home/liz/GitHub/nara-pension-grabber/nara_bridge.py