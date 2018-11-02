#!/usr/bin/python

import RPi.GPIO as GPIO
import time
import threading

class ValveManager(object):
    def __init__(self, pins):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.valve_controls = {}
        self.toggle_phase = "off"
        for pin in pins:
            self.valve_controls[pin] = ValveController(pin)

    def update_valve_timings(self, timings):
        for timing in timings:
            thread = self.threads[timing["pin"]]
            thread.update_timing(timing["on"], timing["off"])

    def shutdown_threads(self):
        for thread in self.threads:
            thread.shutdown = True
            thread.join()
        self.threads = []

    def start_threads(self):
        if any([thread.isActive() for thread in self.threads]):
            self.shutdown_threads()
        for timing in self.valve_timings:
            pin = timing["pin"]
            self.threads[pin] = ValveThread(
                    self.valve_controls[pin], timing["on"], timing["off"]
                    )

    def toggle_valves(self):
        if self.toggle_phase == "off":
            for pin in list(self.valve_controls.keys()):
                valve = self.valve_controls[pin]
                print("Toggling on valve: {}".format(valve.control_pin))
                valve.turn_on()
        else:
            for pin in list(self.valve_controls.keys()):
                valve = self.valve_controls[pin]
                print("Toggling off valve: {}".format(valve.control_pin))
                valve.turn_off()

class ValveThread(threading.Thread):
    def __init__(self, controller, on_time, off_time):
        threading.Thread.__init__(self)
        self.shutdown = False
        self.valve_controller = controller
        self.off_time = off_time
        self.on_time = on_time
        self.phase = "on"

    def shutdown(self):
        self.shutdown = True

    def update_timing(self, on, off):
        self.on_time = on
        self.off_time = off

    def on(self):
        print("Toggling On for {} :: pin: {}".format(self.on_time, self.valve_controller))
        self.valve_controller.turn_on()
        time.sleep(abs(self.on_time))
        self.phase = "off"

    def off(self):
        print("Toggling Off for {} :: pin: {}".format(self.off_time, self.valve_controller))
        self.valve_controller.turn_off()
        time.sleep(abs(self.off_time))
        self.phase = "on"

    def run(self):
        while not self.shutdown:
            getattr(self, self.phase)()

class ValveController(object):
    def __init__(self, pin):
        self.control_pin = pin
        GPIO.setup(self.control_pin, GPIO.OUT)

    def turn_on(self):
        GPIO.output(self.control_pin, GPIO.HIGH)

    def turn_off(self):
        GPIO.output(self.control_pin, GPIO.LOW)
