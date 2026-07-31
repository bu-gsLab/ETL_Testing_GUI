from dataclasses import dataclass
import ipaddress
from pathlib import Path
import tomllib

CONFIG_PATH = Path(__file__).parent.parent / "config" / "hardware.toml"

@dataclass(frozen=True)
class HardwareConfig:
    kcu_ip: str
    lv_supply_ip: str

def load_hardware_config(path: Path = CONFIG_PATH) -> HardwareConfig:
    try:
        with path.open("rb") as config_file:
            network = tomllib.load(config_file)["network"]
        config = HardwareConfig(
            kcu_ip=network["kcu_ip"],
            lv_supply_ip=network["lv_supply_ip"],
        )
        ipaddress.ip_address(config.kcu_ip)
        ipaddress.ip_address(config.lv_supply_ip)
        return config
    except (OSError, KeyError, tomllib.TOMLDecodeError, ValueError) as error:
        raise RuntimeError(
            f"Invalid hardware configuration in {path}: {error}"
        ) from error
