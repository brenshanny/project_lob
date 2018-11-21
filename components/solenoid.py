#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import threading
import logging

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
        for controller in self.controllers:
            self.valve_table[controller.tank] = controller

    def update_valve_timings(self, timings):
        self.logger.info("Updating valve timings")
        for timing in timings:
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

class ValveController(object):
    def __init__(self, pin, tank):
        self.logger = logging.getLogger(
            "project_lob.components.valve_controller")
        self.logger.info("Setting up Valve Controller for tank: {}".format(tank))
        self.pin = pin
        self.tank = tank
        GPIO.setup(self.pin, GPIO.OUT)

    def turn_on(self):
        self.logger.info("Turning valve tank: {} ON".format(self.tank))
        GPIO.output(self.pin, GPIO.HIGH)

    def turn_off(self):
        self.logger.info("Turning valve tank: {} OFF".format(self.tank))
        GPIO.output(self.pin, GPIO.LOW)
