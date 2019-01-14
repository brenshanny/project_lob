from ..components.temperature.temperature_manager import TemperatureManager
from ..components.valves.valve_manager import ValveManager
from ..components.water_flow.water_flow_manager import WaterFlowManager
from ..components.water_level.water_level_manager import WaterLevelManager

import time

if __name__ == "__main__":
    water_level_pins = [
        {"pin": 0, "tank": 0, "min": 0, "max": 10},
        {"pin": 1, "tank": 1, "min": 0, "max": 10},
        {"pin": 2, "tank": 2, "min": 0, "max": 10},
        {"pin": 3, "tank": 3, "min": 0, "max": 10}
    ]
    water_flow_pins = [
        {"pin": 3, "tank": 0},
        {"pin": 17, "tank": 1},
        {"pin": 27, "tank": 2},
        {"pin": 22, "tank": 3}
    ]
    valve_pins = [
        {"pin": 14, "tank": 0},
        {"pin": 15, "tank": 1},
        {"pin": 23, "tank": 2},
        {"pin": 24, "tank": 3}
    ]
    temperature_codes = [
        {"device_id": "28-00000a299f32", "tank": 0},
        {"device_id": "28-00000a29db61", "tank": 1},
        {"device_id": "28-00000a2a2567", "tank": 2},
        {"device_id": "28-00000a2ad073", "tank": 3}
    ]

    tempManager = TemperatureManager(temperature_codes)
    valveManager = ValveManager(valve_pins)
    flowManager = WaterFlowManager(water_flow_pins, 5)
    levelManager = WaterLevelManager(water_level_pins, 1.1, .9)
    while True:
        print("----------------------")
        levelManager.print_levels()
        flowManager.print_flows()
        tempManager.print_temps()
        # valveManager.toggle_valves()
        time.sleep(5)
