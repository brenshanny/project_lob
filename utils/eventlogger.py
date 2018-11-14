#!/usr/bin/env python

# Originally written by Brett Graham
# https://github.com/braingram

import atexit
import os
import time
import pickle


class EventHandler(object):
    def __init__(
            self, output_directory, entries_per_file=18000,
            name=None, max_time=1800):
        if name is None:
            self.name = ""
        else:
            self.name = name
        self.data = None
        self.logfilename = None
        self.max_entries = entries_per_file
        self.max_time = max_time
        self.output_directory = output_directory
        atexit.register(self.end_log)

    @property
    def output_directory(self):
        return self._output_directory

    @output_directory.setter
    def output_directory(self, directory):
        if self.data is not None:
            self.end_log()
        self._output_directory = os.path.abspath(
            os.path.expanduser(directory))

    def start_log(self, timestamp):
        self.data = {}
        self.start_time = time.time()
        self.logfilename = os.path.join(
            self.output_directory,
            '{}_{}.p'.format(self.name, int(timestamp)))

    def add_event(self, event, timestamp=None):
        t = time.time()
        if timestamp is None:
            timestamp = t
        if self.data is None:
            self.start_log(t)
        if (
                len(self.data) > self.max_entries or
                t - self.start_time > self.max_time):
            self.end_log()
            self.add_event(event, timestamp)
        else:
            if timestamp in self.data:
                self.data[timestamp].update(event)
            else:
                self.data[timestamp] = event

    def end_log(self):
        if self.data is None:
            return
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        with open(self.logfilename, 'wb') as f:
            pickle.dump(self.data, f, pickle.HIGHEST_PROTOCOL)
        self.data = None
        self.logfilename = None

    def log(self, **kwargs):
        ts = kwargs.pop('timestamp', None)
        self.add_event(kwargs, ts)

    def __del__(self):
        self.end_log()
