#!/bin/bash

while :
do
  # loop forever in case this gets quit somehow
  xterm -maximize -e "python3 /home/pi/camera/chris_gui_main_run_this.py"
done
