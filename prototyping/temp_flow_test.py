import os
import glob
import time
import sys

from water_flow import WaterFlowMonitor
from temperature_probe import TemperatureMonitor

# Create monitor instances
FlowMonitor = WaterFlowMonitor()
TempMonitor = TemperatureMonitor()

print("Running temperature probe and water flow monitor")
timer = time.time() + 10
while True:
    try:
        if time.time() >= timer:
            FlowMonitor.calc_flow()
            FlowMonitor.reset_rate_count()
            timer = time.time() + 10
            print(TempMonitor.read_temp())
        time.sleep(1)
    except KeyboardInterrupt:
        FlowMonitor.shut_down()
        sys.exit()
