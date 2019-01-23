from ..components.temperature.temperature_manager import TemperatureManager
from ..components.valves.valve_manager import ValveManager
from ..components.water_flow.water_flow_manager import WaterFlowManager
from ..components.water_level.water_level_manager import WaterLevelManager
from ..components.logging_service import LoggingService
from ..utils.eventlogger import EventHandler

import logging
import os
import json
import time, sys
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
        with open(os.environ[self.config["phone_numbers"]]) as phones:
            self.phone_numbers = json.load(phones)
        self.logging_service = LoggingService(
            os.environ[self.config["sheet_key"]],
            os.environ[self.config["cred_file"]],
            os.environ[self.config["gmail_email"]],
            os.environ[self.config["gmail_pwd"]],
            self.phone_numbers,
        )
        # create a lookup table by tank
        self.create_tank_lookup_dict()

    def create_tank_lookup_dict(self):
        self.tank_table = {
            "4": {"last_offset": None, "flow_rate_warning": False},
            "5": {"last_offset": None, "flow_rate_warning": False},
            "6": {"last_offset": None, "flow_rate_warning": False},
            "7": {"last_offset": None, "flow_rate_warning": False}
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
            valve_thread = None # valve_thread = self.valve_manager.get_thread_by_tank_id(tank_id)
            on_time = "on_time_here" # valve_thread.on_time if valve_thread else None
            off_time = "off_time_here" # valve_thread.off_time if valve_thread else None
            self.logging_service.add_entry([
                dt, ts, today.year, today.month, today.day, tank_id,
                temp, flow, level, norm_level, on_time, off_time,
            ])
            if level_alert:
                self.logger.info(level_alert)
                self.logging_service.notify_all(level_alert)
        self.logger.info("Done logging to services!!")

    def update_downstream_tank(self, tank_id):
        self.logger.info("Assessing tank level: {}".format(tank_id))
        tank = self.tank_table[tank_id]
        # read current rates
        level = tank["level_monitor"].get_average()
        flow_rate = tank["flow_monitor"].flow_index
        offset = tank["level_monitor"].raw_offset()
        # pull in last readings
        last_offset = tank["last_offset"]
        flow_warning = tank["flow_rate_warning"]
        # we'll need to populate the initial readings
        if last_offset is None:
            tank["last_offset"] = offset
            return
        if abs(last_offset) < abs(offset):
            # the error is increasing, we'll want to modify the flow rate
            if offset >= 0:
                if flow_rate == 0:
                    if flow_warning:
                        # theres an issue, we're trying to slow down too much
                    else:
                        tank["flow_rate_warning"] = True
                else:
                    # slow down
                    tank["valve"].slow_down()
            else:
                if flow_rate == 9:
                    if flow_warning:
                        # theres an issue, we're trying to speed up too much
                    else:
                        tank["flow_rate_warning"] = True
                else:
                    # speed up
                    tank["valve"].speed_up()
        tank["last_offset"] = offset

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
                        pass
                        # self.update_valve_timings()
                    else:
                        # otherwise, we want to update our delay timer
                        self.update_delay_bool()
                    self.reset_timer()
                    self.logger.info("Finished cold lob update")
                time.sleep(1)
            except KeyboardInterrupt:
                self.logger.warn("Shutting down!")
                sys.exit()
