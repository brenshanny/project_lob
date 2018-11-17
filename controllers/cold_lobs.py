from ..components.temperature import TemperatureManager
from ..components.solenoid import ValveManager
from ..components.water_flow import WaterFlowManager
from ..components.water_level import WaterLevelManager
from ..utils.eventlogger import EventHandler

import logging
import os
import json

class ColdLobMonitor(object):
    def __init__(self, config_path):
        self.logger = logging.getLogger("project_lob.cold_lob_monitor")
        self.logger.info("Initializing Cold Lob Monitor")
        with open(config_path) as config_file:
            self.logger.info("Loading Cold Lob config @ {}".format(cofig_path))
            self.config = json.load(config_path)["cold_lob"]
        self.event_logger = EventHandler(
            os.environ[self.config['event_logger_filename']],
            name="cold_lob_data"
        )
        self.set_interval(self.config['read_interval'])
        # set a delay for when we want to start making adjustments
        self.delay = time.time() + self.config["initial_delay"]
        self.update_delay_bool()
        self.logger.info("Initializing Water Level Manager")
        self.level_manager = WaterLevelManager(
            list(self.config["water_level"]["monitors"])
        )
        self.logger.info("Initializing Water Flow Manager")
        self.flow_manager = WaterFlowManager(
            list(self.config["water_flow"]["meters"])
        )
        self.logger.info("Initializing Valve Manager")
        self.valve_manager = ValveManager(
            list(self.config["valves"])
        )
        self.logger.info("Initializing Temperature Manager")
        self.temp_manager = TemperatureManager(
            list(self.config["temperature"]["probes"])
        )
        # create a lookup table by tank
        self.create_tank_lookup_dict()

    def create_tank_lookup_dict(self):
        self.tank_table = {
            "1": {},
            "2": {},
            "3": {},
            "4": {},
        }
        for monitor in self.level_manager.monitors:
            self.tank_table[str(monitor.tank)]["level_monitor"] = monitor
        for monitor in self.flow_manager.monitors::
            self.tank_table[str(monitor.tank)]["flow_monitor"] = monitor
        for monitor in self.temp_manager.monitors:
            self.tank_table[str(monitor.tank)]["temp_monitor"] = monitor
        for control in self.valve_manager.controllers:
            self.tank_table[str(control.tank)]["valve_controller"] = control

    def reset_timer(self):
        self.logger.info("Resetting timer!")
        self.timer = time.time() + self.interval

    def set_interval(self, val):
        self.logger.info("Setting interval: {}".format(val))
        self.interval = val

    def update_flow_reading(self):
        self.last_flows = self.flow_manager.read_monitors()

    def update_level_reading(self):
        self.last_levels = self.level_manager.read_monitors()

    def update_temp_reading(self):
        self.last_temps = self.temperature_manager.read_monitors()

    def update_delay_bool(self):
        self.past_delay = time.time() >= self.delay

    def collect_data(self):
        self.logger.info("Collecting data...")
        self.update_flow_reading()
        self.uddate_level_reading()
        self.update_temperature_reading()
        self.logger.info("Successfully collected data...")

    def log_data(self):
        # create thread ? maybe ? to log the data to the spreadsheet
        pass

    def determine_level_trends(self):
        # likely some linear regression here
        # but is it needed?
          # i guess it would be nice to adjust the magnitude of a change
          # to flow rate based on the rate of level change
        pass

    def determine_flow_targets(self):
        for tank in list(self.tank_table.keys()):
            level_offset = tank["level_monitor"].target_offset()
            flow_offset = tank["flow_monitor"].target_offset()
            if abs(level_offset) >= 0.1:
                # determine flow target
            elif abs(flow_offset) >= .05:
                # determine flow target
            else:
                # dont do anything? maybe
        # for each tank pair (level/flow)
            # take the difference between target level and current level
            # take the differnce betweent target flow and current flow
            # if the flow diff is still large and the target level isn't too large (> 25%)
                # focus on getting the flow to the desired rate
            # otherwise
            # adjust the flow based on the % level diff
            # and taper the amout of change based on how large the diff is
        pass

    def update_valve_timings(self):
        pass

    def run(self):
        self.logger.info("Running Cold Lob Monitor")
        while True:
            try:
                if time.time() >= self.timer:
                    self.collect_data()
                    self.log_data()
                    self.determine_level_trends()
                    # if we have passed the initial delay period then
                    # update the valves
                    if self.past_delay:
                        self.update_valve_timings()
                    else:
                        # otherwise, we want to update our delay timer
                        self.update_delay_bool()
                time.sleep(1)
            except KeyboardInterrupt:
                self.logger.warn("Shutting down!")
                sys.exit()
