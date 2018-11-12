from ..components.temperature import TemperatureManager
from ..components.solenoid import ValveManager
from ..components.water_flow import WaterFlowManager
from ..components.water_level import WaterLevelManager

import os
import sys
import json

class ColdLobs(object):
    def __init__(self, config_path):
        self.config = json.load(config_path)
        self.water_level_manager = WaterLevelManager(
            list(self.config["water_level"]["monitors"].keys())
        )
        self.water_flow_manager = WaterFlowManager(
            list(self.config["water_flow"]["meters"].keys())
        )
        self.valve_manager = ValveManager(
            list(self.config["valves"].keys())
        )
        self.temperature_manger = TemperatureManager(
            list(self.config["temperature"]["probes"].keys())
        )

    def collect_data(self):


    def run(self):
        self.reset_timer()
        print("Running Cold Lob Controller")
        while True:
            try:
                if time.time() >= self.timer:
                    self.collect_data()
                    # figure stuff out here
                time.sleep(1)
            except KeyboardInterrupt:
                print("Shutting down...")
                sys.exit()

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
        "hot_lobs_config.json")
    cold_lobs = ColdLobs(config_path)
    cold_lobs.run()
