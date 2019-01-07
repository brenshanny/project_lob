#!/usr/bin/python

import time
import threading
import logging

class ValveThread(threading.Thread):
    def __init__(self, controller, on_time, off_time):
        self.logger = logging.getLogger("project_lob.components.valve_thread")
        self.logger.info("Initializing Valve Thread for tank controller:"
                         " {}".format(controller.tank))
        threading.Thread.__init__(self)
        self.shutdown_needed = False
        self.valve_controller = controller
        self.update_timing(on_time, off_time)
        self.phase = "on"

    def shutdown(self):
        self.logging.info("Setting Thread for tank {} for shutdown!".format(
            self.valve_controller.tank))
        self.shutdown_needed = True

    def update_timing(self, on, off):
        self.logger.info("Controller: {} Updating timings, on: {},"
                         " off: {}".format(self.valve_controller.tank, on, off))
        self.on_time = on
        self.off_time = off

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
