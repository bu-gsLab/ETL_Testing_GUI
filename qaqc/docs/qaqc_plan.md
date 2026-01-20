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
