#!/usr/bin/env python

# Module that handles all of the I/O exchange through the OBDII port
import obd_io
import platform
import obd_sensors
from datetime import datetime
import time
import os

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
        filename = path +"Car_Data_"+str(localtime[0])+"_"+str(localtime[1])+"_"+str(localtime[2])+"_"+str(localtime[3])+"_"+str(localtime[4])+"_"+str(localtime[5])+".log"
        # Create the log file and open it as a writable file
        self.log_file = open(filename, "w")
        # Write the header in the log file
        for item in log_items:
            self.log_file.write(item + ",")
        # Write new line character after list of items
        self.log_file.write("\n")

        # Loop to build sensorlist
        for item in log_items:
            self.add_log_item(item)

        # Connect the instance of OBD_Recorder to the serial port
        self.connect()
        # Verify the instance of OBD_Recorder is connected
        if not self.is_connected():
            print "Not connected"
        # Record data to the log file
        self.record_data()



    # Method to connect to the OBD port
    def connect(self):
        # Collect the list of all the open serial ports
        portnames = scanSerial()
        print portnames
        # Loop through the list of port names
        for port in portnames:
            # Create instance of OBDPort
            self.port = obd_io.OBDPort(port, None, 2, 2)
            # Verify that the serial port is connected
            if(self.port.State == 0):
                # If the serial port is not connected, close the port
                self.port.close()
                self.port = None
            # Else the serial port is connected break from the loop
            else:
                break
        # Verify the serial port is connected
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
                print "Logging item: " + e.name
                break

     # Method to record data
    def record_data(self):
        # Verify that there is an open port, if there is no port available, return "None"
        if(self.port is None):
            return None
        print "Logging started"
        # Loop to collect data for log
        while 1:
            localtime = datetime.now()
            # Build string for the time that will be placed in the log
            current_time = str(localtime.hour) + ":" + str(localtime.minute) + ":" + str(localtime.second) + "." + \
                           str(localtime.microsecond)
            # Add current_time to the log string
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
           # gear = self.calculate_gear(results["rpm"], results["speed"])

            # Parse the current gear onto the log_string
            log_string = log_string + "," #+ str(gear)

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

"""
# List of sensors that are able to be read through the OBD
SENSORS = [
    Sensor("pids"                  , "          Supported PIDs", "0100", hex_to_bitstring ,""       ),
    Sensor("dtc_status"            , "Status Since DTC Cleared", "0101", dtc_decrypt      ,""       ),
    Sensor("dtc_ff"                , "DTC Causing Freeze Frame", "0102", cpass            ,""       ),
    Sensor("fuel_status"           , "      Fuel System Status", "0103", cpass            ,""       ),
    Sensor("load"                  , "   Calculated Load Value", "0104", percent_scale    ,"%"      ),
    Sensor("temp"                  , "     Coolant Temperature", "0105", temp             ,"C"      ),
    Sensor("short_term_fuel_trim_1", "    Short Term Fuel Trim", "0106", fuel_trim_percent,"%"      ),
    Sensor("long_term_fuel_trim_1" , "     Long Term Fuel Trim", "0107", fuel_trim_percent,"%"      ),
    Sensor("short_term_fuel_trim_2", "    Short Term Fuel Trim", "0108", fuel_trim_percent,"%"      ),
    Sensor("long_term_fuel_trim_2" , "     Long Term Fuel Trim", "0109", fuel_trim_percent,"%"      ),
    Sensor("fuel_pressure"         , "      Fuel Rail Pressure", "010A", fuel_pres        ,"kPa"    ),
    Sensor("manifold_pressure"     , "Intake Manifold Pressure", "010B", intake_m_pres    ,"psi"    ),
    Sensor("rpm"                   , "              Engine RPM", "010C", rpm              ,"RPM"    ),
    Sensor("speed"                 , "           Vehicle Speed", "010D", speed            ,"MPH"    ),
    Sensor("timing_advance"        , "          Timing Advance", "010E", timing_advance   ,"degrees"),
    Sensor("intake_air_temp"       , "         Intake Air Temp", "010F", temp             ,"C"      ),
    Sensor("maf"                   , "     Air Flow Rate (MAF)", "0110", maf              ,"lb/min" ),
    Sensor("throttle_pos"          , "       Throttle Position", "0111", throttle_pos     ,"%"      ),
    Sensor("secondary_air_status"  , "    Secondary Air Status", "0112", cpass            ,""       ),
    Sensor("o2_sensor_positions"   , "  Location of O2 sensors", "0113", sensor_pos       ,""       ),
    Sensor("o211"                  , "        O2 Sensor: 1 - 1", "0114", fuel_trim_percent,"%"      ),
    Sensor("o212"                  , "        O2 Sensor: 1 - 2", "0115", fuel_trim_percent,"%"      ),
    Sensor("o213"                  , "        O2 Sensor: 1 - 3", "0116", fuel_trim_percent,"%"      ),
    Sensor("o214"                  , "        O2 Sensor: 1 - 4", "0117", fuel_trim_percent,"%"      ),
    Sensor("o221"                  , "        O2 Sensor: 2 - 1", "0118", fuel_trim_percent,"%"      ),
    Sensor("o222"                  , "        O2 Sensor: 2 - 2", "0119", fuel_trim_percent,"%"      ),
    Sensor("o223"                  , "        O2 Sensor: 2 - 3", "011A", fuel_trim_percent,"%"      ),
    Sensor("o224"                  , "        O2 Sensor: 2 - 4", "011B", fuel_trim_percent,"%"      ),
    Sensor("obd_standard"          , "         OBD Designation", "011C", compliance       ,""       ),
    Sensor("o2_sensor_position_b"  ,"  Location of O2 sensors" , "011D", cpass            ,""       ),
    Sensor("aux_input"             , "        Aux input status", "011E", pto_status       ,"bool"   ),
    Sensor("engine_time"           , " Time Since Engine Start", "011F", sec_to_min       ,"min"    ),
    Sensor("engine_mil_time"       , "  Engine Run with MIL on", "014D", sec_to_min       ,"min"    ),
    ]
    """


# User defined list of data items to collect
logitems = ["temp", "rpm", "speed", "throttle_pos", "engine_time"]

# Path to storage location on RPi
if(platform.linux_distribution() != 0):
    path = '/home/pi/OBD_Data/'
# Path to the storage location on OSx
if(platform.mac_ver() != 0):
    path = '/Users/' + os.getlogin() + '/Car_Data/'

if(not os.path.exists(path)):
    os.mkdir(path)


# Create an instance of OBD_Recorder, passing in path and items arguments
o = OBD_Recorder(path, logitems)
