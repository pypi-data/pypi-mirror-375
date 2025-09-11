from enum import Enum

class RegisterType(Enum):
    """This enumeration defines the type of a register"""
    DISCRETE_INPUT = 0
    INPUT_REGISTER = 1
    HOLDING_REGISTER = 2
    INPUT_REGISTER_MULT = 10

class RegisterDataType(Enum):
    """This enumeration defines the data type of a register"""
    VAL_U1 = 0 # One byte long unsigned integer
    VAL_U2 = 1 # Two bytes long unsigned integer
    VAL_U4 = 2 # Four bytes long unsigned integer
    VAL_U2_FP10 = 3 # Two bytes long unsigned integer divided by 10
    VAL_U2_FP100 = 4 # Two bytes long unsigned integer divided by 100
    VAL_D1 = 5 # One byte long signed integer
    VAL_D2 = 6 # Two bytes long signed integer
    VAL_D4 = 7 # Four bytes long signed integer
    VAL_D2_FP10 = 8 # Two bytes long signed integer divided by 10
    VAL_D2_FP100 = 9 # Two bytes long signed integer divided by 100
    STRING = 10 # A string

InvalidValues: dict = {
    RegisterDataType.VAL_U1: 255,
    RegisterDataType.VAL_U2: 65535,
    RegisterDataType.VAL_U4: 4294967295,
    RegisterDataType.VAL_U2_FP10: 6553.5,
    RegisterDataType.VAL_U2_FP100: 655.35,
    RegisterDataType.VAL_D1: 127,
    RegisterDataType.VAL_D2: 32767,
    RegisterDataType.VAL_D4: 2147483647,
    RegisterDataType.VAL_D2_FP10: 3276.7,
    RegisterDataType.VAL_D2_FP100: 327.67
}

class RegisterObjectType(Enum):
    """This enumeration defines the object type of a register"""
    GENERIC = 0
    ROOM = 1
    DEHUMIDIFIERS = 10
    OUTDOOR = 33
    DHW_CONTROLLERS = 65
    DHW_TANKS = 66
    ITC_CIRCUITS = 73
    HCCS = 77
    PGOS = 128
    PERIPHERIES = 512
    VENTILATIONS = 610

class RegisterImplementationVersion(Enum):
    """This enumeration defines minimal version required of using a specific register"""
    NOT_SUPPORTED = -1
    V1_0 = 0
    V2_0 = 1
    V3_0 = 2
    V3_1 = 3
    V3_2 = 4
    V3_3 = 5
    V3_4 = 6
    V3_5 = 7

class RegisterRoomTypeSupport(Enum):
    """This enumeration defines whether a register is supported by a room type"""
    BOTH = 0
    NORMAL_ONLY = 1
    DUMMY_ONLY = 2

class RegisterRepresentation:
    """This class defines a register representation"""
    def __init__(
            self, 
            _regType: RegisterType,
            _address: int,
            _count: int,
            _dataType: RegisterDataType = RegisterDataType.VAL_U2,
            _objectType: RegisterObjectType = RegisterObjectType.GENERIC,
            _minVersion: RegisterImplementationVersion = RegisterImplementationVersion.V3_5
        ):
        self.regType = _regType
        self.address = _address
        self.count = _count
        self.dataType = _dataType
        self.objectType = _objectType
        self.minVersion = _minVersion

    def __str__(self):
        return "Address:{0}, Type:{1}, Count:{2}, DataType:{3}, ObjectType:{4}".format(self.address, self.regType, self.count, self.dataType, self.objectType)

class RoomRegisterRepresentation(RegisterRepresentation):
    """This class adds room type support to a register representation"""
    def __init__(
            self,
            _regType: RegisterType,
            _address: int,
            _count: int,
            _dataType: RegisterDataType = RegisterDataType.VAL_U2,
            _objectType: RegisterObjectType = RegisterObjectType.ROOM,
            _minVersion: RegisterImplementationVersion = RegisterImplementationVersion.V3_5,
            _roomType: RegisterRoomTypeSupport = RegisterRoomTypeSupport.BOTH
        ):
        super().__init__(_regType, _address, _count, _dataType, _objectType, _minVersion)
        self.roomType = _roomType


class SentioRegisterMap:
    """This class contains all register representations"""
    class Location:
        #Discrete Inputs
        AggregatedWarning                   = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 1, 1, _minVersion=RegisterImplementationVersion.V1_0)
        AggregatedError                     = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 2, 1, _minVersion=RegisterImplementationVersion.V1_0)

        #Input Registers
        AdressSpaceMajorVersion             = RegisterRepresentation(RegisterType.INPUT_REGISTER, 1, 1, _dataType=RegisterDataType.VAL_U1, _minVersion=RegisterImplementationVersion.V3_0)
        AdressSpaceMinorVersion             = RegisterRepresentation(RegisterType.INPUT_REGISTER, 2, 1, _dataType=RegisterDataType.VAL_U1, _minVersion=RegisterImplementationVersion.V3_4)
        #reserve
        DeviceType                          = RegisterRepresentation(RegisterType.INPUT_REGISTER, 10, 1, _dataType=RegisterDataType.VAL_U1, _minVersion=RegisterImplementationVersion.V1_0) #Values: 0 = CCU-208, 1 = DHW-201
        DeviceHwVersion                     = RegisterRepresentation(RegisterType.INPUT_REGISTER, 11, 1, _dataType=RegisterDataType.VAL_U1, _minVersion=RegisterImplementationVersion.V1_0)
        DeviceSwVersion                     = RegisterRepresentation(RegisterType.INPUT_REGISTER, 12, 1, _dataType=RegisterDataType.VAL_U1, _minVersion=RegisterImplementationVersion.V1_0)
        DeviceSwVersionMinor                = RegisterRepresentation(RegisterType.INPUT_REGISTER, 13, 1, _dataType=RegisterDataType.VAL_U1, _minVersion=RegisterImplementationVersion.V1_0)
        DeviceSerialNrPrefix                = RegisterRepresentation(RegisterType.INPUT_REGISTER, 14, 1, _dataType=RegisterDataType.VAL_U2, _minVersion=RegisterImplementationVersion.V1_0)
        DeviceSerialNumber                  = RegisterRepresentation(RegisterType.INPUT_REGISTER, 15, 2, _dataType=RegisterDataType.VAL_U4, _minVersion=RegisterImplementationVersion.V1_0)
        #reserve
        HeatingCoolingMode                  = RegisterRepresentation(RegisterType.INPUT_REGISTER, 20, 1, _dataType=RegisterDataType.VAL_U1, _minVersion=RegisterImplementationVersion.V3_1) #Values: 0 = Heating, 1 = Cooling

        #Holding Registers
        AdressSpaceMajorVersionHolding      = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 1, 1, _dataType=RegisterDataType.VAL_U1)
        AdressSpaceMinorVersionHolding      = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 2, 1, _dataType=RegisterDataType.VAL_U1)
        ModbusSlaveAdress                   = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 3, 1, _dataType=RegisterDataType.VAL_U1) #Allowed values: 1-247
        ModbusBaudrate                      = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 4, 1, _dataType=RegisterDataType.VAL_U2) #Allowed values: 9600, 19200, 38400, 57600
        ModbusMode                          = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 5, 1, _dataType=RegisterDataType.VAL_U1) #Allowed values: 0 = Disabled, 1 = Read Only, 2 = Read Write, 3 = Write with password
        ModbusPassword                      = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6, 2, _dataType=RegisterDataType.VAL_U2) #Allowed values: 0-65535, Write only
        ModbusParity                        = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7, 1, _dataType=RegisterDataType.VAL_U1) #Allowed values: 0 = None, 1 = Even, 2 = Odd
        ModbusStopBits                      = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 8, 1, _dataType=RegisterDataType.VAL_U1) #Allowed values: 0 = 1, 2 = 1 Stop bit
        #reserve
        LocationName                        = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 10, 15, _dataType=RegisterDataType.STRING)
        Standby                             = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 26, 1, _dataType=RegisterDataType.VAL_U1) #Allowed values: 0 = Disabled, 1 = Enabled
        Vacation                            = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 27, 1, _dataType=RegisterDataType.VAL_U1) #Allowed values: 0 = Disabled, 1 = Enabled
        DateTime                            = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 28, 2, _dataType=RegisterDataType.VAL_U4) # - unit timestamp format - localtime including DST (if enabled) - minimum date is 2018-01-01 00:00:00 - maximum date is 2099-12-30 23:59:59
        DaylightSavingTimeAllowed           = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 30, 1, _dataType=RegisterDataType.VAL_U1) #Allowed values: 0 = Disabled, 1 = Enabled
        CoolingMinimumOutdoorTemperature    = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 31, 1, _dataType=RegisterDataType.VAL_D2_FP100) #Only available whith profile supporting cooling mode
        HeatingMaxiumumOutdoorTemperature   = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 32, 1, _dataType=RegisterDataType.VAL_D2_FP100) #Must be lower or equal than CoolingMinimumOutdoorTemperature
        UpdateMode                          = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 33, 1, _dataType=RegisterDataType.VAL_U1) #Allowed values: 0 = Disabled from mobile app, 1 = Enabled, 2 = Disable entirely
        HeatingCoolingModeBMSOverride       = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 34, 1, _dataType=RegisterDataType.VAL_U1) #Allowed values: 0 = Disabled, 1 = Heating mode, 2 = Cooling mode, 3 = By external input
        TimeZoneNumber                      = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 35, 1, _dataType=RegisterDataType.VAL_U2) #TODO translator
        CoolingToHeatingChangeOutTemp       = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 36, 1, _dataType=RegisterDataType.VAL_D2_FP100) #Only available whith profiles 3.3.1 and 3.3.3
        HeatingToCoolingChangeOutTemp       = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 37, 1, _dataType=RegisterDataType.VAL_D2_FP100) #Only available whith profiles 3.3.1 and 3.3.3

    class Room:
        #Discrete Inputs
        AggregatedWarning                   = RoomRegisterRepresentation(RegisterType.DISCRETE_INPUT, 101, 1, _objectType=RegisterObjectType.ROOM)
        AggregatedError                     = RoomRegisterRepresentation(RegisterType.DISCRETE_INPUT, 102, 1, _objectType=RegisterObjectType.ROOM)
        LowBatteryWarning                   = RoomRegisterRepresentation(RegisterType.DISCRETE_INPUT, 103, 1, _objectType=RegisterObjectType.ROOM, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        PeripheryLostError                  = RoomRegisterRepresentation(RegisterType.DISCRETE_INPUT, 104, 1, _objectType=RegisterObjectType.ROOM, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)   

        #Input Registers
        DesiredTemperature                  = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 101, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_D2_FP100)
        GeneralHeatingCoolingState          = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 102, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1) #Values: 1 = Idle, 2 = Heating, 3 = Cooling, 4 = Blocked heating, 5 = Blocked cooling
        GeneralHeatingCoolingBlockingSource = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 103, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1)
        AirTemperature                      = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 104, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_D2_FP100, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        FloorTemperature                    = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 105, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_D2_FP100, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        RelativeHumidity                    = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 106, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_D2_FP100, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        CalculatedDewPoint                  = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 107, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_D2_FP100, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        #COConcentration                     = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 108, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_D2_FP100, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY) #Not supported
        CO2Concentration                    = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 109, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U2, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        VOCConcentration                    = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 110, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U2, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        AssociatedToRadiators               = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 111, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY) #0 = None
        AssociatedToUFHC                    = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 112, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        AssociatedToHeatingBlock            = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 113, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        AssociatedToDryer                   = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 114, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        AssociatedToThermalIntegration      = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 115, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        AssociatedToVentilation             = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 116, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        RadiatorsState                      = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 117, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        UnderfloorHeatingCoolingState       = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 118, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        DryingState                         = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 119, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        ThermalIntegrationState             = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 120, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        VentilationState                    = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 121, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        BlockingSourceRadiators             = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 122, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        BlockingSourceUnderfloorHC          = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 123, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        BlockingSourceDrying                = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 124, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        BlockingSourceIntegration           = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 125, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        BlockingSourceVentilation           = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 126, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        RoomType                            = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 127, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1)
        AssociatedHeatingSource             = RoomRegisterRepresentation(RegisterType.INPUT_REGISTER, 128, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1, _roomType=RegisterRoomTypeSupport.DUMMY_ONLY)

        #Holding Registers
        Name                                = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 101, 16, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.STRING)
        Mode                                = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 117, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1)
        ModeOverride                        = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 118, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1)
        TemperatureSetpoint                 = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 119, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_D2_FP100, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        UserInterfaceAccessLevel            = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 120, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        StandybyTemperature                 = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 121, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_D2_FP100)
        VacationTemperature                 = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 122, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_D2_FP100)
        ExcludeFromVacation                 = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 123, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1)
        AdaptiveMode                        = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 124, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_U1, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        ThermalIntegrationHeatingOffset     = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 125, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_D2_FP100, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        ThermalIntegrationHysteresis        = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 126, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_D2_FP100, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        HumidityThresholdHeating            = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 127, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_D2_FP100, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        HumidityThresholdCooling            = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 128, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_D2_FP100, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        HumidityHysteresis                  = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 129, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_D2_FP100, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        DryingCoolingWaterOffset            = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 130, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_D2_FP100, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        DryingCoolingWaterOffsetHysteresis  = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 131, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_D2_FP100, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        DewPointCoolingThreshold            = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 132, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_D2_FP100, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        DewPointCoolingThresholdHysteresis  = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 133, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_D2_FP100, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        HumidityHighAlarmLimit              = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 134, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_D2_FP100, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY)
        TemperaturePreset                   = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 135, 1, _objectType=RegisterObjectType.ROOM, _roomType=RegisterRoomTypeSupport.DUMMY_ONLY) #Acceptable values: 0 = ECO, 1 = Comfort, 2 = ExtraComfort
        TemperatureSetpointUniversal        = RoomRegisterRepresentation(RegisterType.HOLDING_REGISTER, 136, 1, _objectType=RegisterObjectType.ROOM, _dataType=RegisterDataType.VAL_D2_FP100, _roomType=RegisterRoomTypeSupport.NORMAL_ONLY) #READ ONLY

    class Outdoors:
        #Discrete Inputs
        AggregatedWarning                   = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 3301, 1, _objectType=RegisterObjectType.OUTDOOR)
        AggregatedError                     = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 3302, 1, _objectType=RegisterObjectType.OUTDOOR)
        LowBatteryWarning                   = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 3303, 1, _objectType=RegisterObjectType.OUTDOOR)
        PeripheryLostError                  = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 3304, 1, _objectType=RegisterObjectType.OUTDOOR)

        #Input Registers
        AirTemperature                      = RegisterRepresentation(RegisterType.INPUT_REGISTER, 3301, 1, _objectType=RegisterObjectType.OUTDOOR, _dataType=RegisterDataType.VAL_D2_FP100)
        AirTemperatureFiltered              = RegisterRepresentation(RegisterType.INPUT_REGISTER, 3302, 1, _objectType=RegisterObjectType.OUTDOOR, _dataType=RegisterDataType.VAL_D2_FP100)
        AirTemperatureGeometrical           = RegisterRepresentation(RegisterType.INPUT_REGISTER, 3303, 1, _objectType=RegisterObjectType.OUTDOOR, _dataType=RegisterDataType.VAL_D2_FP100)
        #AirHumidity                        = RegisterRepresentation(RegisterType.INPUT_REGISTER, 3304, 1, _objectType=RegisterObjectType.OUTDOOR, _dataType=RegisterDataType.VAL_D2_FP100) #Not Implemented 
        #AirCO2                             = RegisterRepresentation(RegisterType.INPUT_REGISTER, 3305, 1, _objectType=RegisterObjectType.OUTDOOR, _dataType=RegisterDataType.VAL_D2_FP100) #Not Implemented
        #LightLevel                         = RegisterRepresentation(RegisterType.INPUT_REGISTER, 3306, 1, _objectType=RegisterObjectType.OUTDOOR, _dataType=RegisterDataType.VAL_D2_FP100) #Not Implemented

        #Holding Registers
        Name                                = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 3301, 16, _objectType=RegisterObjectType.OUTDOOR, _dataType=RegisterDataType.STRING) #READ ONLY#Fixed to outdoor - futureproofing
        AirTempBMSOverride                  = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 3317, 1, _objectType=RegisterObjectType.OUTDOOR, _dataType=RegisterDataType.VAL_D2_FP100) #Disalbed when value = 327.67

        #reserve

    class DHWControllers:
        #Discrete Inputs
        AggregatedWarning                   = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6501, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _minVersion=RegisterImplementationVersion.V1_0)
        AggregatedError                     = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6502, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _minVersion=RegisterImplementationVersion.V1_0)
        RetentiveLowEnergyWarning           = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6503, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _minVersion=RegisterImplementationVersion.V1_0)
        TempHighError                       = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6504, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _minVersion=RegisterImplementationVersion.V1_0)
        MotorFailureError                   = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6505, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _minVersion=RegisterImplementationVersion.V1_0)
        DHISensorFailureError               = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6506, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _minVersion=RegisterImplementationVersion.V1_0)
        DHOSensorFailureError               = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6507, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _minVersion=RegisterImplementationVersion.V1_0)
        DHWSensorFailureError               = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6508, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _minVersion=RegisterImplementationVersion.V1_0)
        DCWSensorFailureError               = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6509, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _minVersion=RegisterImplementationVersion.V1_0)
        PressureHighWarning                 = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6510, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _minVersion=RegisterImplementationVersion.V3_0)
        PresuureLowWarning                  = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6511, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _minVersion=RegisterImplementationVersion.V3_0)
        PressureCriticalLowError            = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6512, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _minVersion=RegisterImplementationVersion.V3_0)
        FlowSensorFailureError              = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6513, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _minVersion=RegisterImplementationVersion.V3_2)

        #Input Registers
        DesiredTemperature                  = RegisterRepresentation(RegisterType.INPUT_REGISTER, 6501, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_D2_FP100)  
        State                               = RegisterRepresentation(RegisterType.INPUT_REGISTER, 6502, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_U1) #Values:1 = IDLE, 2 = HEATING, 3 =  BYPASS, 4 = BLOCKED_HEATING, 5 = BLOCKED_BYPASS
        BlockingSource                      = RegisterRepresentation(RegisterType.INPUT_REGISTER, 6503, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_U1)
        CirculationState                    = RegisterRepresentation(RegisterType.INPUT_REGISTER, 6504, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_U1)
        MeasuredTemperature                 = RegisterRepresentation(RegisterType.INPUT_REGISTER, 6505, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_D2_FP100)
        SourceInletTemperature              = RegisterRepresentation(RegisterType.INPUT_REGISTER, 6506, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_D2_FP100)
        SourceReturnTemperature             = RegisterRepresentation(RegisterType.INPUT_REGISTER, 6507, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_D2_FP100)
        Pressure                            = RegisterRepresentation(RegisterType.INPUT_REGISTER, 6508, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_D2_FP100)
        DomesticColdWaterTemperature        = RegisterRepresentation(RegisterType.INPUT_REGISTER, 6509, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_D2_FP100)
        DomesticColdWaterFlow               = RegisterRepresentation(RegisterType.INPUT_REGISTER, 6510, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_D2)
        ValvePosition                       = RegisterRepresentation(RegisterType.INPUT_REGISTER, 6511, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_D2_FP100)
        BoostPumpState                      = RegisterRepresentation(RegisterType.INPUT_REGISTER, 6512, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_U1) #Values: 0 = OFF, 1 = ON
        
        #Holding Registers
        Name                                = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6501, 16, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.STRING)
        Mode                                = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6517, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_U1)
        UserInterfaceAccessLevel            = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6518, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_U1)
        BlockRequest                        = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6519, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_U1) #Values: 0 = NONE, 1 = BLOCK_REQUEST
        PowerConsumptionLimit               = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6520, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_U2)
        TemperatureSetpoint                 = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6521, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_D2_FP100)
        BypassTemperature                   = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6522, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_D2_FP100)
        CirculationPumpPresent              = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6523, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_U1)
        CirculationInletTemperature         = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6524, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_D2_FP100)
        ExcludeFromVacation                 = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6525, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_U1)
        ExcludeFromStandby                  = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6526, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_U1)
        BoostPumpMode                       = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6527, 1, _objectType=RegisterObjectType.DHW_CONTROLLERS, _dataType=RegisterDataType.VAL_U1) #Values: 0 = OFF, 1 = LOW, 2 = HIGH

    class DHWTanks:
        #Discrete Inputs
        AggregatedWarning                   = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6601, 1, _objectType=RegisterObjectType.DHW_TANKS)
        AggregatedError                     = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6602, 1, _objectType=RegisterObjectType.DHW_TANKS)
        CleaningProcessFailWarning          = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6603, 1, _objectType=RegisterObjectType.DHW_TANKS)
        TankTempSensorFailError             = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6604, 1, _objectType=RegisterObjectType.DHW_TANKS)
        CirculationReturnTempSensorFailError= RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6605, 1, _objectType=RegisterObjectType.DHW_TANKS)
        SourceReturnTempSensorFailError     = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6606, 1, _objectType=RegisterObjectType.DHW_TANKS)
        SourceInletTempSensorFailError      = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6607, 1, _objectType=RegisterObjectType.DHW_TANKS)
        SourceInletTempTooLowWarning        = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6608, 1, _objectType=RegisterObjectType.DHW_TANKS)
        PeripheryLowBatteryWarning          = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6609, 1, _objectType=RegisterObjectType.DHW_TANKS)
        ParipheryUnreachableError           = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 6610, 1, _objectType=RegisterObjectType.DHW_TANKS)

        #Input Registers
        MeasuredTemperature                 = RegisterRepresentation(RegisterType.INPUT_REGISTER, 6601, 1, _objectType=RegisterObjectType.DHW_TANKS, _dataType=RegisterDataType.VAL_D2_FP100)
        DesiredTemperature                  = RegisterRepresentation(RegisterType.INPUT_REGISTER, 6602, 1, _objectType=RegisterObjectType.DHW_TANKS, _dataType=RegisterDataType.VAL_D2_FP100)
        State                               = RegisterRepresentation(RegisterType.INPUT_REGISTER, 6603, 1, _objectType=RegisterObjectType.DHW_TANKS, _dataType=RegisterDataType.VAL_U1)
        BlockingSource                      = RegisterRepresentation(RegisterType.INPUT_REGISTER, 6604, 1, _objectType=RegisterObjectType.DHW_TANKS, _dataType=RegisterDataType.VAL_U1)
        CirculationState                    = RegisterRepresentation(RegisterType.INPUT_REGISTER, 6605, 1, _objectType=RegisterObjectType.DHW_TANKS, _dataType=RegisterDataType.VAL_U1)
        CircualtionReturnTemperature        = RegisterRepresentation(RegisterType.INPUT_REGISTER, 6606, 1, _objectType=RegisterObjectType.DHW_TANKS, _dataType=RegisterDataType.VAL_D2_FP100)
        SourceInletTemperature              = RegisterRepresentation(RegisterType.INPUT_REGISTER, 6607, 1, _objectType=RegisterObjectType.DHW_TANKS, _dataType=RegisterDataType.VAL_D2_FP100)
        SourceReturnTemperature             = RegisterRepresentation(RegisterType.INPUT_REGISTER, 6608, 1, _objectType=RegisterObjectType.DHW_TANKS, _dataType=RegisterDataType.VAL_D2_FP100)
        
        #Holding Registers
        Name                                = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6601, 16, _objectType=RegisterObjectType.DHW_TANKS, _dataType=RegisterDataType.STRING)
        Mode                                = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6617, 1, _objectType=RegisterObjectType.DHW_TANKS, _dataType=RegisterDataType.VAL_U1)
        CirculationCooldownTime             = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6618, 1, _objectType=RegisterObjectType.DHW_TANKS, _dataType=RegisterDataType.VAL_U2)
        CirculationStopTempDifference       = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6619, 1, _objectType=RegisterObjectType.DHW_TANKS, _dataType=RegisterDataType.VAL_D2_FP100)
        SourceReturnTemperatureLimit        = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6620, 1, _objectType=RegisterObjectType.DHW_TANKS, _dataType=RegisterDataType.VAL_D2_FP100)
        TemperatureSetpoint                 = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6621, 1, _objectType=RegisterObjectType.DHW_TANKS, _dataType=RegisterDataType.VAL_D2_FP100)
        VacationTemperature                 = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6622, 1, _objectType=RegisterObjectType.DHW_TANKS, _dataType=RegisterDataType.VAL_D2_FP100)
        CleaningTemperature                 = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6623, 1, _objectType=RegisterObjectType.DHW_TANKS, _dataType=RegisterDataType.VAL_D2_FP100)
        StandbyTemperature                  = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6624, 1, _objectType=RegisterObjectType.DHW_TANKS, _dataType=RegisterDataType.VAL_D2_FP100)
        ExcludeFromVacation                 = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6625, 1, _objectType=RegisterObjectType.DHW_TANKS, _dataType=RegisterDataType.VAL_U1)
        ExcludeFromStandby                  = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 6626, 1, _objectType=RegisterObjectType.DHW_TANKS, _dataType=RegisterDataType.VAL_U1)

        #reserve

    class ITCCircuits:
        #Discrete Inputs
        AggregatedWarning                   = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 7301, 1, _objectType=RegisterObjectType.ITC_CIRCUITS)
        AggregatedError                     = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 7302, 1, _objectType=RegisterObjectType.ITC_CIRCUITS)
        InletSensorFailureError             = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 7303, 1, _objectType=RegisterObjectType.ITC_CIRCUITS)
        ServoFailureError                   = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 7304, 1, _objectType=RegisterObjectType.ITC_CIRCUITS)
        ReturnSensorFailureError            = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 7305, 1, _objectType=RegisterObjectType.ITC_CIRCUITS)
        OutdoorSensorFailureError           = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 7306, 1, _objectType=RegisterObjectType.ITC_CIRCUITS)
        HighTempCutoffActivatedError        = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 7307, 1, _objectType=RegisterObjectType.ITC_CIRCUITS)
        FrostProtectionActivatedError       = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 7308, 1, _objectType=RegisterObjectType.ITC_CIRCUITS)

        #Input Registers
        State                               = RegisterRepresentation(RegisterType.INPUT_REGISTER, 7301, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_U1)
        BlockingSource                      = RegisterRepresentation(RegisterType.INPUT_REGISTER, 7302, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_U1)
        PumpDemand                          = RegisterRepresentation(RegisterType.INPUT_REGISTER, 7303, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_U1)
        PumpState                           = RegisterRepresentation(RegisterType.INPUT_REGISTER, 7304, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_U1)
        MeasuredTemperature                 = RegisterRepresentation(RegisterType.INPUT_REGISTER, 7305, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP100)
        DesiredInletTemperature             = RegisterRepresentation(RegisterType.INPUT_REGISTER, 7306, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP100)
        DesiredReturnTemperature            = RegisterRepresentation(RegisterType.INPUT_REGISTER, 7307, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP100)
        MainSupplierTemperature             = RegisterRepresentation(RegisterType.INPUT_REGISTER, 7308, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP100)
        ServoPositionRequest                = RegisterRepresentation(RegisterType.INPUT_REGISTER, 7309, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP100)
        DesiredRoomTemperatureByCustomers   = RegisterRepresentation(RegisterType.INPUT_REGISTER, 7310, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP100)

        #Holding Registers
        Name                                = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7301, 16, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.STRING)
        RegulatorPValue                     = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7317, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP10)
        RegulatorIValue                     = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7318, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_U2)
        RegulatorDHysteresis                = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7319, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP100)
        HeatCurveType                       = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7320, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_U1)
        HeatCurveManualSlope                = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7321, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP10) #Used only in MANUAL mode
        HeatCurveParallelDisplacement       = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7322, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP100)
        HeatCurveMinInlet                   = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7323, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP100)
        HeatCurveMaxInlet                   = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7324, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP100)
        HeatCurveGain                       = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7325, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP10)
        ReturnTemperatureLimiterFunction    = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7326, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_U1)
        ReturnTemperatureMaxLimiterLimit    = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7327, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP100)
        ReturnTemperatureMaxLimiterGain     = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7328, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP10)
        ReturnTempMaxLimiterPriorityOvInlet = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7329, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_U1)
        ReturnTemperatureMinLimiterLimit    = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7330, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP100)
        ReturnTemperatureMinLimiterGain     = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7331, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP10)
        OptimizationBoost                   = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7332, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_U1)
        OptimizationBoostFlow               = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7333, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_U1)
        OptimizationRamping                 = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7334, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_U1)
        OptimizationRampingTime             = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7335, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_U1)
        FrostProtectionMode                 = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7336, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_U1)
        FrostProtectionTemperature          = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7337, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP100)
        HighTempCutoffMode                  = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7338, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_U1)
        HighTempCutoffTemperature           = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7339, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP100)
        CoolingRegualtorPValue              = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7340, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP10)
        CoolingRegualtorIValue              = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7341, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_U2)
        CoolingRegualtorHysteresis          = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7342, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP100)
        CoolingInletTempMin                 = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7343, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP100)
        CoolingInletTempMax                 = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 7344, 1, _objectType=RegisterObjectType.ITC_CIRCUITS, _dataType=RegisterDataType.VAL_D2_FP100)

    class HCCControllers:
        pass

    class HCSource:
        State                               = RegisterRepresentation(RegisterType.INPUT_REGISTER, 8101, 1, ) #todo

    class HCWSourceElements:
        pass #todo

    class HardwareIO:
        class Thermistor:
            T1                              = RegisterRepresentation(RegisterType.INPUT_REGISTER, 12801, 1, RegisterDataType.VAL_D2_FP100, RegisterImplementationVersion.V3_4)
            T2                              = RegisterRepresentation(RegisterType.INPUT_REGISTER, 12802, 1, RegisterDataType.VAL_D2_FP100, RegisterImplementationVersion.V3_4)
            T3                              = RegisterRepresentation(RegisterType.INPUT_REGISTER, 12803, 1, RegisterDataType.VAL_D2_FP100, RegisterImplementationVersion.V3_4)
            T4                              = RegisterRepresentation(RegisterType.INPUT_REGISTER, 12804, 1, RegisterDataType.VAL_D2_FP100, RegisterImplementationVersion.V3_4)
            T5                              = RegisterRepresentation(RegisterType.INPUT_REGISTER, 12805, 1, RegisterDataType.VAL_D2_FP100, RegisterImplementationVersion.V3_4)

        class ProgrammableOutputs:
            pass # Not implemented by Sentio yet

        class ProgrammableInputs:
            pass # Not implemented by Sentio yet

        class PhysicalIO:
            pass # Not implemented by Sentio yet

    class PeripheryInfo:

        #Discrete Inputs
        AggregatedWarning                   = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 51201, 1, RegisterObjectType.PERIPHERIES, RegisterImplementationVersion.V3_0)
        AggregatedError                     = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 51202, 1, RegisterObjectType.PERIPHERIES, RegisterImplementationVersion.V3_0)
        LowBatteryWarning                   = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 51203, 1, RegisterObjectType.PERIPHERIES, RegisterImplementationVersion.V3_0)
        PeripheryLostError                  = RegisterRepresentation(RegisterType.DISCRETE_INPUT, 51204, 1, RegisterObjectType.PERIPHERIES, RegisterImplementationVersion.V3_0)
             
        #Input Registers
        Type                                = RegisterRepresentation(RegisterType.INPUT_REGISTER, 51201, 1, RegisterObjectType.PERIPHERIES, RegisterDataType.VAL_U2, RegisterImplementationVersion.V3_0)
        SN                                  = RegisterRepresentation(RegisterType.INPUT_REGISTER, 51202, 2, RegisterObjectType.PERIPHERIES, RegisterDataType.VAL_U4, RegisterImplementationVersion.V3_0)
        Owner                               = RegisterRepresentation(RegisterType.INPUT_REGISTER, 51204, 1, RegisterObjectType.PERIPHERIES, RegisterDataType.VAL_U2, RegisterImplementationVersion.V3_0)
        SignalStrength                      = RegisterRepresentation(RegisterType.INPUT_REGISTER, 51205, 1, RegisterObjectType.PERIPHERIES, RegisterDataType.VAL_U1, RegisterImplementationVersion.V3_1)

        #Holding Registers
        Name                                = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 51201, 16, RegisterObjectType.PERIPHERIES, RegisterDataType.STRING, RegisterImplementationVersion.V3_0)
    
    class ExternalDevices: # todo
        class Ventilation:
            pass

        class Dehumidifier:
            pass

    """Maps old names to new register interpretations for backward compatibility"""
    DeviceType              = Location.DeviceType
    DeviceHwVersion         = Location.DeviceHwVersion
    DeviceSwVersion         = Location.DeviceSwVersion
    DeviceSwVersionMinor    = Location.DeviceSwVersionMinor
    DeviceSerialNrPrefix    = Location.DeviceSerialNrPrefix
    DeviceSerialNumber      = Location.DeviceSerialNumber
    ModbusMode              = Location.ModbusMode
    HCSourceState           = HCSource.State
    RoomTempSetpoint        = Room.DesiredTemperature
    RoomAirTempActual       = Room.AirTemperature
    RoomFloorTempActual     = Room.FloorTemperature
    RoomRelHumidity         = Room.RelativeHumidity
    RoomCalcDewPoint        = Room.CalculatedDewPoint
    RoomHeatingState        = Room.GeneralHeatingCoolingState
    RoomBlockingReason      = Room.GeneralHeatingCoolingBlockingSource
    RoomName                = Room.Name
    RoomModeOverride        = Room.ModeOverride
    RoomTempSetpChange      = Room.TemperatureSetpoint
    RoomTempSetpVacation    = Room.VacationTemperature
    RoomTempSetpStandby     = Room.StandybyTemperature
    RoomMode                = Room.Mode
    RoomPresetMode          = Room.TemperaturePreset
    RoomCO2Level            = Room.CO2Concentration
    OutdoorTemperature      = Outdoors.AirTemperature
    CMVDeviceName           = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 61001, 32, RegisterDataType.STRING)
    CMVVentilationState     = RegisterRepresentation(RegisterType.INPUT_REGISTER, 61023, 1)
    DHWDeviceName           = DHWControllers.Name
    DehumDeviceName         = RegisterRepresentation(RegisterType.HOLDING_REGISTER, 65001, 32, RegisterDataType.STRING, _objectType = RegisterObjectType.DEHUMIDIFIERS)
    Itc_Name                = ITCCircuits.Name
    Itc_State               = ITCCircuits.State
    Itc_PumpState           = ITCCircuits.PumpState
    Itc_InletTempMeasured   = ITCCircuits.MeasuredTemperature
    Itc_InletTempDesired    = ITCCircuits.DesiredInletTemperature
    Itc_ReturnTemperature   = ITCCircuits.DesiredReturnTemperature
    Itc_SupplierTemperature = ITCCircuits.MainSupplierTemperature