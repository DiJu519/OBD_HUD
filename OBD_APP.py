#!/usr/bin/env python

import obd_io
import serial
import platform
import obd_sensors
from datetime import datetime
import time
import signal
import os
import time
import urllib

from obd_utils import scanSerial

from simplejson import dumps as to_json
from simplejson import loads as from_json

from webgui import start_gtk_thread
from webgui import launch_browser
from webgui import synchronous_gtk_message
from webgui import asynchronous_gtk_message
from webgui import kill_gtk_thread

class Global(object):
    quit = False
    @classmethod
    def set_quit(cls, *args, **kwargs):
        cls.quit = True


class OBD_Capture():
    def __init__(self):
        self.port = None
        localtime = time.localtime(time.time())

    def connect(self):
        portnames = scanSerial()
        print portnames
        for port in portnames:
            self.port = obd_io.OBDPort(port, None, 2, 2)
            if(self.port.State == 0):
                self.port.close()
                self.port = None
            else:
                break

        if(self.port):
            print "Connected to "+self.port.port.name
            
    def is_connected(self):
        return self.port
        
    def capture_data(self):

        #Find supported sensors - by getting PIDs from OBD
        # its a string of binary 01010101010101 
        # 1 means the sensor is supported
        self.supp = self.port.sensor(0)[1]
        self.supportedSensorList = []
        self.unsupportedSensorList = []

        print "Supported!!!!! "

        print self.supp

        start_gtk_thread()

         # Create a proper file:// URL pointing to demo.xhtml:
        file = os.path.abspath('ui.xhtml')
        uri = 'file://' + urllib.pathname2url(file)
        browser, web_recv, web_send = \
            synchronous_gtk_message(launch_browser)(uri,
                                                quit_function=Global.set_quit)

        # loop through PIDs binary
        #for i in range(0, len(self.supp)):
        for i in range(0, 32):
            

            print "INDEX "
            print i
            if self.supp[i] == "1":
                # store index of sensor and sensor object
                self.supportedSensorList.append([i+1, obd_sensors.SENSORS[i+1]])
            else:
                self.unsupportedSensorList.append([i+1, obd_sensors.SENSORS[i+1]])
        
        for supportedSensor in self.supportedSensorList:
            print "supported sensor index = " + str(supportedSensor[0]) + " " + str(supportedSensor[1].shortname)        
        
        time.sleep(3)
        
        if(self.port is None):
            return None

        #Loop until Ctrl C is pressed        
        try:
            #while True:
            while not Global.quit:
                localtime = datetime.now()
                current_time = str(localtime.hour)+":"+str(localtime.minute)+":"+str(localtime.second)+"."+str(localtime.microsecond)
                log_string = current_time + "\n"
                results = {}
                for supportedSensor in self.supportedSensorList:
                    sensorIndex = supportedSensor[0]
                    (name, value, unit) = self.port.sensor(sensorIndex)
                    log_string += name + " = " + str(value) + " " + str(unit) + "\n"
                    
                    web_send('document.getElementById('+ "\"" + str(supportedSensor[1].shortname)+ "\""  ').innerHTML = %s' %
                     to_json('%s' % str(value)))
                
                print log_string
                print "FUCK"
                print name
                
                time.sleep(0.5)

        except KeyboardInterrupt:
            self.port.close()
            print("stopped")

    def my_quit_wrapper(fun):
        signal.signal(signal.SIGINT, Global.set_quit)
        def fun2(*args, **kwargs):
            try:
                x = fun(*args, **kwargs) # equivalent to "apply"
            finally:
                kill_gtk_thread()
                Global.set_quit()
            return x
        return fun2

if __name__ == "__main__":

    o = OBD_Capture()
    o.connect()

    time.sleep(3)
    if not o.is_connected():
        print "Not connected"
    else:
        o.capture_data()
            
