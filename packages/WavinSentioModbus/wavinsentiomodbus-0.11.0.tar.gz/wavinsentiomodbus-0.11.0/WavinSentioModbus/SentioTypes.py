import logging

from enum import Enum

class SentioDeviceType(Enum):
    CCU208 = 1
    DHW201 = 2

class SentioCMVVentilationState(Enum):
    STOPPED = 0
    UNOCCUPIED = 1
    ECONOMY = 2
    COMFORT = 3
    BOOST = 4
    BLOCKED_STOPPED = 5
    BLOCKED_UNOCCUPIED = 6
    BLOCKED_ECONOMY = 7
    BLOCKED_COMFORT = 8
    BLOCKED_BOOST = 9
    FAILURE = 10
    MAINTENANCE = 11

class SentioHeatingStates(Enum):
    IDLE = 1
    HEATING = 2 
    COOLING = 3
    BLOCKED_HEATING = 4 
    BLOCKED_COOLING = 5

class SentioRoomMode(Enum):
    SCHEDULE = 0
    MANUAL = 1
    
class SentioRoomModeSetting(Enum):
    RM_NONE = 0
    RM_TEMPORARY = 1
    RM_VACATION_AWAY = 2
    RM_ADJUST = 3

class SentioRoomPreset(Enum):
    RP_INVALID = -1
    RP_ECO= 0
    RP_COMFORT = 1
    RP_EXTRA_COMFORT = 2
    RP_MIN = RP_ECO           #Start
    RP_MAX = RP_EXTRA_COMFORT #Sentinel

class ITC_PumpState(Enum):
    PUMP_IDLE = 1
    PUMP_ON = 2

class SentioRoomBlockingReasons(Enum):
    NONE = 0
    UNKNOWN = 1
    CONTACT = 2
    FLOOR_TEMP = 3
    LOW_ENERGY = 4
    AIR_TEMP = 5
    DEW_POINT = 6
    OUTDOOR_TEMP = 7
    FAULT = 8# (general fault, e.g. missing sensors)
    FAULT_HTCO = 9
    PERIODIC_ACTIVATION = 10
    BMS = 11
    DEADBAND = 12
    DRYING = 13
    HEATING_COOLING_MODE = 14
    INSUFFICIENT_DEMAND = 15
    COOLDOWN_PERIOD=16
    HCW_SOURCE_NOT_RELEASED = 17
    ROOM_MODE = 18
    SYSTEM_IS_INITIALIZING = 19
    SYSTEM_IS_SHUTTING_DOWN = 20
    NO_OUTPUT = 21
    FIRST_OPEN_ACTIVATION = 22
    ROOM_WITH_NO_TEMPERATURE = 23
