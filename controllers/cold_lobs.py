from ..components.temperature import TemperatureManager
from ..components.solenoid import ValveManager
from ..components.water_flow import WaterFlowManager
from ..components.water_level import WaterLevelManager
from ..utils.eventlogger import EventHandler

import logging
import os
import json
import time
import sys
from datetime import datetime

class ColdLobMonitor(object):
    def __init__(self, config_path):
        self.logger = logging.getLogger("project_lob.cold_lob_monitor")
        self.logger.info("Initializing Cold Lob Monitor")
        with open(config_path) as config_file:
            self.logger.info("Loading Cold Lob config @ {}".format(config_path))
            self.config = json.load(config_file)["cold_lob"]
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
            list(self.config["water_level"]["monitors"]),
            self.config["water_level"]["min_threshold"],
            self.config["water_level"]["max_threshold"]
        )
        self.logger.info("Initializing Water Flow Manager")
        self.flow_manager = WaterFlowManager(
            list(self.config["water_flow"]["meters"]), self.interval
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
            "4": {"level_lock": None, "target_flow": None },
            "5": {"level_lock": None, "target_flow": None },
            "6": {"level_lock": None, "target_flow": None },
            "7": {"level_lock": None, "target_flow": None }
        }
        for monitor in self.level_manager.monitors:
            self.tank_table[str(monitor.tank)]["level_monitor"] = monitor
        for monitor in self.flow_manager.monitors:
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
        self.logger.info("Collecting flow readings")
        self.event_logger.add_event({
            "flow_check": self.flow_manager.read_monitors()
        })

    def update_level_reading(self):
        self.logger.info("Collecting level readings")
        self.event_logger.add_event({
            "level_check": self.level_manager.read_monitors()
        })

    def update_temp_reading(self):
        self.logger.info("Collecting temp readings")
        self.event_logger.add_event({
            "temperature_check": self.temp_manager.read_monitors()
        })

    def update_delay_bool(self):
        self.logger.info("Updating the delay boolean")
        self.past_delay = time.time() >= self.delay

    def collect_data(self):
        self.logger.info("Collecting data...")
        self.update_flow_reading()
        self.update_level_reading()
        self.update_temp_reading()
        self.logger.info("Successfully collected data...")

    def log_data_to_services(self):
        self.logger.info("Logging data to services!")
        today = datetime.today()
        dt = "{}/{}/{}".format(today.month, today.day, today.year)
        ts = "{}:{}:{}".format(today.hour, today.minute, today.second)
        for tank_id, tank in list(self.tank_table.items()):
            self.logger.info(
                "Updating spreadsheet for tank: {}".format(tank_id))
            temp = (tank["temp_monitor"].last_sample() if "temp_monitor"
                in tank else None)
            flow = (tank["flow_monitor"].last_sample() if "flow_monitor"
                in tank else None)
            level = (tank["level_monitor"].last_sample() if "level_monitor"
                in tank else None)
            norm_level = tank["level_monitor"].target_offset() if level else None
            min_level = tank["level_monitor"].min_level if level else None
            level_alert = tank["level_monitor"].check_alert() if level else None
            valve_thread = self.valve_manager.get_thread_by_tank_id(tank_id)
            on_time = valve_thread.on_time if valve_thread else None
            off_time = valve_thread.off_time if valve_thread else None
            self.logging_service.add_entry([
                dt, ts, today.year, today.month, today.day, tank_id,
                temp, flow, level, norm_level, on_time, off_time,
            ])
            if level_alert:
                self.logging.info(level_alert)
                self.logging_service.notify_all(level_alert)
        self.logger.info("Done logging to services!!")

    def determine_level_trends(self):
        # likely some linear regression here
        # but is it needed?
          # i guess it would be nice to adjust the magnitude of a change
          # to flow rate based on the rate of level change
        pass

    def update_valve_timings(self):
        for tank_id in list(self.tank_table.keys()):
            if tank_id is not "7":
                self.update_downstream_tank(tank_id)
            else:
                self.update_header_tank()

    def update_header_tank(self, tank_id):
        pass

    def update_downstream_tank(self, tank_id):
        self.logger.info("Updating flow rate for tank: {}".format(tank_id))
        tank = self.tank_table[tank_id]
        level = tank["level_monitor"].get_average()
        flow = tank["flow_monitor"].get_average()
        level_offset = tank["level_monitor"].target_offset()
        level_trend = tank["level_monitor"].level_trend()
        flow_offset = tank["flow_monitor"].target_offset()
        if not tank["level_lock"]:
            if level_offset > 0.1 and level_trend > 0:
                # the level is high and its trending up
                # we want to slow down the flow into the tank
                tank["level_lock"] = level
                # tank["target_flow"] = 
                pass
            elif level_offset < -0.1 and level_trend < 0:
                # the level is low and its trending down
                # we want to speed up the flow into the tank
                tank["level_lock"] = level
                pass
            else:
                # the tank is in the sweet spot (-0.1 <-> 0.1)
                pass
        else:
            if abs(level - tank["level_lock"]) >= (tank["level_lock"] * 0.1):
                # the tank is draining/filling quickly so we should update the flow now
                pass
            elif abs(flow - tank["target_flow"]) <= (tank["target_flow"] * 0.05):
                # the flow is close to the target flow, we should reset the locks/targets
                # and redo this method
                tank["level_lock"] = None
                tank["target_flow"] = None
                self.update_downstream_tank(tank_id)
            else:
                # the level is not moving too much, but we haven't reached our target flow
                # so we shouldn't do anything just yet
                pass

            # take a measurement
            # if the past level/flow rate targets aren't set
            # -> then start fresh
                # determine the flow necessary (likely a small % up or down from current flow rate)
                # retain the level at this moment
            # otherwise
            # if the flow rate is within 5% of the target rate and the level isn't 10% +/- the last level
                # then check the level and its relation to the last level
                # if not moving in the correct direction
                    # update the flow target,
            # retain the level at this moment
            # on the next iteration


        pass

    def update_valve_timings(self):
        pass

    def run(self):
        self.logger.info("Running Cold Lob Monitor")
        self.reset_timer()
        while True:
            try:
                if time.time() >= self.timer:
                    self.logger.info("Cold lob update started")
                    self.collect_data()
                    self.log_data_to_services()
                    if self.past_delay:
                        self.update_valve_timings()
                    else:
                        # otherwise, we want to update our delay timer
                        self.update_delay_bool()
                    self.reset_timer()
                    self.logger.info("Finished cold lob update")
                time.sleep(1)
            except KeyboardInterrupt:
                self.logger.warn("Shutting down!")
                sys.exit()
