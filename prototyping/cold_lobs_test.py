from ..components.temperature import TemperatureManager
from ..components.solenoid import ValveManager
from ..components.water_flow import WaterFlowManager
from ..components.water_level import WaterLevelManager

import time

if __name__ == "__main__":
    water_level_pin = [0, 1, 2, 3]
    water_flow_pins = [3, 17, 27, 22]
    valve_pins = [14, 15, 23, 24]
    temperature_codes = ["28-00000a299f32", "28-00000a29db61", "28-00000a2a2567", "28-00000a2ad073"]

    temperatureManager = TemperatureManager(temperature_codes)
    valveManager = ValveManager(valve_pins)
    flowManager = WaterFlowManager(water_flow_pins)
    levelManager = WaterLevelManager(water_level_pins)
    while True:
        print("----------------------")
        levelManager.print_levels()
        flowManager.print_flows()
        tempManager.print_temps()
        valveManager.toggle_valves()
        sleep(5)
