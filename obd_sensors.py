 #!/usr/bin/env python
###########################################################################
# obd_sensors.py
#
# Copyright 2004 Donour Sizemore (donour@uchicago.edu)
# Copyright 2009 Secons Ltd. (www.obdtester.com)
#
# This file is part of pyOBD.
#
# pyOBD is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# pyOBD is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyOBD; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
###########################################################################

# Definition of methods used to preform hexadecimal conversion to human readable information

# Converts argument, hexadecimal, into the Mass Air Flow sensor reading
def maf(code):
    code = int(code, 16)
    return code * 0.00132276

# Converts argument, hexadecimal, into the Throttle Position
def throttle_pos(code):
    code = int(code, 16)
    return code * 100.0 / 255.0

# Converts argument, hexadecimal, into the Intake Manifold Pressure (absolute measurement)
def intake_m_pres(code): # in kPa
    code = int(code, 16)
    return code / 0.14504

# Converts argument, hexadecimal, into the Engine RPM
def rpm(code):
    code = int(code, 16)
    return code / 4

# Converts argument, hexadecimal, into the vehicle's Speed
def speed(code):
    code = int(code, 16)
    return code * .621371

# Converts argument, hexadecimal, into a percentage
def percent_scale(code):
    code = int(code, 16)
    return code * 100.0 / 255.0

# Converts argument, hexadecimal, into the Engine Advance
def timing_advance(code):
    code = int(code, 16)
    return (code - 128) / 2.0

# Converts argument, hexadecimal seconds, into minutes
def sec_to_min(code):
    code = int(code, 16)
    return code / 60

# Coverts argument, hexadecimal, into temperature
def temp(code):
    code = int(code, 16)
    return code - 40

# Converts argument, hexadecimal, onto fuel pressure
def fuel_pres(code):
    code = int(code, 16)
    return code * 3

def cpass(code):
    print code
    return code

# Converts argument, hexadecimal, into PTO status
def pto_status(code):
    code = int(code, 16)
    if code is 1:
        return code
    else:
        return 0

# Converts argument, hexadecimal, into OBD compliance type
def compliance(code):
 for i in OBD_COMPLIANCE:
     if i.hex_format.equal(code):
        return i.compliance_description
     else:
         return 0

# Converts argument, hexadecimal, into the Fuel Trim Percentage
def fuel_trim_percent(code):
    code = int(code, 16)
    return (code - 128.0) * 100.0 / 128

# Converts argument, hexadecimal, into 0^2 sensor locations
def sensor_pos(code):
    code = int(code, 16)
    if(code >= 160 and code <= 163):
        return 'Bank 1'
    elif(code >= 164 and code <= 167):
        return 'Bank 2'
    else:
        return 'None'

# Converts argument, hexadecimal, into a Diagnostic Trouble Code
def dtc_decrypt(code):
    #first byte is byte after PID and without spaces
    num = int(code[:2], 16) #A byte
    res = []

    # Sets flag if Manufacturer's Indicator Light is on
    if num & 0x80: # is mil light on
        mil = 1
    else:
        mil = 0

    # bit 0-6 are the number of dtc's.
    num = num & 0x7f

    res.append(num)
    res.append(mil)

    numB = int(code[2:4], 16) #B byte

    for i in range(0,3):
        res.append(((numB>>i)&0x01)+((numB>>(3+i))&0x02))

    numC = int(code[4:6], 16) #C byte
    numD = int(code[6:8], 16) #D byte

    for i in range(0,7):
        res.append(((numC>>i)&0x01)+(((numD>>i)&0x01)<<1))
    res.append(((numD>>7)&0x01)) #EGR SystemC7  bit of different

    return res

# Convert argument, hexadecimal string, into a bit string
def hex_to_bitstring(hex_str):
    return '{0:08b}'.format(int(hex_str, 16))

# Sensor class definition
class Sensor:
    def __init__(self, shortName, sensorName, sensorcommand, sensorValueFunction, u):
        self.shortname = shortName
        self.name = sensorName
        self.cmd = sensorcommand
        self.value = sensorValueFunction
        self.unit = u

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

# OBD compliance class definition
class OBD_Comply:
    def __init__(self, compliance_description, hex_format, binary_format,):
        self.compliance_description = compliance_description
        self.hex_format = hex_format
        self.binary_format = binary_format

# List of OBD compliance types
OBD_COMPLIANCE = [
    OBD_Comply("                 OBD II as defined by CARB", "0x01", "00000001b" ),
    OBD_Comply("                     OBD as defined by EPA", "0x02", "00000010b" ),
    OBD_Comply("                          OBD I and OBD II", "0x03", "00000011b" ),
    OBD_Comply("                                     OBD I", "0x04", "00000100b" ),
    OBD_Comply("Note ment to comply with any OBD standard ", "0x05", "00000101b" ),
    OBD_Comply("                             EOBD (Europe)", "0x06", "00000110b" ),
    OBD_Comply("                           EOBD and OBD II", "0x07", "00000111b" ),
    OBD_Comply("                            EOBD and OBD I", "0x08", "00001000b" ),
    OBD_Comply("                    EOBD, OBD I and OBD II", "0x09", "00001001b" ),
    OBD_Comply("                              JOBD (Japan)", "0x0A", "00001010b" ),
    OBD_Comply("                           JOBD and OBD II", "0x0B", "00001011b" ),
    OBD_Comply("                             JOBD and EOBD", "0x0C", "00001100b" ),
    OBD_Comply("                     JOBD, EOBD and OBD II", "0x0D", "00001101b" )
    ]


# Secondary air status class definition
class Air_Sec:
    def __init__(self, description, hex_format):
        self.description = description
        self.hex_format = hex_format

# List of Secondary air status'
AIR_SECONDARY = [
    Air_Sec("  Upstream from catalytic converter", "AO"),
    Air_Sec("Downstream from catalytic converter", "A1"),
    Air_Sec("     From outside atmosphere or off", "A2"),
    Air_Sec("                        Always Zero", "A3"),
    Air_Sec("                        Always Zero", "A3"),
    Air_Sec("                        Always Zero", "A4"),
    Air_Sec("                        Always Zero", "A5"),
    Air_Sec("                        Always Zero", "A6"),
    Air_Sec("                        Always Zero", "A7")
    ]
#___________________________________________________________

def test():
    for i in SENSORS:
        print i.name, i.value("F")

if __name__ == "__main__":
    test()
