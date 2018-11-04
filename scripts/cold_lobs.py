from ..components.temperature import TemperatureManager
from ..components.solenoid import ValveManager
from ..components.water_flow import WaterFlowManager
from ..components.water_level import WaterLevelManager

import json

class ColdLobs(object):
    def __init__(self, config_path):
        self.config = json.load(config_path)
        self.water_level_manager = WaterLevelManager(
            list(self.config["water_level"]["monitors"].keys())
        )
        self.water_flow_manager= WaterFlowManager(
            list(self.config["water_flow"]["meters"].keys())
        )
        self.valve_manager= ValveManager(
            list(self.config["valves"].keys())
        )
        self.temperature_manger= TemperatureManager(
            list(self.config["temperature"]["probes"].keys())
        )
