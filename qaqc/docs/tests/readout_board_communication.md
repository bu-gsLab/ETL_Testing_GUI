# TODOs
- Add VTRX+ communication check

# Purpose
Make initial connection to the Readout Board and ensure we can read and write to the registers on the Master lpGBT, Servant lpGBT, and MUX64.

# Read/Write on lpGBTs
To test we simply read the `CHIPID.USERID0` register, write a dummy value and read it back. 

# MUX64
We read pin 63. Assuming no erros means success.