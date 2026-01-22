from qaqc import register, required
from qaqc.errors import FailedTestCriteriaError
from etlup.tamalero.LPGBTRegisters import LPGBTRegistersV0
import yaml
from pathlib import Path

@register(LPGBTRegistersV0)
@required(["ReadoutBoardCommunicationV0"])
def test(session):
    """
    Reads all LpGBT registers and compares them to a reference dump
    """
    try:
        rb = session.readout_board

        # load allowable MUX64 values from yaml
        lpgbt_yaml_path = Path(__file__).parent / 'configs' / 'lpgbt_registers.yaml'
        with open(lpgbt_yaml_path, 'r') as f:
            expected_lpgbt_registers = yaml.safe_load(f)

        # read all LpGBT registers 
        trig_lpgbt_registers = {}
        bad_trig_reg_val_pairs = {}
        
        daq_lpgbt_registers = {}
        bad_daq_reg_val_pairs = {}

        for n in rb.TRIG_LPGBT.nodes:
            try:
                val = rb.TRIG_LPGBT.rd_reg(n)
            except:
                val = "unable"
            
            trig_lpgbt_registers[n] = val

            # compare read values with expected
            expected_val = expected_lpgbt_registers['TRIG'][n]
            if val == expected_val:
                pass
            else:
                bad_trig_reg_val_pairs[n] = val

        for n in rb.DAQ_LPGBT.nodes:
            try:
                val = rb.DAQ_LPGBT.rd_reg(n)
            except:
                val = "unable"
            
            daq_lpgbt_registers[n] = val

            # compare read values with expected
            expected_val = expected_lpgbt_registers['DAQ'][n]
            if val == expected_val:
                pass
            else:
                bad_daq_reg_val_pairs[n] = val

        if len(bad_daq_reg_val_pairs) == 0 and len(bad_trig_reg_val_pairs) == 0:
            all_values_passed = True
        else:
            all_values_passed = False
    
        if not all_values_passed:
            raise FailedTestCriteriaError(f"Unexpected LpGBT readings --- DAQ: {len(bad_daq_reg_val_pairs)}, TRIG: {len(bad_trig_reg_val_pairs)}\nDAQ: {bad_daq_reg_val_pairs}\nTRIG: {bad_trig_reg_val_pairs}")

    except Exception as e:
        raise FailedTestCriteriaError(str(e))
        
    data = {
        "lpgbt_all_passed": all_values_passed,
        "daq_lpgbt_values": daq_lpgbt_registers,
        "trig_lpgbt_values": trig_lpgbt_registers,
        "bad_daq_lpgbt_values": bad_daq_reg_val_pairs,
        "bad_trig_lpgbt_values": bad_trig_reg_val_pairs
    }

    return LPGBTRegistersV0(**data)
