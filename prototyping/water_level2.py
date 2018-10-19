#!/usr/bin/python

import spidev
import time

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz = 1350000

def read_spi(channel):
    spidata = spi.xfer2([1,(8+channel)<<4,0])
    print("Raw ADC:      {}".format(spidata))
    data = ((spidata[1] & 3) << 8) + spidata[2]
    return data

while True:
    channeldata = read_spi(0)
    voltage = round(((channeldata * 3300) / 1024),0)
    temperature = ((voltage - 500) / 10)
    print("Data (dec)    {}".format(channeldata))
    print("Data (bin)    {}".format(('{0:010b}'.format(channeldata))))
    print("Voltage (mV): {}".format(voltage))
    print("Temperature:  {} degC".format(temperature))
    print("-----------------")
    time.sleep(1)
