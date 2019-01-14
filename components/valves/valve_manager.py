#!/usr/bin/python

import RPi.GPIO as GPIO
import logging

from .valve_controller import ValveController
from .valve_thread import ValveThread

class ValveManager(object):
    def __init__(self, config):
        self.logger = logging.getLogger("project_lob.components.valve_manager")
        self.logger.info("Initializing Valve Manager")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.controllers = [
            ValveController(cfg["pin"], cfg["tank"]) for cfg in config
        ]
        self.toggle_phase = "off"
        self.valve_table = {}
        self.threads = {}
        for controller in self.controllers:
            self.valve_table[controller.tank] = controller

    def update_valve_timings(self, timings):
        self.logger.info("Updating valve timings")
        self.valve_timings = timings
        for timing in timings:
            if timing["tank"] in self.threads:
                thread = self.threads[timing["tank"]]
                thread.update_timing(timing["on"], timing["off"])

    def shutdown_threads(self):
        self.logger.info("Shutting down threads")
        for thread in self.threads.values():
            thread.shutdown = True
            thread.join()
        self.threads = {}

    def start_threads(self):
        self.logger.info("Starting threads")
        if any([thread.isActive() for thread in self.threads.values()]):
            self.shutdown_threads()
        for timing in self.valve_timings:
            tank  = timing["tank"]
            self.threads[tank] = ValveThread(
                self.valve_table[tank], timing["on"], timing["off"]
            )
            self.threads[tank].start()

    def get_thread_by_tank_id(self, tank):
        if tank in self.threads:
            return self.threads[tank]
        else:
            return None

    def toggle_valves(self):
        if self.toggle_phase == "off":
            self.logger.info("Toggling valves on")
            self.toggle_phase = "on"
            for valve in self.valve_table.values():
                print("Toggling on valve: {}".format(valve.tank))
                valve.turn_on()
        else:
            self.logger.info("Toggling valves off")
            self.toggle_phase = "off"
            for valve in self.valve_table.values():
                print("Toggling off valve: {}".format(valve.tank))
                valve.turn_off()

