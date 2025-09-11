import logging

from .SentioRegisterMap import *
from .ModbusWrapper import ModbusWrapper
from .SentioTypes import *
from .Defaults import Defaults

class SentioRoomHandler:
    def __init__(self, api:ModbusWrapper):
        self._detectedRooms = []
        self._api = api
        pass

    def initialize(self):
        roomCtr = 0
        self._detectedRooms = []
        for roomCtr in range(Defaults.MaxNumberOfRooms):
            try:
                value = self._api.readRegister(SentioRegisterMap.RoomName, _subIndex = roomCtr)
                if value != None:
                    self._detectedRooms.append(SentioRoom(roomCtr, value, self._api))
                #else:
                    #logging.error("Room {0} not found".format(roomCtr))
            except Exception as e:
                logging.exception("Exception reading room {0}".format(e))
                return -1

        for room in self._detectedRooms:
            logging.debug("Room ID={0} | Name={1}".format(room.index, room.name))
        return 0
    
    def updateData(self):
        for room in self._detectedRooms:
            room.updateData()

class SentioRoom:
    def __init__(self, index, name, api:ModbusWrapper):
        self.index = index;
        self.name = name;
        self.roomMode = SentioRoomMode.MANUAL
        self.heatingState = SentioHeatingStates.IDLE
        self.airTemp = 0.0
        self.temperatureSetPoint = 0.0
        self.humidity = 0.0
        self.floorTemp = 0.0
        self.roomBlockingMode = None
        self._api = api

    def GetRoomIndex(self):
        return self.index
    
    def GetAirTemp(self):
        return self.CurrentTemp

    def GetFloorTemp(self):
        return self.floorTemp

    def SetAirTemp(self, temperature):
        self.CurrentTemp = temperature
        
    def SetFloorTemp(self, temperature):
        self.floorTemp = temperature

    def GetFloorTemp(self):
        return self.floorTemp

    def SetTemperatureSetpoint(self, setpoint):
        self.SetPoint = setpoint

    def __str__(self):
        return "{0} - {1}".format(self.index, self.name)

    def updateData(self):
        #print("Updating room {0} data now".format(self.index))
        #TODO; here is al lot of duplicity, we can (should) simplify this..
        tempSetpoint = self._api.readRegister(SentioRegisterMap.RoomTempSetpoint, _subIndex = self.index)
        if tempSetpoint != None and tempSetpoint != Defaults.InvalidFP2_100:
            self.temperatureSetPoint = tempSetpoint
        else:
            self.temperatureSetPoint = None
        self.calculatedDewPoint = self._api.readRegister(SentioRegisterMap.RoomCalcDewPoint, _subIndex = self.index)
        if(self.calculatedDewPoint == Defaults.InvalidFP2_100):
            self.calculatedDewPoint = None
        self.floorTemp  = self._api.readRegister(SentioRegisterMap.RoomFloorTempActual, _subIndex = self.index)
        if(self.floorTemp == Defaults.InvalidFP2_100):
            self.floorTemp = None
        self.airTemp   = self._api.readRegister(SentioRegisterMap.RoomAirTempActual, _subIndex = self.index)
        if self.airTemp: 
            self.airTemp = self.airTemp
        self.humidity  = self._api.readRegister(SentioRegisterMap.RoomRelHumidity, _subIndex = self.index)
        if(self.humidity == Defaults.InvalidFP2_100):
           self.humidity = None
        self.co2Concentration = self._api.readRegister(SentioRegisterMap.RoomCO2Level, _subIndex = self.index)
        if(self.co2Concentration == Defaults.Invalid_UINT16):
            self.co2Concentration = None

        value = self._api.readRegister(SentioRegisterMap.RoomHeatingState, _subIndex = self.index)
        if value:
            self.heatingState = SentioHeatingStates(value)
        value = self._api.readRegister(SentioRegisterMap.RoomMode, _subIndex = self.index)
        if value:
            self.roomMode = SentioRoomMode(value)
        value = self._api.readRegister(SentioRegisterMap.RoomPresetMode, _subIndex = self.index)
        if value and (value >= SentioRoomPreset.RP_MIN) and (value <= SentioRoomPreset.RP_MAX):
            self.roomPreset = SentioRoomPreset(value)
        if self.heatingState == SentioHeatingStates.BLOCKED_COOLING or self.heatingState == SentioHeatingStates.BLOCKED_HEATING:
            value = self._api.readRegister(SentioRegisterMap.RoomBlockingReason, _subIndex = self.index)
            if value:
                self.roomBlockingMode = SentioRoomBlockingReasons(value)
        else:
            self.roomBlockingMode = None
        pass

    def setRoomSetpoint(self, setpointdouble):
        mode = self._api.readRegister(SentioRegisterMap.RoomModeOverride, _subIndex = self.index)
        if mode and mode != SentioRoomModeSetting.RM_NONE:
            self._api.writeRegister(SentioRegisterMap.RoomModeOverride, SentioRoomModeSetting.RM_NONE.value, _subIndex = self.index)

        setpoint_fp100 = int(setpointdouble * 100)
        logging.debug(" ---------- Set room {0} temp setpoint to {1}".format(self.index, setpoint_fp100))
        value = self._api.writeRegister(SentioRegisterMap.RoomTempSetpChange, setpoint_fp100, _subIndex = self.index)
        self.temperatureSetPoint = setpointdouble
        #print("Setting room temperature setpoint to " + setpointdouble + " result " + value)
        return value
    
    def getRoomSetpoint(self):
        return self.temperatureSetPoint
    
    def getRoomActualTemperature(self):
        return self.airTemp
        
    def getRoomRelativeHumidity(self):
        return self.humidity

    def getRoomFloorTemperature(self):
        return self.floorTemp

    def getRoomCalculatedDewPoint(self):
        return self.calculatedDewPoint

    def getRoomCO2Level(self):
        return self.co2Concentration
    
    def getRoomHeatingState(self):
        return self.heatingState

    def getRoomMode(self):
        return self.roomMode

    def setRoomMode(self, roomMode:SentioRoomMode):
        value = self._api.writeRegister(SentioRegisterMap.RoomMode, roomMode.value, _subIndex = self.index)
        print("Setting Room {0} to set room {1} {2} == Result:{3}".format(self.index, roomMode, roomMode.value, value))
        self.roomMode = roomMode

    def setRoomPreset(self, roomPreset:SentioRoomPreset):
        val = self._api.writeRegister(SentioRegisterMap.RoomPresetMode, roomPreset.value, _subIndex = self.index)
        print("Setting Room Preset {0} {1}".format(roomPreset.value, val))
        self.roomPreset = roomPreset

    def setRoomHeatingState(self, roomHvacMode:SentioRoomModeSetting):
        #todo
        
        pass

