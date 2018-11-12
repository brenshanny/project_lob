import json
import os
import sys
import time
from datetime import datetime
import logging

from ..components.temperature import TemperatureManager
from ..components.lobster_log import LoggingService

class HotLobMonitor(object):
    def __init__(self, config_path):
        self.logger = logger.getLogger('project_lob.hot_lob_monitor')
        self.logger.info("Initializing Hot Lob Monitor")
        with open(config_path) as config_file:
            self.logger.info("Loading Hot Lob config @ {}".format(config_path))
            self.config = json.load(config_file)
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

    def update_spreadsheet(self, tank, temp):
        self.logger.info(
            "Updating spreadsheet for tank {}, with temp {}".format(
                tank, temp))
        today = datetime.today()
        self.logging_service.add_entry([
            "{}/{}/{}".format(today.month, today.day, today.year),
            "{}:{}:{}".format(today.hour, today.minute, today.second),
            today.year,
            today.month,
            today.day,
            tank,
            temp
        ])

    def read_temps(self):
        self.logger.info("Reading temps")
        temps = self.temperature_manager.read_monitors()
        for temp in temps:
            tank = self.tank_from_id(temp['device_id'])
            self.logger.debug("Tank: {}, temp: {}".format(tank, temp['data']))
            self.update_spreadsheet(tank, temp['data'][0])

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
