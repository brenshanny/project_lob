import json
import os
import sys
import time
from datetime import datetime
import logging

from ..components.temperature import TemperatureManager
from ..components.logging_service import LoggingService
from ..utils.eventlogger import EventHandler

class HotLobMonitor(object):
    def __init__(self, config_path):
        self.logger = logging.getLogger('project_lob.hot_lob_monitor')
        self.logger.info("Initializing Hot Lob Monitor")
        with open(config_path) as config_file:
            self.logger.info("Loading Hot Lob config @ {}".format(config_path))
            self.config = json.load(config_file)["hot_lob"]
        self.event_logger = EventHandler(self.config['event_logger_filename'],
                                          name="hot_lob_data")
        self.temperature_probes = self.config['temperature_probes']
        self.set_interval(self.config['read_interval'])
        self.logger.info("Initializing Temperature Manger")
        self.temperature_manager = TemperatureManager([
            p_id for p_id in list(self.config['temperature_probes'].keys())
        ])
        self.logger.info("Loading phone numbers")
        with open(os.environ[self.config["phone_numbers"]]) as phones:
            self.phone_numbers = json.load(phones)
        self.logger.info("Initializing Logging Service")
        self.logging_service = LoggingService(
            os.environ[self.config['sheet_key']],
            os.environ[self.config['cred_file']],
            os.environ[self.config['gmail_email']],
            os.environ[self.config['gmail_pwd']],
            self.phone_numbers
        )

    def tank_from_id(self, probe_id):
        return self.temperature_probes[probe_id]['tank']

    def reset_timer(self):
        self.logger.info("Resetting timer!")
        self.timer = time.time() + self.interval

    def set_interval(self, val):
        self.logger.info("Setting interval: {}".format(val))
        self.interval = val

    def log_data(self, tank, temp):
        time = datetime.today()
        self.update_spreadsheet(tank, temp, time)
        self.event_logger.addEvent({
            "temperature_check": {
                "tank": tank,
                "temp": tmep
            },
            today.timestamp()
        })

    def update_spreadsheet(self, tank, temp, datetime_today = None):
        if not datetime_today:
            datetime_today = datetime.today()
        self.logger.info(
            "Updating spreadsheet for tank {}, with temp {}".format(
                tank, temp))
        self.logging_service.add_entry([
            "{}/{}/{}".format(datetime_today.month, datetime_today.day,
                              datetime_today.year),
            "{}:{}:{}".format(datetime_today.hour, datetime_today.minute,
                              datetime_today.second),
            datetime_today.year,
            datetime_today.month,
            datetime_today.day,
            tank,
            temp
        ])

    def read_temps(self):
        self.logger.info("Reading temps")
        temps = self.temperature_manager.read_monitors()
        for temp in temps:
            tank = self.tank_from_id(temp['device_id'])
            self.logger.debug("Tank: {}, temp: {}".format(tank, temp['data']))
            self.log_data(tank, temp['data'][0])

    def run(self):
        self.logger.info("Running Hot Lob Monitor")
        self.reset_timer()
        while True:
            try:
                if time.time() >= self.timer:
                    self.read_temps()
                    self.reset_timer()
                time.sleep(1)
            except KeyboardInterrupt:
                self.logger.warn("Shutting down!")
                sys.exit()
