import numpy as np
from etlup.tamalero.Noisewidth import NoisewidthV0
from qaqc import register, required
from etlup.tamalero.Baseline import BaselineV0
from etlup.tamalero.ReadoutBoardCommunication import ReadoutBoardCommunicationV0

@register(NoisewidthV0)
@required([ReadoutBoardCommunicationV0, BaselineV0])
def test(session) -> NoisewidthV0:
    """
    Uploads the noise widths from threshold scan run during the baseline test.
    If 'config' is provided (from TestSequence), it uses it as a base/configuration.
    Returns a fully populated NoisewidthV0 instance.
    """
    slot = session.current_slot
    rb = session.readout_board
    module = rb.modules[slot - 1]
    etroc_noisewidths = []

    for etroc in module.ETROCs:
        if not etroc.is_connected():
            print(f"ETROC {etroc.chip_no} not found")
            etroc_noisewidths.append(np.zeros((16,16)).tolist())
            continue

        etroc_noisewidths.append(etroc.noise_width.tolist())

    data = session.current_base_data | {
        "pos_0": etroc_noisewidths[0],
        "pos_1": etroc_noisewidths[1],
        "pos_2": etroc_noisewidths[2],
        "pos_3": etroc_noisewidths[3]
    }
    
    return NoisewidthV0(**data)
