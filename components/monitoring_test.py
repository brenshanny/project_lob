#!/usr/bin/python

# setup a test circuit with the following:
#     temp sensor:        pin 4
#     water flow sensor:  pin 2
#     water level sensor: MCP3008 pin 0
import time, os

from .temperature.temperature_monitor import TemperatureMonitor
from .water_flow.water_flow_monitor import WaterFlowMonitor
from .water_level.water_level_monitor import WaterLevelMonitor

if __name__ == "__main__":
    temp = TemperatureMonitor(2)
    flow = WaterFlowMonitor(2)
    level = WaterLevelMonitor(0)
    timer = time.time() + 10
    while True:
        try:
            if time.time() >= timer:
                [tC, tF] = temp.read_temp()
                [fL, fT] = flow.calc_flow(True)
                height = level.read_level()
                print('-------------------------')
                print('Temperature Celcius     -> ', tC)
                print('Temperature Ferinheight -> ', tF)
                print('Flow Liters/min         -> ', fL)
                print('Flow total liters       -> ', fT)
                print('Water Level             -> ', height)
                timer = time.time() + 10
            time.sleep(1)
        except KeyboardInterrupt:
            print("Shutting down...")
            flow.shut_down()
