# Still in development

# ETL Testing GUI

This Python GUI facilitates coldbox testing of ETL detector modules.

## Requirements

### Hardware
- Recirculating chiller
- Dry air supply
- Arduino sensors
    - DHT22 temperature/humidity sensor
    - [Type-T thermocouple](https://a.co/d/5xr8zDA) (x2)
    - [Thermocouple SPI digital interface](https://www.playingwithfusion.com/productview.php?catid=1001&pdid=64)
- Xilinx KCU105 FPGA Board
- CAEN NDT1470 high-voltage power supply
- SIGLENT SPD3303X-E low-voltage power supply
- Coldbox (see coldbox setup below)


### Software
- OS: Ubuntu 20.04.1
- [Vivado 2021.1](https://www.xilinx.com/support/download/index.html/content/xilinx/en/downloadNav/vivado-design-tools/archive.html)


## Coldbox Setup

For detailed instructions and documentation on the mechanical, electrical, thermal, and safety aspects of the coldbox, refer to the [documentation](./BU%20ETL%20Cold%20Box%20Documentation.pdf) and/or the [step file](./BU%20Coldbox%20V1.stp) to see the 3D model.

## Installation

### Note: Some steps require sudo privileges

The following instructions were adapted from [this original SOP](./ETL_test_stand_setup.md), which you should refer to if any step is unclear.

### Cloning the repo

To clone this repo, please run `git clone --recurse-submodules <repo url>`. It is necessary to run with the `--recurse-submodules` flag so that Tamalero (which is imported as a submodule) is properly cloned inside the repo.

### Vivado installation

You can follow [this link](https://www.xilinx.com/support/download/index.html/content/xilinx/en/downloadNav/vivado-design-tools/archive.html) and navigate to the 2021.1 download. Either the linux self-extracting web installer or tar file should be fine. You will likely have to make an account on the AMD website to download either. For specific instructions for unpacking the tar file and managing the license, see the [original SOP](./ETL_test_stand_setup.md). 

### IPbus installation

To download the IPbus software, move to the `scripts/` directory and run `source setup_ipbus.sh`. This [SOP](./ETL_test_stand_setup.md) also gives the step-by-step instructions.

### General setup

First, you need to setup the virtual environment, for which we are using Astral's uv. To set this up, navigate to the project root directory and run

```source scripts/setup_env.sh```

This script does the following:
- Downloads uv if not already installed
- Sets up pathing for Tamalero
- Creates virtual environment with uv
    - Removes existing uv venv
    - Cleans cache
    - Updates uv to latest version
    - Installs and pins python version (3.14.2)
    - Initializes venv and installs project dependencies
- Adds Vivado to path if not already

### Flashing firmware
You can follow the directions here on the [rbdocs](https://etl-rb.docs.cern.ch/Firmware/rb-firmware/#firmware-for-kcu-105)

## User's Guide

To run the GUI, navigate to the project root directory and run `uv run -m GUI.app`. Make sure you have already set up the uv venv. 

## Contact

This project was written by Bobby Vitale (bobby21@bu.edu) and Insung Hwang (insert email) at Boston University. Please feel free to reach out with questions or issues. 