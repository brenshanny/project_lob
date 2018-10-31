import json
import os
import sys
import time

from ..components.temperature import TemperatureManager as TempManager

class HotLobMonitor(object):
    def __init__(self, config_path):
        with open(config_path) as config:
            self.temperature_probes = config['temperature_probes']
            self.interval = config['read_interval']
        self.temperature_manager = TempManager([
            p_id for p_id in list(self.config['temperature_probes'].keys())
        ])

    def tank_from_id(self, probe_id):
        return self.temperature_probes[probe_id]['tank']

    def reset_timer(self):
        self.timer = time.time() + self.interval

    def read_temps(self):
        print(time.strftime("%b %d, %Y - %H:%M", time.localtime(time.time())))
        temps = self.temperature_manager.read_temps()
        for temp in temps:
            print("Tank: {}".format(self.tank_from_id(temp['device_id'])))
            print(temp['readings'])

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
