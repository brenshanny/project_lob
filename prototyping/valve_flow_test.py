from ..components.valves.valve_manager import ValveManger
from ..components.valves.valve_controller import ValveController
from ..components.water_flow.water_flow_manager import WaterFlowManager

import time

if __name__ == "__main__":
    water_flow_pins = [
        { "pin": 3, "tank": 0 }
    ]
    valve_pins = [
        { "pin": 14, "tank": 0 }
    ]

    valveManager = ValveManager(valve_pins)
    flowManager = WaterFlowManager(water_flow_pins, 5)
    # open valve
    valveManager.valve_table[0].turn_on()
    while True:
        print("-----------------")
        flowManager.print_flows()
        time.sleep(5)

