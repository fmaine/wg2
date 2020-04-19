__author__ = "Francois Maine"
__copyright__ = "Copyright 2020, Preedom Partners"
__email__ = "fm@freedom-partners.com"

import time
import re
import json
import os

class ProgressMonitor():

    def __init__(self,name,log_dir=''):
        self._name = name
        self._info =''
        self._filename = log_dir+name+'.json'
        self._interval = 1
        self._progress = 0
        self._time_start=time.time()
        self._last_pub=self._time_start
        self._total = 0

    def reset(self,total):
        self._total = total
        self._progress = 0
        self._time_start=time.time()
        self._last_pub=self._time_start

    def info(self,text):
        self._info = text

    def set_progress(self,p):
        self._progress = p
        self.publish()

    def increment(self):
        self._progress += 1
        self.publish()

    def status(self):
        elapsed = time.time() - self._time_start
        if self._total > 0:
            percent = float(self._progress)/float(self._total)
        else:
            percent = 0
        return {
            'name' : self._name,
            'info' : self._info,
            'progress' : self._progress,
            'total' : self._total,
            'percent' : int(100*percent),
            'elapsed' : int(elapsed),
#            'eta' : eta,
        }

    def publish(self):
        if self._progress == self._total or time.time()-self._last_pub > self._interval :
            self._last_pub = time.time()
            with open(self._filename,'w') as file :
                json.dump(self.status(),file)

    def read(self):
        if os.path.isfile(self._filename):
            with open(self._filename) as file :
                return json.load(file)
        else:
            return self.status()
