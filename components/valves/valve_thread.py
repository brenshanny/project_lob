#!/usr/bin/python

import time
import threading
import logging

class ValveThread(threading.Thread):
    def __init__(self, controller, starting_flow = 4):
        self.logger = logging.getLogger("project_lob.components.valve_thread")
        self.logger.info("Initializing Valve Thread for tank controller:"
                         " {}".format(controller.tank))
        threading.Thread.__init__(self)
        self.shutdown_needed = False
        self.valve_controller = controller
        self.flow_index = starting_flow
        self.phase = "on"

    def shutdown(self):
        self.logging.info("Setting Thread for tank {} for shutdown!".format(
            self.valve_controller.tank))
        self.shutdown_needed = True

    def flow_rates(self):
        return [
            {'on': 1, 'off': 5},
            {'on': 1, 'off': 4},
            {'on': 1, 'off': 3},
            {'on': 1, 'off': 2},
            {'on': 1, 'off': 1},
            {'on': 2, 'off': 1},
            {'on': 3, 'off': 1},
            {'on': 4, 'off': 1},
            {'on': 5, 'off': 1},
            {'on': 5, 'off': 0}
        ]

    def on_time(self):
        return self.flow_rates[self.flow_index]["on"]

    def off_time(self):
        return self.flow_rates[self.flow_index]["off"]

    def speed_up(self):
        if self.flow_index < 9:
            self.flow_index += 1
            self.logger.info("Controller: {} speeding up, on: {},"
                             " off: {}".format(
                                 self.valve_controller.tank,
                                 self.on_time,
                                 self.off_time))

    def slow_down(self):
        if self.flow_index > 1:
            self.flow_index -= 1
            self.logger.info("Controller: {} slowing down, on: {},"
                             " off: {}".format(
                                 self.valve_controller.tank,
                                 self.on_time,
                                 self.off_time))

    def update_flow(self, index):
        if 0 < index > 9:
            return
        self.flow_index = index
        self.logger.info("Controller: {} updating flow rate, on: {},"
                         " off: {}".format(
                             self.valve_controller.tank,
                             self.on_time,
                             self.off_time))

    def on(self):
        self.logger.info("Toggling On for {} seconds, controller: {}".format(
            self.on_time, self.valve_controller.tank))
        self.valve_controller.turn_on()
        time.sleep(abs(self.on_time))
        self.phase = "off"

    def off(self):
        self.logger.info("Toggling Off for {} seconds, controller: {}".format(
            self.off_time, self.valve_controller.tank))
        self.valve_controller.turn_off()
        time.sleep(abs(self.off_time))
        self.phase = "on"

    def run(self):
        self.logger.info("Running Valve Thread for controler: {}".format(
            self.valve_controller.tank))
        while not self.shutdown:
            getattr(self, self.phase)()
