#!/usr/bin/env python

import RPi.GPIO as GPIO
import time, sys

class WaterFlowMonitor(object):
    def __init__(self):
        self.flow_sensor_pin = 17
        self.total_count = 0
        self.rate_count = 0
        self.timer = 0
        self.min_count = 0
        self.constant = 0.10
        # Setup GPIO
        GPIO.setMode(GPIO.BCM)
        GPIO.setup(self.flow_sensor_pin, GPIO.in, pull_up_down = GPIO.PUD_UP)
        GPIO.add_event_detect(
                self.flow_sensor_pin,
                GPIO.FALLING,
                callback=self.countPulse
                )

    def countPulse():
        self.total_count += 1
        self.rate_count += 1

    def calcFlow():
        print('Liters/min -> ', round(self.rate_count * self.constant, 4))
        print('Total Liters -> ', round(self.total_count * self.constant, 4))
    
    def run():
        self.timer = time.time() + 10
        print("Running WaterFlowMonitor")
        while True:
            try:
                if time.time() >= self.timer:
                    self.min_count += 1
                    self.calcFlow()
                    self.rate_count = 0
                    self.timer = time.time() + 10
                time.sleep(1)
            except KeyboardInterrupt:
                print 'Shutting down...'
                GPIO.cleanup()
                sys.exit()

if __name__ == "__main__":
    waterFlow = WaterFlowMonitor()
    waterFlow.run()
