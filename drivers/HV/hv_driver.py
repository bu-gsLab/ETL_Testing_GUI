import serial
import time
from matplotlib.figure import Figure
import numpy as np
from pathlib import Path
import os
import csv
#from etlup.module.ModuleIV import ModuleIVV0
#from etlup import prod_session

class HVPowerSupply():
    def __init__(self, port, baud=9600, bd_addr=0, channel=0):
        self.port = port
        self.baud = baud
        self.bd_addr = bd_addr
        self.channel = channel
        self.vtol = .5
        self.ser = serial.Serial(self.port, 
                                self.baud,
                                parity=serial.PARITY_NONE,
                                stopbits=serial.STOPBITS_ONE,
                                bytesize=serial.EIGHTBITS,
                                timeout=1)
        self.flush_input_buffer()

    def __enter__(self):
        self.set_voltage(0)
        self.set_channel_off()
        self.wait_ramp(.5)
        return self
    
    def __exit__(self, type, value, traceback):
        print("Exiting, ramping down HV now")
        self.set_voltage(0)
        self.set_channel_off()
        self.wait_ramp(.5)
        self.close()
        print("Done ramping down")


    def close(self):
        if self.ser != None:
            self.ser.close()

    def send_command(self, type, channel, parameter, value=None):
        cmd = f"$BD:{self.bd_addr},CMD:{type},CH:{channel},PAR:{parameter}"
        if value is not None:
            cmd += f",VAL:{value}"
        cmd += "\r\n"
        self.ser.reset_input_buffer()
        self.ser.write(bytes(cmd, 'ascii'))
        self.ser.flush()
        response = self.ser.readline()

        return response.decode('ascii')
    
    def parse_response(self, response):
        # Example response: $BD:*,CMD:OK,VAL:*
        parts = response.strip().split(',')
        resp_dict = {}
        for part in parts:
            key, value = part.split(':')
            resp_dict[key] = value
        return resp_dict
    
    def flush_input_buffer(self):
        self.ser.flushInput()

    def set_voltage(self, voltage):
        response = self.send_command('SET', self.channel, "VSET", voltage)
        return self.parse_response(response)
    
    def set_current_limit(self, current):
        response = self.send_command('SET', self.channel, "ISET", current)
        return self.parse_response(response)
    
    def set_channel_on(self):
        response = self.send_command('SET', self.channel, "ON")
        return self.parse_response(response)
    
    def set_channel_off(self):
        response = self.send_command('SET', self.channel, "OFF")
        return self.parse_response(response)
    
    def read_vset(self):
        response = self.send_command('MON', self.channel, "VSET")
        return self.parse_response(response)
    
    def read_vmon(self):
        response = self.send_command('MON', self.channel, "VMON")
        return self.parse_response(response)
        
    def read_iset(self):
        response = self.send_command('MON', self.channel, "ISET")
        return self.parse_response(response)
    
    def read_imon(self):
        response = self.send_command('MON', self.channel, "IMON")
        return self.parse_response(response)
    
    def set_ramp_up(self, ramp_up):
        response = self.send_command('SET', self.channel, "RUP", ramp_up)
        return self.parse_response(response)
    
    def set_ramp_down(self, ramp_down):
        response = self.send_command('SET', self.channel, "RDW", ramp_down)
        return self.parse_response(response)
    
    def read_ramp_up(self):
        response = self.send_command('MON', self.channel, "RUP")
        return self.parse_response(response)
    
    def read_ramp_down(self):
        response = self.send_command('MON', self.channel, "RDW")
        return self.parse_response(response)
    
    def read_status(self):
        response = self.send_command('MON', self.channel, "STAT")
        return self.parse_response(response)
    
    def read_polarity(self):
        response = self.send_command('MON', self.channel, "POL")
        return self.parse_response(response)
    
    def wait_ramp(self, delay, stop_event=None, progress_callback=None):
        while True:
            if stop_event is not None and stop_event.is_set():
                raise InterruptedError("IV curve aborted by user")
            vmon = self.extract_float_value(self.read_vmon())
            vset = self.extract_float_value(self.read_vset())
            status = int(self.read_status()['VAL'])
            if progress_callback is not None:
                progress_callback({
                    "vset": vset,
                    "vmon": vmon,
                    "iset": self.extract_float_value(self.read_iset()),
                    "imon": self.extract_float_value(self.read_imon()),
                    "status": status,
                    "output": status & 1,
                })
            if abs(vmon-vset) <= self.vtol:
                break
            if status & 128 or status & 8:
                raise ValueError("Compliance reached, supply tripped")
            time.sleep(.1)
        if stop_event is not None:
            if stop_event.wait(delay):
                raise InterruptedError("IV curve aborted by user")
        else:
            time.sleep(delay)
        if int(self.read_status()['VAL']) & 128 or int(self.read_status()['VAL']) & 8:
                raise ValueError("Compliance reached, supply tripped")
    
    
    def extract_float_value(self, response_dict):
        if 'VAL' in response_dict:
            try:
                return float(response_dict['VAL'])
            except ValueError:
                return None
        return None
    
    def IV_curve(self, start_v, stop_v, step_v, curr_limit, leave_on, delay,
                 stop_event=None, progress_callback=None):
        n = abs((stop_v - start_v) // step_v) + 1
        voltages = []
        currents = []
        kfactors = []
        if self.read_polarity()['VAL'] == '-':
            pol = -1
        else:
            pol = 1
        self.set_current_limit(curr_limit)
        self.set_voltage(start_v)
        self.set_channel_on()
        try:
            self.wait_ramp(delay, stop_event, progress_callback)
        except ValueError as e:
            print(e)
            print(voltages, currents, kfactors)
        vmon_resp = self.read_vmon()
        imon_resp = self.read_imon()
        vmon = self.extract_float_value(vmon_resp)
        imon = self.extract_float_value(imon_resp)
        print(f"Vmon: {vmon*pol}, Imon: {imon}")
        voltages.append(vmon*pol)
        currents.append(imon)
        kfactors.append(np.nan)

        for v in range(1, int(n)):
            volt = start_v + v * step_v
            self.set_voltage(volt)
            try:
                self.wait_ramp(delay, stop_event, progress_callback)
            except ValueError as e:
                print(e)
                print(voltages, currents, kfactors)
                break
            vmon_resp = self.read_vmon()
            imon_resp = self.read_imon()
            vmon = self.extract_float_value(vmon_resp)
            imon = self.extract_float_value(imon_resp)
            if imon>0:
                kfactor = ((imon-currents[v-1])/(vmon-pol*voltages[v-1]))*(vmon/imon)
            else:
                kfactor = np.nan

            print(f"Vmon: {vmon*pol}, Imon: {imon}, K-Factor: {kfactor}")
            voltages.append(vmon*pol)
            currents.append(imon)
            kfactors.append(kfactor)
        if not leave_on:
            self.set_channel_off()
        print(voltages, currents, kfactors)
        return voltages, currents, kfactors
    
    @staticmethod
    def plot_iv_data(voltages, currents, kfactors, output_path, title="IV Curve"):
        """Plot current versus voltage without opening a GUI window."""
        fig = Figure()
        ax1 = fig.subplots()

        ax1.set_xlabel("Voltage (V)")
        ax1.set_ylabel("Current (uA)", color="red")
        ax1.set_yscale("log")
        ax1.plot(voltages, currents, "o-", ms=3, color="red", label="Current")
        ax1.tick_params(axis="y", labelcolor="red")
        ax1.grid(True, ls="--", alpha=0.3)

        if len(voltages) > 1 and voltages[-1] < voltages[0]:
            ax1.invert_xaxis()

        ax1.legend(loc="best")
        ax1.set_title(title)
        fig.tight_layout()
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_path, dpi=150)
        fig.clear()
        return output_path

    def plot_IV_curve(self, start_v, stop_v, step_v, curr_limit, moduleid,
                      leave_on=False, delay=10, comment="", stop_event=None,
                      progress_callback=None):
        """Acquire, save, and plot an IV curve; return paths and acquired arrays."""
        moduleid = str(moduleid).strip()
        if (not moduleid or moduleid in (".", "..") or
                any(char in moduleid for char in '<>:"/\\|?*')):
            raise ValueError("Module ID is not a valid folder name")
        try:
            voltages, currents, kfactors = self.IV_curve(
                start_v, stop_v, step_v, curr_limit, leave_on, delay,
                stop_event, progress_callback)
        except Exception:
            if not leave_on or (stop_event is not None and stop_event.is_set()):
                self.set_channel_off()
            raise

        timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
        maindir = Path(__file__).parent.parent.parent

        resultdir = maindir / "IV_Curves" / str(moduleid) / timestamp
        resultdir.mkdir(parents=True, exist_ok=True)

        outfile = resultdir / f"IV_Curve_{moduleid}_{timestamp}.csv"
        with open(outfile, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(voltages)
            writer.writerow(currents)
            writer.writerow(kfactors)

        commentfile = resultdir / "comment.txt"
        commentfile.write_text(comment, encoding="utf-8")

        plotfile = resultdir / f"IV_Curve_{moduleid}_{timestamp}.png"
        self.plot_iv_data(voltages, currents, kfactors, plotfile,
                          title=f"IV Curve - {moduleid}")
        return {
            "voltages": voltages,
            "currents": currents,
            "kfactors": kfactors,
            "csv_path": outfile,
            "plot_path": plotfile,
            "comment_path": commentfile,
            "result_dir": resultdir,
        }
