from ..components.temperature import TemperatureManager
from ..components.solenoid import ValveManager
from ..components.water_flow import WaterFlowManager
from ..components.water_level import WaterLevelManager

import logging
import os
import json

class ColdLobMonitor(object):
    def __init__(self, config_path):
        self.logger = logging.getLogger("project_lob.cold_lob_monitor")
        self.logger.info("Initializing Cold Lob Monitor")
        with open(config_path) as config_file:
            self.logger.info("Loading Cold Lob config @ {}".format(cofig_path))
            self.config = json.load(config_path)
        self.logger.info("Initializing Water Level Manager")
        self.water_level_manager = WaterLevelManager(
            list(self.config["water_level"]["monitors"].keys())
        )
        self.logger.info("Initializing Water Flow Manager")
        self.water_flow_manager = WaterFlowManager(
            list(self.config["water_flow"]["meters"].keys())
        )
        self.logger.info("Initializing Valve Manager")
        self.valve_manager = ValveManager(
            list(self.config["valves"].keys())
        )
        self.logger.info("Initializing Temperature Manager")
        self.temperature_manger = TemperatureManager(
            list(self.config["temperature"]["probes"].keys())
        )

    def run(self):
        self.logger.info("Running Cold Lob Monitor")
        while True:
            try:
                if time.time() >= self.timer:
                    self.collect_data()
                    # figure stuff out here
                time.sleep(1)
            except KeyboardInterrupt:
                self.logger.warn("Shutting down!")
                sys.exit()
