import logging

from pymodbus.client import ModbusTcpClient
from pymodbus.client import ModbusSerialClient

#Api regisers and defaults
#import Defaults
from .Defaults import Defaults
from .SentioRegisterMap import *
from .SentioTypes import *
from .ModbusWrapper import ModbusWrapper
from .SentioRoom import SentioRoom, SentioRoomHandler
from .SentioITC import SentioItcCircuit, SentioItcHandler
from .SentioSensors import SentioSensors

class ModbusType(Enum):
    MODBUS_TCPIP = 0
    MODBUS_RTU = 1

class SentioModbus:
    def __init__(self, 
        _ModbusType:ModbusType = ModbusType.MODBUS_TCPIP,
        _host: str = "",
        _baudrate: int = Defaults.BaudRate,
        _Device_Id: int = Defaults.Device_Id,
        _port: int = Defaults.TcpPort,
        _loglevel = logging.ERROR,
        _parity = 'E',
        _stopbits = 1
    ):
        self.host = _host
        self.Device_Id = _Device_Id
        self.port = _port
        self.modbusType = _ModbusType
        self.baudrate = _baudrate
        self.parity = _parity
        self.stopbits = _stopbits

        logging.basicConfig(format='%(levelname)s %(asctime)s | %(message)s', level=_loglevel, datefmt='%m/%d/%Y %H:%M:%S')
        self.detectedRooms=[]
        pass

    def connectModbusRTU(self):
        try:
            self.client = ModbusSerialClient(method='rtu', port=self.host, baudrate=self.baudrate, parity=self.parity, stopbits=self.stopbits) #fixed parity & stopbits?
            result = self.client.connect()
            if result == True:
                self.modbusWrapper = ModbusWrapper(self.client, self.Device_Id)
                logging.debug("Connected {0}".format(result))
                #super().connect()
                return 0
            else:
                logging.error("Failed to connect")
                return -1
        except Exception as error:
            logging.exception("Failed to connect: {0} ".format(error))
            return -1

    def connectModbusTcpIp(self):
        try:
            self.client = ModbusTcpClient(self.host)
            logging.debug("Connecting")
            result = self.client.connect()
            if result == True:
                self.modbusWrapper = ModbusWrapper(self.client, self.Device_Id)
                logging.debug("Connected {0}".format(result))
                #super().connect()
                return 0
            else:
                logging.error("Failed to connect")
                return -1
        except:
            logging.exception("Failed to connect")
            raise NoConnectionPossible("Failed to connect")

    def connect(self):
        if self.modbusType == ModbusType.MODBUS_TCPIP:
           return self.connectModbusTcpIp()
        elif self.modbusType == ModbusType.MODBUS_RTU:
            return self.connectModbusRTU()
        elif self.modbusType == 0:
            return self.connectModbusTcpIp() #ugly fallback
        else: 
            logging.exception("Wrong modbus type detected {0}".format(self.modbusType))
            raise AttributeError("Wrong modbus type detected {0}".format(self.modbusType))

    def disconnect(self):
        return self.client.close()

    def initialize(self):
        self._sentioData = SentioSensors(self.modbusWrapper)
        self._roomData = SentioRoomHandler(self.modbusWrapper)
        self._itcData = SentioItcHandler(self.modbusWrapper)

        if self._sentioData.initialize() == 0:
            if self._roomData.initialize() == 0:
                return self._itcData.initialize()
            else:
                logging.error("Failed to initialize room data")
        else:
            logging.error("Failed to initialize Sentio data")
        return -1

    def updateData(self):
        self._sentioData.updateData()
        self._roomData.updateData()
        self._itcData.updateData()
        pass

    def detectDHW(self):
        output = self.modbusWrapper.readRegister(SentioRegisterMap.DHWDeviceName)
        return output != None #if None is returned, it is not valid

    def detectCMV(self):
        output = self.modbusWrapper.readRegister(SentioRegisterMap.CMVDeviceName)
        return output != None

    def detectDehumidifiers(self):
        returnValue=[]
        for i in range(4):
            returnValue.append((self.modbusWrapper.readRegister(SentioRegisterMap.DehumDeviceName, _subIndex=i) != None))
        return returnValue

    @property
    def sentioData(self):
        return self._sentioData
    
    @property
    def availableRooms(self):
        return self._roomData._detectedRooms
    
    @property
    def availableItcs(self):
        return self._itcData._detectedItcs
    
class NoConnectionPossible(Exception):
    pass