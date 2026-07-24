from typing import Literal

from etlup.base_model import ConstructionBase
from etlup.tamalero.Baseline import BaselineV0
from etlup.tamalero.Noisewidth import NoisewidthV0

from qaqc import register, required
from qaqc.errors import FatalTestError, NonFatalTestError


class ChargeInjectionV0(ConstructionBase):
    name: Literal["charge_injection"] = "charge_injection"
    version: Literal["v0"] = "v0"
    charge_fc: int
    pulses_per_etroc: int
    row: int
    col: int
    hits_per_etroc: list[int]


@register(ChargeInjectionV0)
@required([BaselineV0, NoisewidthV0])
def test(session) -> ChargeInjectionV0:
    """Inject charge into one pixel on each connected ETROC."""
    # Keep these imports local so the GUI can start on Windows without uHAL.
    from tamalero.DataFrame import DataFrame
    from tamalero.FIFO import FIFO

    row = 0
    col = 0
    charge_fc = 15
    pulses = 100
    qinj_delay = 10
    l1a_delay = 501
    rb_l1a_delay = 504

    module = session.readout_board.modules[session.current_slot]
    fifo = FIFO(rb=session.readout_board)
    hits_per_etroc = []
    connected_etroc_count = 0

    for etroc in module.ETROCs:
        if not etroc.is_connected():
            hits_per_etroc.append(0)
            continue
        connected_etroc_count += 1
        session.report_status(
            f"Injecting {charge_fc} fC into ETROC {etroc.chip_no}..."
        )

        threshold = int(etroc.baseline[row, col] + 20)
        try:
            fifo.reset()
            etroc.bypass_THCal()
            etroc.QInj_set(
                charge_fc,
                qinj_delay,
                l1a_delay,
                row=row,
                col=col,
                broadcast=False,
            )
            etroc.wr_reg(
                "DAC",
                threshold,
                row=row,
                col=col,
                broadcast=False,
            )
            fifo.send_QInj(count=pulses, delay=rb_l1a_delay)
            words = fifo.pretty_read(DataFrame())
        finally:
            etroc.QInj_unset(row=row, col=col, broadcast=False)

        hits = sum(int(word[1]["hits"]) for word in words if word[0] == "trailer")
        hits_per_etroc.append(hits)

    if connected_etroc_count == 0:
        raise FatalTestError("Module has no ETROCs to test")
    if not any(hits_per_etroc):
        raise NonFatalTestError(
            "Charge injection returned zero hits on every ETROC"
        )
    if any(hits == 0 for hits in hits_per_etroc):
        raise NonFatalTestError(
            f"Charge injection returned zero hits on some ETROCs: "
            f"{hits_per_etroc}"
        )

    return ChargeInjectionV0(
        **session.current_base_data,
        charge_fc=charge_fc,
        pulses_per_etroc=pulses,
        row=row,
        col=col,
        hits_per_etroc=hits_per_etroc,
    )
