from ..components.valves.valve_manager import ValveManager
from ..components.valves.valve_controller import ValveController
from ..components.water_flow.water_flow_manager import WaterFlowManager

import time
import sys

if __name__ == "__main__":
    water_flow_pins = [
        { "pin": 27, "tank": 0 }
    ]
    valve_pins = [
        { "pin": 23, "tank": 0 }
    ]

    valveManager = ValveManager(valve_pins)
    flowManager = WaterFlowManager(water_flow_pins, 5)
    # open valve
    # valveManager.valve_table[0].turn_off()
    valveManager.update_valve_timings([{ "tank": 0, "on": 1, "off": 0 }])
    valveManager.start_threads()
    while True:
        try:
            print("-----------------")
            flowManager.print_flows()
            time.sleep(5)
        except KeyboardInterrupt:
            valveManager.shutdown_threads()
            sys.exit()


