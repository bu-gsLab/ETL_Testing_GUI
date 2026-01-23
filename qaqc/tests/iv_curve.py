from qaqc import register, required
from qaqc.errors import FailedTestCriteriaError
from etlup.IVCurve import IVCurveV0
from pathlib import Path
import yaml
from ...drivers.HV.hv_driver import HVPowerSupply

@register(IVCurveV0)
# FIXME: The shortest test that checks ETROC connection and powers it on should be required below
@required(["ReadoutBoardCommunicationV0"])
def test(session):
    """
    Conducts IV curve test based on given parameters
    """
    try:
        # load test parameters from yaml
        test_param_yaml_path = Path(__file__).parent / 'configs' / 'iv_curve_parameters.yaml'
        with open(test_param_yaml_path, 'r') as f:
            test_params = yaml.safe_load(f)

        CAEN_Supply = HVPowerSupply("/dev/hv_supply")

        ramp_up = test_params["ramp_up"]
        ramp_down = test_params["ramp_down"]
        CAEN_Supply.set_ramp_up(ramp_up)
        CAEN_Supply.set_ramp_down(ramp_down)
        if CAEN_Supply.read_polarity()['VAL'] == "+":
            raise FailedTestCriteriaError("HV supply polarity is positive when it should be negative")

        start_v = test_params["start_voltage"]
        stop_v = test_params["stop_voltage"]
        step_v = test_params["voltage_step"]
        curr_lim = test_params["current_limit"]
        leave_on = test_params["leave_on"]
        delay = test_params["delay"]

        voltages, currents, k_factors = CAEN_Supply.IV_curve(start_v, stop_v, step_v, curr_lim, leave_on, delay)
    
        # TODO: Run a check on results to catch "bad" IV curves that don't raise existing exceptions (tripping supply)


    except Exception as e:
        raise FailedTestCriteriaError(str(e))
        
    data = {
        "voltages": voltages,
        "currents": currents,
        "k-factors": k_factors,
        "test_parameters": test_params
    }

    return IVCurveV0(**data)
