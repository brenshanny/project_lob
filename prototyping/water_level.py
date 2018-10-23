#!/usr/bin/python

import spidev
import time

delay = 0.5
ldr_channel = 0

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1350000

def read(adcnum):
    if adcnum > 7 or adcnum < 0:
        return -1
    r = spi.xfer2([1, 8 + adcnum << 4, 0])
    data = ((r[1] & 3) << 8) + r[2]
    return data

while True:
    ldr_value = read(ldr_channel)
    ohms = round(((ldr_value * 3300) / 1024),0)
    print("----------------------------")
    print("Water Level: {}".format(ldr_value))
    time.sleep(delay)
