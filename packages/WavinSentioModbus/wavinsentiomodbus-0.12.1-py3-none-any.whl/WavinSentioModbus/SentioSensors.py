import logging

from .SentioRegisterMap import *
from .ModbusWrapper import ModbusWrapper
from .SentioTypes import *
from .Defaults import Defaults

class SentioSensors:
    def __init__(self, api:ModbusWrapper):
        self._outdoorTemp = None
        self._hcsourceState = None
        
        self._deviceType = None
        self._serialNumber = None
        self._firmwareVersionMajor = None
        self._firmwareVersionMinor = None
        
        self._api = api
    
     ### TODO remove?
    #def readDeviceData(self):
    #    devType = self.modbusWrapper.readRegister(SentioRegisterMap.DeviceType)
    #    logging.info("DeviceType           = {0}".format(devType))
    #    logging.info("SerialNumberPrefix   = {0}".format(self.modbusWrapper.readRegister(SentioRegisterMap.DeviceSerialNrPrefix)))
    #    logging.info("SerialNumber         = {0}".format(self.modbusWrapper.readRegister(SentioRegisterMap.DeviceSerialNumber)))
    #    logging.info("FirmwareVersion         = {0}".format(self.modbusWrapper.readRegister(SentioRegisterMap.DeviceSerialNumber)))
    #    logging.info("ModbusMode           = {0}".format(self.modbusWrapper.readRegister(SentioRegisterMap.ModbusMode)))
        
    def initialize(self):
        returnValue = 0
        try:
            deviceTypeInt = self._api.readRegister(SentioRegisterMap.DeviceType)
            if deviceTypeInt:
                self._deviceType = SentioDeviceType(deviceTypeInt)
            else:
                self._deviceType = None

            serialNumberPrefix =  self._api.readRegister(SentioRegisterMap.DeviceSerialNrPrefix)
            serialNumberNumber  = self._api.readRegister(SentioRegisterMap.DeviceSerialNumber)
            serialNumberNumber = str(serialNumberNumber).zfill(Defaults.SerialNumberLength - Defaults.SerialNumberPrefixLen)
            self._serialNumber  = "{0}-{1}-{2}-{3}".format(serialNumberPrefix, serialNumberNumber[:2], serialNumberNumber[2:6], serialNumberNumber[6:10])

            self._firmwareVersionMajor = self._api.readRegister(SentioRegisterMap.DeviceSwVersion)
            self._firmwareVersionMinor = self._api.readRegister(SentioRegisterMap.DeviceSwVersionMinor)  

        except Exception as e:
            logging.error("Exception occured ==> {0}".format(e))
            returnValue = -1
        return returnValue

    def updateData(self):      
        #repetative values:
        self._outdoorTemp = self._api.readRegister(SentioRegisterMap.OutdoorTemperature)
        if self._outdoorTemp and self._outdoorTemp == Defaults.InvalidFP2_100:
            self._outdoorTemp = None
        hcstate = self._api.readRegister(SentioRegisterMap.HCSourceState)
        if hcstate:
            self._hcsourceState = SentioHeatingStates(hcstate)


    @property
    def outdoor_temperature(self) -> float:
        """Return outdoor temperature."""
        return self._outdoorTemp
    
    @property
    def hc_source_state(self) -> float:
        """Return H/C source state."""
        return self._hcsourceState

    @property
    def device_type(self) -> SentioDeviceType:
        return self._deviceType

    @property
    def serial_number(self):
        return self._serialNumber
    
    @property
    def firmware_version_major(self) -> int:
        return self._firmwareVersionMajor

    @property
    def firmware_version_minor(self) -> int:
        return self._firmwareVersionMinor

    @property
    def firmware_version_major(self) -> int:
        return self._firmwareVersionMajor