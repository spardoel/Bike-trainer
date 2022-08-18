# Developing a cycling control program for my indoor trainer (TrainerRoad clone) Part 1 - Establish a BLE connection
First of all, thanks for checking out my Github page! 
This project is a personal development project that I am undertaking to practice my python coding skills and to explore new libraries and functionalities. 
My intention is to use mainly python and PostgreSQL.

The overall goal is to make a basic version of TrainerRoad, which is a popular cycling training platform. 

To start, I wanted to see if I could connect to my bike trainer. I use the Suito trainer by Elite. 
In the past I have used MATLAB to control bluetooth devices, so I started there. 

I started with the basics. Search for available devices, connect to the device by name, then display the services and characteristics. 
These are the commands that will be used in this post.
```
devlist = blelist % list the available bluetooth low energy devices.
suito_device = ble("SUITO") % connect to the device names "SUITO"
suito_device.Services % show the available services
suito_device.Characteristics % show all available characteristics
```

### Scan for available device

```
devlist = blelist % list the available bluetooth low energy devices.
```
This was the output shown in the MATLAB Command Window:
```
    Index            Name               Address        RSSI    Advertisement
    _____    ____________________    ______________    ____    _____________

      1      "SUITO"                 "F3DB2BF4470C"    -63      1×1 struct  
      2      ""                      "51C6F31E60BC"    -65      1×1 struct  
      3      "S9f1b4589198ad67cC"    "B4D285C2CDFE"    -91      1×1 struct  
      4      ""                      "48AB51FEDB8E"    -91      1×1 struct  
      5      ""                      "535735FC234A"    -97      1×1 struct  
```
The first device labeled "Suito" is the one I wanted.

### Establish a connection
Next, using the name of the device connect using bluetooth low energy.
```
suito_device = ble("SUITO") % connect to the device names "SUITO"
```
A ble object was created in the MATLAB workspace and is summarized in the Command Window
```
suito_device = 
  ble with properties:
               Name: "SUITO"
            Address: "F3DB2BF4470C"
          Connected: 1
           Services: [8×2 table]
    Characteristics: [34×5 table]
```

### Explore the available services and characteristics
Next, I wanted to see what services and characteristics were available. This can be done by double clicking on the ble object in the Workspace, or by entering the following commands
```
suito_device.Services % show the available services
suito_device.Characteristics % show all available characteristics
```
The output:
```
>> suito_device.Services
ans =
  8×2 table
            ServiceName                         ServiceUUID              
    ___________________________    ______________________________________

    "Generic Access"               "1800"                                
    "Generic Attribute"            "1801"                                
    "Cycling Speed and Cadence"    "1816"                                
    "Cycling Power"                "1818"                                
    "Fitness Machine"              "1826"                                
    "Custom"                       "347B0001-7635-408B-8918-8FF3949CE592"
    "Device Information"           "180A"                                
    "Custom"                       "8E400001-F315-4F60-9FB8-838830DAEA50"

>> suito_device.Characteristics
ans =
  34×5 table
            ServiceName                         ServiceUUID                               CharacteristicName                           CharacteristicUUID                     Attributes        
    ___________________________    ______________________________________    ____________________________________________    ______________________________________    _________________________

    "Generic Access"               "1800"                                    "Device Name"                                   "2A00"                                    {["Read"    "Write"    ]}
    "Generic Access"               "1800"                                    "Appearance"                                    "2A01"                                    {["Read"               ]}
    "Generic Access"               "1800"                                    "Peripheral Preferred Connection Parameters"    "2A04"                                    {["Read"               ]}
    "Generic Access"               "1800"                                    "Central Address Resolution"                    "2AA6"                                    {["Read"               ]}
    "Generic Attribute"            "1801"                                    "Service Changed"                               "2A05"                                    {["Indicate"           ]}
    "Cycling Speed and Cadence"    "1816"                                    "CSC Measurement"                               "2A5B"                                    {["Notify"             ]}
    "Cycling Speed and Cadence"    "1816"                                    "CSC Feature"                                   "2A5C"                                    {["Read"               ]}
    "Cycling Speed and Cadence"    "1816"                                    "Sensor Location"                               "2A5D"                                    {["Read"               ]}
    "Cycling Power"                "1818"                                    "Cycling Power Measurement"                     "2A63"                                    {["Notify"             ]}
    "Cycling Power"                "1818"                                    "Cycling Power Feature"                         "2A65"                                    {["Read"               ]}
    "Cycling Power"                "1818"                                    "Sensor Location"                               "2A5D"                                    {["Read"               ]}
    "Cycling Power"                "1818"                                    "Cycling Power Control Point"                   "2A66"                                    {["Write"    "Indicate"]}
    "Fitness Machine"              "1826"                                    "Fitness Machine Feature"                       "2ACC"                                    {["Read"               ]}
    "Fitness Machine"              "1826"                                    "Indoor Bike Data"                              "2AD2"                                    {["Notify"             ]}
    "Fitness Machine"              "1826"                                    "Training Status"                               "2AD3"                                    {["Notify"             ]}
    "Fitness Machine"              "1826"                                    "Supported Resistance Level Range"              "2AD6"                                    {["Read"               ]}
    "Fitness Machine"              "1826"                                    "Supported Power Range"                         "2AD8"                                    {["Read"               ]}
    "Fitness Machine"              "1826"                                    "Fitness Machine Status"                        "2ADA"                                    {["Notify"             ]}
    "Fitness Machine"              "1826"                                    "Fitness Machine Control Point"                 "2AD9"                                    {["Write"    "Indicate"]}
    "Custom"                       "347B0001-7635-408B-8918-8FF3949CE592"    "Custom"                                        "347B0010-7635-408B-8918-8FF3949CE592"    {["Write"              ]}
    "Custom"                       "347B0001-7635-408B-8918-8FF3949CE592"    "Custom"                                        "347B0011-7635-408B-8918-8FF3949CE592"    {["Notify"             ]}
    "Custom"                       "347B0001-7635-408B-8918-8FF3949CE592"    "Custom"                                        "347B0018-7635-408B-8918-8FF3949CE592"    {["Write"              ]}
    "Custom"                       "347B0001-7635-408B-8918-8FF3949CE592"    "Custom"                                        "347B0012-7635-408B-8918-8FF3949CE592"    {["Write"              ]}
    "Custom"                       "347B0001-7635-408B-8918-8FF3949CE592"    "Custom"                                        "347B0013-7635-408B-8918-8FF3949CE592"    {["Read"               ]}
    "Custom"                       "347B0001-7635-408B-8918-8FF3949CE592"    "Custom"                                        "347B0014-7635-408B-8918-8FF3949CE592"    {["Notify"             ]}
    "Custom"                       "347B0001-7635-408B-8918-8FF3949CE592"    "Custom"                                        "347B0016-7635-408B-8918-8FF3949CE592"    {["Write"              ]}
    "Custom"                       "347B0001-7635-408B-8918-8FF3949CE592"    "Custom"                                        "347B0017-7635-408B-8918-8FF3949CE592"    {["Notify"             ]}
    "Custom"                       "347B0001-7635-408B-8918-8FF3949CE592"    "Custom"                                        "347B0019-7635-408B-8918-8FF3949CE592"    {["Read"               ]}
    "Device Information"           "180A"                                    "Manufacturer Name String"                      "2A29"                                    {["Read"               ]}
    "Device Information"           "180A"                                    "Serial Number String"                          "2A25"                                    {["Read"               ]}
    "Device Information"           "180A"                                    "Hardware Revision String"                      "2A27"                                    {["Read"               ]}
    "Device Information"           "180A"                                    "Firmware Revision String"                      "2A26"                                    {["Read"               ]}
    "Device Information"           "180A"                                    "Software Revision String"                      "2A28"                                    {["Read"               ]}
    "Custom"                       "8E400001-F315-4F60-9FB8-838830DAEA50"    "Custom"                  
  
```
As you can see, the services and chracteristics are nicely listed along with the UUIDs and attributes. 

### Wrap up

This is the end of the first post. I established a BLE connection and displayed the available services and characteristics. 
The next step for me was to install a local bluetooth packet sniffer to see which services and charateristics were being used during normal use. 


