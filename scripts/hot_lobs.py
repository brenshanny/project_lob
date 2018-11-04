import json
import os
import sys
import time
from datetime import datetime as dt

from ..components.temperature import TemperatureManager as TempManager
from ..components.drive_service import DriveService

class HotLobMonitor(object):
    def __init__(self, config_path):
        with open(config_path) as config_file:
            self.config = json.load(config_file)
        self.temperature_probes = self.config['temperature_probes']
        self.interval = self.config['read_interval']
        self.temperature_manager = TempManager([
            p_id for p_id in list(self.config['temperature_probes'].keys())
        ])
        with open(os.environ[self.config["phone_numbers"]]) as phones:
            self.phone_numbers = json.load(phones)
        self.drive_service = DriveService(
            os.environ[self.config['sheet_key']],
            os.environ[self.config['cred_file']],
            os.environ[self.config['gmail_email']],
            os.environ[self.config['gmail_pwd']],
            self.phone_numbers
        )

    def tank_from_id(self, probe_id):
        return self.temperature_probes[probe_id]['tank']

    def reset_timer(self):
        self.timer = time.time() + self.interval

    def update_spreadsheet(self, tank, temp):
        today = dt.today()
        self.drive_service.add_entry([
            "{}/{}/{}".format(today.month, today.day, today.year),
            "{}:{}:{}".format(today.hour, today.minute, today.second),
            today.year,
            today.month,
            today.day,
            tank,
            temp
        ])

    def read_temps(self):
        print(time.strftime("%b %d, %Y - %H:%M", time.localtime(time.time())))
        temps = self.temperature_manager.read_monitors()
        for temp in temps:
            tank = self.tank_from_id(temp['device_id'])
            print("Tank: {}".format(tank))
            print(temp['readings'])
            self.update_spreadsheet(tank, temp['readings'][0])

    def run(self):
        self.reset_timer()
        print("Running Hot Lob Monitor")
        while True:
            try:
                if time.time() >= self.timer:
                    self.read_temps()
                    self.reset_timer()
                time.sleep(1)
            except KeyboardInterrupt:
                print('Shutting down...')
                sys.exit()

if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),
            'hot_lobs_config.json')
    hotLobs = HotLobMonitor(config_path)
    hotLobs.run()
