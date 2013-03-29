import serial
import platform


# Method to scan through the a list of 4 possible serial port locations
# 1. ttyS
# 2. ttyACM
# 3. ttyUSB
# 4. ttyd
# Incrementing through the 256 possibility for each location
def scanSerial():
    """scan for available ports. return a list of serial names"""
    available = []
    for i in range(256):
      try: #scan standard ttyS*
        s = serial.Serial(i)
        available.append(s.portstr)
        s.close()   # explicit close 'cause of delayed GC in java
      except serial.SerialException:
        pass
    for i in range(256):
      try: #scan USB ttyACM
        s = serial.Serial("/dev/ttyACM"+str(i))
        available.append(s.portstr)
        s.close()   # explicit close 'cause of delayed GC in java
      except serial.SerialException:
        pass
    for i in range(256):
      try:
        s = serial.Serial("/dev/ttyUSB"+str(i))
        available.append(s.portstr)
        s.close()   # explicit close 'cause of delayed GC in java
      except serial.SerialException:
        pass
    for i in range(256):
      try:
        s = serial.Serial("/dev/ttyd"+str(i))
        available.append(s.portstr)
        s.close()   # explicit close 'cause of delayed GC in java
      except serial.SerialException:
        pass
        
    # ELM-USB shows up as /dev/tty.usbmodemXXXX, where XXXX is a changing hex string
    # on connection; so we have to search through all 64K options
    if len(platform.mac_ver()[0])!=0:  #search only on MAC
      for i in range (65535):
        extension = hex(i).replace("0x","", 1)
        try:
          s = serial.Serial("/dev/tty.usbmodem"+extension)
          available.append(s.portstr)
          s.close()
        except serial.SerialException:
          pass 
    
    return available
