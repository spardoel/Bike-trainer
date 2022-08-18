clear all % clear all variables to start fresh


devlist = blelist % list the available bluetooth low energy devices.

suito_device = ble("SUITO") % connect to the device names "SUITO"

suito_device.Services % show the available services

suito_device.Characteristics % show all available characteristics



