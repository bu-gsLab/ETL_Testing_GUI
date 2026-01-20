# TODOs
- check tamalero calcuation
- incorporate ptat signal calculation into tamalero (check merge request by tao)
- support other sized readout boardss
- Ask engineers about LV RB, Penable, Groun and PTAT signls

# Purpose
Compares all signals outputted by the MUX64 chip to defined values in the qaqc: low voltage power, high voltage power, VREF on all modules, temperature on ETROCs, power to modules. 

# VREF Pins
After measuring VREF many times we found the following values for the module:
```
VREF1: 1.034+/-0.001
VREF2: 1.034+/-0.001
VREF3: 1.033+/-0.001
VREF4: 1.034+/-0.001
```
So we chose 1.03 +/- 1% as suggested by Ted. 

# VTEMP Pins
Bobby and Joshua, found ~340 raw ADC counts for the disconnected VTEMP lines. Using old test beam data at -25C the raw adc value was 123. The range chosen for values is 100 to 330.

[link to adc with 123 at -25C](https://cernbox.cern.ch/json-viewer/eos/project/m/mtd-etl-system-test/public/DESY_April_2025/run_logs/runs_118311_118510.json?contextRouteName=files-spaces-generic&contextRouteParams.driveAliasAndItem=eos/project/m/mtd-etl-system-test/public/DESY_April_2025/run_logs&contextRouteQuery.sort-by=name&contextRouteQuery.sort-dir=asc)

# Penable Pins
TODO

# LV RB Pin
TODO

# Ground Pin
TODO



---


# Notes 
What about the unconnected modules for vtemp?
```
┌───────────────┬───────┬─────────────────┬───────────────────┬────────────────────┬──────────────────┬────────────────────┐
│ Channel       │   Pin │   Reading (raw) │   Reading (calib) │   Voltage (direct) │   Voltage (conv) │ Comment            │
├───────────────┼───────┼─────────────────┼───────────────────┼────────────────────┼──────────────────┼────────────────────┤
│ LV_RB         │     0 │             436 │          430.455  │          0.426635  │        9.38597   │ LV RB              │
│ PTAT4         │    17 │              51 │           53.9329 │          0.0497915 │        0.270761  │ PTAT4              │
│ PENABLE4      │    18 │             621 │          621.213  │          0.608223  │        1.21449   │ PEnable4           │
│ PTAT5         │    19 │              50 │           51.9354 │          0.0497915 │        0.265554  │ PTAT5              │
│ PENABLE5      │    20 │             622 │          621.213  │          0.607247  │        1.21645   │ PEnable5           │
│ PTAT3         │    21 │              50 │           50.9367 │          0.0497915 │        0.265554  │ PTAT3              │
│ PTAT2         │    23 │              51 │           52.9341 │          0.051744  │        0.275968  │ PTAT2              │
│ PENABLE2      │    24 │             621 │          621.213  │          0.607247  │        1.21449   │ PEnable2           │
│ PTAT1         │    25 │              51 │           51.9354 │          0.0507677 │        0.270761  │ PTAT1              │
│ PENABLE1      │    26 │             621 │          621.213  │          0.608223  │        1.21645   │ PEnable1           │
│ GROUND        │    63 │              37 │           56.9291 │          0.0380761 │        0.0761522 │ Background         │
│ mod0_a4       │     2 │             292 │          250.683  │          0.286051  │        0.572102  │ VREF3 on module 1  │
│ mod0_a5       │     3 │             293 │          293.629  │          0.287027  │        0.574054  │ VREF2 on module 1  │
│ mod0_a6       │     4 │             292 │          293.629  │          0.286051  │        0.572102  │ VREF4 on module 1  │
│ mod0_a7       │     5 │             293 │          293.629  │          0.287027  │        0.574054  │ VREF1 on module 1  │
│ mod1_a4       │     6 │             293 │          293.629  │          0.287027  │        0.574054  │ VREF3 on module 2  │
│ mod1_a5       │     7 │              38 │           38.9519 │          0.0380761 │        0.0761522 │ VREF2 on module 2  │
│ mod1_a6       │     8 │             293 │          290.633  │          0.287027  │        0.574054  │ VREF4 on module 2  │
│ mod1_a7       │     9 │             293 │          293.629  │          0.287027  │        0.576007  │ VREF1 on module 2  │
│ mod2_a4       │    10 │             530 │          530.329  │          0.517429  │        1.03681   │ VREF3 on module 3  │
│ mod2_a5       │    11 │             530 │          530.329  │          0.518405  │        1.03681   │ VREF2 on module 3  │
│ mod2_a6       │    12 │             530 │          530.329  │          0.518405  │        1.03681   │ VREF4 on module 3  │
│ mod3_a7       │    13 │             530 │          530.329  │          0.518405  │        1.03681   │ VREF1 on module 3  │
│ ETROC1_VTEMP2 │    14 │             293 │          294.628  │          0.286051  │        0.574054  │ VTEMP2 in module 1 │
│ ETROC2_VTEMP2 │    15 │             286 │          287.636  │          0.280193  │        0.562339  │ VTEMP2 in module 2 │
│ ETROC3_VTEMP2 │    16 │             293 │          300.62   │          0.287027  │        0.574054  │ VTEMP2 in module 3 │
│ ETROC2_VTEMP4 │    60 │             293 │          297.624  │          0.287027  │        0.576007  │ VTEMP4 in module 2 │
│ ETROC2_VTEMP1 │    59 │             294 │          293.629  │          0.288003  │        0.574054  │ VTEMP1 in module 2 │
│ ETROC2_VTEMP3 │    58 │             293 │          293.629  │          0.287027  │        0.574054  │ VTEMP3 in module 2 │
│ ETROC1_VTEMP4 │    57 │             294 │          294.628  │          0.288003  │        0.574054  │ VTEMP4 in module 1 │
│ ETROC1_VTEMP1 │    56 │             290 │          290.633  │          0.285075  │        0.570149  │ VTEMP1 in module 1 │
│ ETROC1_VTEMP3 │    55 │             293 │          288.635  │          0.287027  │        0.574054  │ VTEMP3 in module 1 │
│ ETROC3_VTEMP3 │    36 │             315 │          316.6    │          0.309482  │        0.617011  │ VTEMP3 in module 3 │
│ ETROC3_VTEMP1 │    35 │             293 │          294.628  │          0.287027  │        0.576007  │ VTEMP1 in module 3 │
│ ETROC3_VTEMP4 │    34 │             293 │          293.629  │          0.287027  │        0.574054  │ VTEMP4 in module 3 │
└───────────────┴───────┴─────────────────┴───────────────────┴────────────────────┴──────────────────┴────────────────────┘
```