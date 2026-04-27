import time
import os
from tamalero.utils import get_kcu
from tamalero.ReadoutBoard import ReadoutBoard
from datetime import datetime

import numpy as np
from etlup.tamalero.Baseline import BaselineV0
from etlup.tamalero.ReadoutBoardCommunication import ReadoutBoardCommunicationV0
from qaqc import register, required
from qaqc.errors import FailedTestCriteriaError
from qaqc.session import Session
from drivers.HV.hv_driver import HVPowerSupply

@register(BaselineV0)
@required([ReadoutBoardCommunicationV0])
def test(session) -> BaselineV0:
    """
    Runs the threshold scan. Uploads the baselines.
    If 'config' is provided (from TestSequence), it uses it as a base/configuration.
    Returns a fully populated BaselineV0 instance.
    """

    # Assume current_base_data['module'] is formatted like "40029" not "MP40029"
    MID = int(session.current_base_data["module"])
    timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
    timezone = "-04:00"
    timestamp_upload = datetime.strptime(timestamp + timezone, "%Y-%m-%d-%H-%M-%S%z")
    result_dir = f"results/{MID}/{timestamp}/"

    if not os.path.isdir(result_dir):
        os.makedirs(result_dir)

    rb = session.readout_board

    print("Connecting modules")
    slot = session.current_slot

    moduleids = [0] * session.rb_size
    moduleids[slot] = MID
    rb.connect_modules(
        moduleids=moduleids, 
        hard_reset=True, 
        ext_vref=True,
        use_etroc_team_config=True)
    
    print("MUX64:")
    rb.MUX64.read_channels()

    print("DAQ LPGBT:")
    rb.DAQ_LPGBT.read_adcs()

    print("TRIG LPGBT:")
    rb.TRIG_LPGBT.read_adcs()
    
    module = rb.modules[slot]
    rb.select_module(slot)
    
    if not module.connected:
        raise ValueError(f"Selected module slot {slot} is not connected.")
        
    rb.disable_MUX64()
    etroc_vtemps = []
    etroc_baselines = []

    bias = session.bias_volts[slot]
    sensor = session.sensor_types[slot] # "FBK" or "HPK"
    hybrid_num = session.hybrid_nums[slot]
    sensor_to_current = {"FBK": 100, "HPK": 10}
    compliance = sensor_to_current[sensor] * hybrid_num

    with HVPowerSupply("hv_supply") as hv:
        hv.set_voltage(bias)
        hv.set_current_limit(compliance)
        hv.set_channel_on()
        hv.wait_ramp(0.5)

        for etroc in module.ETROCs:
            etroc_vtemps.append(etroc.check_temp())
            if not etroc.is_connected():
                print(f"ETROC {etroc.chip_no} not found")
                etroc_vtemps.append(None)
                etroc_baselines.append(np.zeros((16,16)).tolist())
                continue
                
            print(f"Found connected ETROC {etroc.chip_no} on module")

            etroc.run_etroc_team_threshold_scan(skip_config=True)

            etroc.plot_threshold(outdir=result_dir, noise_width=False)
            etroc.plot_threshold(outdir=result_dir, noise_width=True)
            etroc_baselines.append(etroc.baseline.tolist())
        # HV already set to ramp down and turn off upon exit

    data = session.current_base_data | {
        'ambient_celcius': session.room_temp_celcius,
        "measurement_date": timestamp_upload,
        "etroc_0_Vtemp": etroc_vtemps[0],
        "etroc_1_Vtemp": etroc_vtemps[1],
        "etroc_2_Vtemp": etroc_vtemps[2],
        "etroc_3_Vtemp": etroc_vtemps[3],
        "bias_volts": bias,
        "pos_0": etroc_baselines[0],
        "pos_1": etroc_baselines[1],
        "pos_2": etroc_baselines[2],
        "pos_3": etroc_baselines[3],
    }
    
    return BaselineV0(**data)