from __future__ import annotations
from typing import Optional, Dict, Any, Literal, List
from module_test_sw.tamalero.KCU import KCU
from module_test_sw.tamalero.ReadoutBoard import ReadoutBoard
from qaqc import TestSequence
from typing_extensions import List, Dict
from etlup import TestType, now_utc
from etlup.base_model import ConstructionBase
from qaqc.errors import (
    FatalTestError,
    MissingRequiredTestError,
    NonFatalTestError,
)

class RbSizeTuple(tuple):
    """
    Just renaming for clarity, that these tuples have size length of rb_size
    """
    def __new__(cls, iterable, size: int):
        instance = super().__new__(cls, iterable)
        if len(instance) != size:
            raise ValueError(f"Expected tuple of size {size}, but got {len(instance)}")
        return instance

    def __class_getitem__(cls, item):
        return cls

class Session:
    def __init__(
        self,
        kcu_ipaddress: str,
        rb: int,
        rb_size: Literal[3,6,7],
        rb_serial_number: str,
        modules: List[str],
        location: str = "BU",
        user_created: str = "unknown",
        room_temp_celcius: Optional[int] = None,
        bias_voltage: Optional[int] = None,
        sensor_types: Optional[list[str]] = None,
        hybrid_nums: Optional[list[int]] = None
    ):
        # Config variables
        self.kcu_ipaddress: str = kcu_ipaddress
        self.rb: int = rb
        self.rb_size: int = rb_size
        self.rb_serial_number = rb_serial_number
        self.modules: RbSizeTuple = RbSizeTuple(modules, size=rb_size)
        self.location = location
        self.user_created = user_created
        self.room_temp_celcius: float = room_temp_celcius
        self.current_slot = None
        self.bias_voltage = bias_voltage
        self.sensor_types = sensor_types
        self.hybrid_nums = hybrid_nums

        # Session state
        self.kcu: Optional[KCU] = None
        self.readout_board: Optional[ReadoutBoard] = None
        self.results: RbSizeTuple[Dict[Any,Any]] = RbSizeTuple(
            [{} for _ in range(self.rb_size)], 
            size=self.rb_size)
        self.nonfatal_failures = RbSizeTuple(
            [set() for _ in range(self.rb_size)],
            size=self.rb_size)
        self.fatal_error: Optional[Exception] = None
        self.status_callback = None

        self.current_base_data: dict = None # current base data for pydantic etlup modules

    def report_status(self, message: str):
        if self.status_callback is not None:
            self.status_callback(message)

    @property
    def active_slots(self) -> List[int]:
        return [i for i in range(len(self.modules)) if self.modules[i] is not None]

    @property
    def rb_config(self) -> Literal["modulev2", "rb7_modulev2", "rb6_modulev2"]:
        """
        Depending on the flavor choose one of these configs.
        This config is used to instantiate a readout board.
        """
        if self.rb_size == 7:
            return "rb7_modulev2"
        elif self.rb_size == 6:
            return "rb6_modulev2"
        else:
            return "modulev2"

    @property
    def module_ids(self) -> RbSizeTuple[int]:
        """
        Tamalero requires a numerical number when instantiating.
        Will probably just take the numerical part of the serial number.
        """
        # TODO: make this actually use the module numbers?
        return [i+100 for i in range(self.rb_size)]

    def iter_test_sequence(self, test_sequence: List[TestType], slot: int):
        """
        On a particular slot of the Readout Board, execute the inputted test_sequence.

        Test Results will be stored in the session
        """
        if not slot in self.active_slots:
            raise ValueError(f"This slot was configured to not be tested. Configured modules: {self.session.modules}")
        self.current_base_data = None # drop any current base data
        
        session_results = self.results[slot]
        test_sequence = TestSequence(test_sequence)

        for test in test_sequence:
            self.current_base_data = self.get_base_data(
                test.model, slot)
            if self.fatal_error is not None:
                error = FatalTestError(
                    f"Skipped after fatal failure: {self.fatal_error}"
                )
                session_results[test.model] = None
                yield test, error
                continue
            try:
                results = test.run(self)
                if not isinstance(results, test.model):
                    raise ValueError(
                        f"Test must return {test.model.__name__}, "
                        f"but returned {type(results).__name__}"
                    )
                session_results[test.model] = results
                yield test, results
            except NonFatalTestError as e:
                session_results[test.model] = None
                self.nonfatal_failures[slot].add(test.model)
                yield test, e
            except (FatalTestError, MissingRequiredTestError) as e:
                session_results[test.model] = None
                self.fatal_error = e
                yield test, e
            except Exception as e:
                error = FatalTestError(
                    f"Unexpected fatal error in {test.model.__name__}: {e}"
                )
                session_results[test.model] = None
                self.fatal_error = error
                yield test, error

        self.current_base_data = None

    def get_base_data(self, test_model: TestType, slot: int) -> Dict:
        """
        A dictionary of all the information in SetupConfig for the upload of a test of a module
        """
        self.current_slot = slot
        res = {}
        for field in ConstructionBase.model_fields:
            if field == "measurement_date":
                res[field] = now_utc()
            elif field == "location":
                res[field] = self.location
            elif field == "user_created":
                res[field] = self.user_created
            elif field == "module":
                res[field] = self.modules[slot]
        
        if "version" in test_model.model_fields:
            res["version"] = test_model.model_fields["version"].default
        if "name" in test_model.model_fields:
            res["name"] = test_model.model_fields["name"].default

        return res

    def clear(self):
        self.kcu = None
        self.readout_board = None
        self.results = RbSizeTuple(
            [{} for _ in range(self.rb_size)], 
            size=self.rb_size)
        self.nonfatal_failures = RbSizeTuple(
            [set() for _ in range(self.rb_size)],
            size=self.rb_size)
        self.fatal_error = None
        self.current_base_data = None
