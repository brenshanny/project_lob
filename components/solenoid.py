#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import threading
import logging

class ValveManager(object):
    def __init__(self, pins):
        self.logger = logging.getLogger("project_lob.components.valve_manager")
        self.logger.info("Initializing Valve Manager")
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.valve_controls = {}
        self.toggle_phase = "off"
        for pin in pins:
            self.valve_controls[pin] = ValveController(pin)

    def update_valve_timings(self, timings):
        self.logger.info("Updating valve timings")
        for timing in timings:
            thread = self.threads[timing["pin"]]
            thread.update_timing(timing["on"], timing["off"])

    def shutdown_threads(self):
        self.logger.info("Shutting down threads")
        for thread in self.threads:
            thread.shutdown = True
            thread.join()
        self.threads = []

    def start_threads(self):
        self.logger.info("Starting threads")
        if any([thread.isActive() for thread in self.threads]):
            self.shutdown_threads()
        for timing in self.valve_timings:
            pin = timing["pin"]
            self.threads[pin] = ValveThread(
                    self.valve_controls[pin], timing["on"], timing["off"]
                    )

    def toggle_valves(self):
        if self.toggle_phase == "off":
            self.logger.info("Toggling valves on")
            for pin in list(self.valve_controls.keys()):
                valve = self.valve_controls[pin]
                print("Toggling on valve: {}".format(valve.pin))
                valve.turn_on()
        else:
            self.logger.info("Toggling valves off")
            for pin in list(self.valve_controls.keys()):
                valve = self.valve_controls[pin]
                print("Toggling off valve: {}".format(valve.pin))
                valve.turn_off()

class ValveThread(threading.Thread):
    def __init__(self, controller, on_time, off_time):
        self.logger = logging.getLogger("project_lob.components.valve_thread")
        self.logger.info("Initializing Valve Thread for controller:"
                         " {}".format(controller.pin))
        threading.Thread.__init__(self)
        self.shutdown_needed = False
        self.valve_controller = controller
        self.update_timing(on_time, off_time)
        self.phase = "on"

    def shutdown(self):
        self.logging.info("Setting Thread {} for shutdown!".format(
            self.valve_controller.pin))
        self.shutdown_needed = True

    def update_timing(self, on, off):
        self.logger.info("Controller: {} Updating timings, on: {},"
                         " off: {}".format(self.valve_controller.pin, on, off))
        self.on_time = on
        self.off_time = off

    def on(self):
        self.logger.info("Toggling On for {} seconds, controller: {}".format(
            self.on_time, self.valve_controller.pin))
        self.valve_controller.turn_on()
        time.sleep(abs(self.on_time))
        self.phase = "off"

    def off(self):
        self.logger.info("Toggling Off for {} seconds, controller: {}".format(
            self.off_time, self.valve_controller.pin))
        self.valve_controller.turn_off()
        time.sleep(abs(self.off_time))
        self.phase = "on"

    def run(self):
        self.logger.info("Running Valve Thread for controler: {}".format(
            self.valve_controller.pin))
        while not self.shutdown:
            getattr(self, self.phase)()

class ValveController(object):
    def __init__(self, pin):
        self.logger = logging.getLogger(
            "project_lob.components.valve_controller")
        self.logger.info("Setting up Valve Controller for pin: {}".format(pin))
        self.pin = pin
        GPIO.setup(self.pin, GPIO.OUT)

    def turn_on(self):
        self.logger.info("Turning valve pin: {} ON".format(pin))
        GPIO.output(self.pin, GPIO.HIGH)

    def turn_off(self):
        self.logger.info("Turning valve pin: {} OFF".format(pin))
        GPIO.output(self.pin, GPIO.LOW)
