#!/usr/bin/env python

# Module that handles all of the I/O exchange through the OBDII port
import obd_io

# both the serial and platform modules were included in the program, but are un used in this module
#import serial
#import platform


import obd_sensors
from datetime import datetime
import time

from obd_utils import scanSerial

# Class to record data from the OBD port
class OBD_Recorder():

    # Constructor method for the OBD_Recorder class.
    # Arguments passed into the constructor are the
    # location of the log file and a list of items to be logged
    def __init__(self, path, log_items):

        # Initialize the instance variables for the method
        self.port = None
        self.sensorlist = []
        localtime = time.localtime(time.time())

        # Create and store the name of the file
        filename = path+"bike-"+str(localtime[0])+"-"+str(localtime[1])+"-"+str(localtime[2])+"-"+str(localtime[3])+"-"+str(localtime[4])+"-"+str(localtime[5])+".log"
        # Create the log file and open it as a writable file
        self.log_file = open(filename, "w", 128)
        # Write the header in the file
        self.log_file.write("Time,RPM,MPH,Throttle,Load,Gear\n");

        # Loop to build sensorlist
        for item in log_items:
            self.add_log_item(item)

        # Create and initialize instance variable to house the gear ratios
        self.gear_ratios = [34/13, 39/21, 36/23, 27/20, 26/21, 25/22]
        #log_formatter = logging.Formatter('%(asctime)s.%(msecs).03d,%(message)s', "%H:%M:%S")

    # Method to connect to the OBD port
    def connect(self):

        # Collect the list of all the open serial ports
        portnames = scanSerial()
        #portnames = ['COM10']
        print portnames

        # Loop through the list of port names
        for port in portnames:
            # Create instance of OBDPort
            # Not sure why the port is created twice, once OBD to USB dongle arrives,
            # will attempt to remove one and see if there is any difference in operation
            self.port = obd_io.OBDPort(port, None, 2, 2)
            self.port = obd_io.OBDPort(port, None, 2, 2)

            # Verify that the serial port is connected
            if(self.port.State == 0):
                # If the serial port is not connected, close the port
                # and set the instance varialbe to 'None'
                self.port.close()
                self.port = None
            # Else the serial port is connected break from the loop
            else:
                break

        # Verify the serial port is not 'None' if it is, print
        # verification to command line
        if(self.port):
            print "Connected to "+self.port.port.name

    # Method to return the name of the port that is currently open
    # in the case where there is no port open, the method will return 'None'
    def is_connected(self):
        return self.port

    # Method to add an item to the log
    def add_log_item(self, item):

        # Loop to increment through the total list of sensors
        for index, e in enumerate(obd_sensors.SENSORS):

            # Comparison between the user defined sensor list and the complete sensor list
            if(item == e.shortname):

                # Add the sensor's index to the
                self.sensorlist.append(index)
                print "Logging item: "+e.name
                break
            
     # Method to record data
    def record_data(self):

        # Verify that there is an open port, if there is no port available, return "None"
        if(self.port is None):
            return None

        # Print logging verification to the command line
        print "Logging started"

        # Loop to collect data for log
        while 1:
            localtime = datetime.now()                  # Collect the current local time

            # Build string for the time that will be placed in the log
            current_time = str(localtime.hour)+":"+str(localtime.minute)+":"+str(localtime.second)+"."+str(localtime.microsecond)

            # Add current_time to the log string
            # All other data to be logged will be parsed to the log string
            # Once all data has been added to the string, the results will be added to the CSV file
            log_string = current_time

            # Dictionary to house the results from the sensors
            results = {}

            # Loop to index through the list of user defined sensors
            for index in self.sensorlist:
                # Collect the sensor's name, current value and the units
                (name, value, unit) = self.port.sensor(index)

                # Parse the sensor's current value to the log_string
                log_string = log_string + ","+str(value)

                # Record the sensor's name, as the dict. key,  and value, as the dict.
                # value, in the results dictionary
                results[obd_sensors.SENSORS[index].shortname] = value;

            # Calculate the current gear using the sensor data recorded in
            # the results dictionary
            gear = self.calculate_gear(results["rpm"], results["speed"])

            # Parse the current gear onto the log_string
            log_string = log_string + "," + str(gear)

            # Parse the log_string into the log file
            self.log_file.write(log_string+"\n")

    # Method to calculate the current gear
    def calculate_gear(self, rpm, speed):
        # Verify that the current speed is not zero,
        # if the speed is zero, return a gear of zero
        if speed == "" or speed == 0:
            return 0
        # Verify that the engine RPM is not zero,
        # if the RPM is zero, return a gear of zero
        if rpm == "" or rpm == 0:
            return 0

        # Convert the measure to Rotations / Second
        rps = rpm/60

        # Calculate the speed in Meters / Second
        mps = (speed*1.609*1000)/3600

        primary_gear = 85/46 #street triple
        final_drive  = 47/16
        
        tyre_circumference = 1.978 #meters

        # Calculate the current ratio
        current_gear_ratio = (rps*tyre_circumference)/(mps*primary_gear*final_drive)
        
        print current_gear_ratio
        # Determine current gear
        gear = min((abs(current_gear_ratio - i), i) for i in self.gear_ratios)[1] 
        return gear




# User defined list of data items to collect
logitems = ["rpm", "speed", "throttle_pos", "load"]

# Create an instance of OBD_Recorder, passing in path and items arguments
o = OBD_Recorder('/home/pi/logs/', logitems)

# Connect the instance of OBD_Recorder to the serial port
o.connect()

# Verify the instance of OBD_Recorder is connected
if not o.is_connected():
    print "Not connected"

# Record data to the log file
o.record_data()
