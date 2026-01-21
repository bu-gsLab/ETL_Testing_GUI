# Main Tasks
1. Wrap up MUX64 test
2. Find next test(s) to make and in what order

## Sub Tasks
- In the event of a crash part way through the test, what do we do? -> best decided after using the GUI for a bit
	- Make sure previous results are outputted to a file to be able to feed back in later if a crash
		- tamalero has the concept of poke? to reconnect without needing to reinstatiate
- GUI interface for qaqc
- Unit Tests
	- Maybe a simulation mode that bypasses the actual functions to check everything but the business logic is correct
        - I would suggest a decorator on each of the test functions that uses the Pydantic model (ex: BaselineV0) and use the example attached to the model

## Future Tests
- [HAYDEN] I2C with the etrocs, all of them (I can)
- [BOBBY] lpgbt registers, dump of registers to check against (before anything to do with modules)
- [BOBBY] IV curve test
	- check all have their breakdown above some limit
	- breakdown per batch that comes
	- ask lgad team what they think a good breakdown voltage value would be
	- it should not be in breakdown at this value should be the test
- [HAYDEN] check the LV and HV power supplies are in expected range (always running)
	- set the current limit per test (on the supply) at any point
	- Software updates required
	- limit will have to be a functioin of RBF size and number of modules
- baseline and noisewidths
	- classify hot pixels
	- Where on the IV curve do we want to do our baseline and noisewidth
- fast commands (QINJ, ), data readout -> qinj test, inject charge into a few pixels and read data out 
	- Note, injecting charge underbias may cause problems (chance of bad results)
	- watch power supply for current limits
