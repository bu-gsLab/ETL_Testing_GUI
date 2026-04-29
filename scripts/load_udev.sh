#!/bin/bash
if [ -f udev/99-ETL_Testing_GUI.rules ] then
    sudo cp udev/99-ETL_Testing_GUI.rules /etc/udev/rules.d/
    sudo udevadm control --reload
    sudo udevadm trigger
fi