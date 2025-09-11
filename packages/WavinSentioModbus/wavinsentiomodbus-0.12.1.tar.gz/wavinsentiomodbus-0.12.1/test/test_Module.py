import WavinSentioModbus
from WavinSentioModbus.SentioApi import SentioModbus, ModbusType
from WavinSentioModbus.SentioTypes import *
import time
import logging

logging.basicConfig(format='[%(levelname)8s] [%(asctime)s] | %(message)s', level=logging.INFO, datefmt='%m/%d/%Y %H:%M:%S')
logging.info("Starting Tests")

class TestClass:
    def init(self):
        returnValue = 0
        logging.debug("Initialize")
        '''
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
        '''
        self.sentio_api = SentioModbus(ModbusType.MODBUS_TCPIP, "192.168.188.14", _port=512)
        #self.sentio_api = SentioApi.SentioModbus("10.31.229.59", SentioApi.ModbusType.MODBUS_TCPIP)
        #self.sentio_api = SentioApi.SentioModbus(SentioApi.ModbusType.MODBUS_RTU, "/dev/ttyS5", 19200, 1, _loglevel=logging.DEBUG)
        #self.sentio_api = SentioApi.SentioModbus("192.168.188.14")
        if self.sentio_api.connect() == 0:
            #logging.error("---- Initializing device data start")
            if self.sentio_api.initialize() == 0:
                logging.debug("Succesfully initialized Sentio device")
            else:
                returnValue = -1
        else:
            logging.error("Failed to connect!")
            returnValue = -1
        return returnValue


    def detectGlobalPeripherals(self):
        status = self.sentio_api.detectDHW()
        if status:
            logging.info("DHW device active")
        else:
            logging.info("DHW device not active")
        status = self.sentio_api.detectCMV()
        if status:
            logging.info("CMV device active")
        else:
            logging.info("CMV device not active")
        status = self.sentio_api.detectDehumidifiers()
        i = 0
        for s in status:
            i = i + 1
            if s == True:
                logging.info("Dehumidification {0} device active".format(i))
            else:
                logging.info("Dehumidification {0} device inactive".format(i))
        
    def readData(self):
        logging.info("DeviceType           = {0}".format(self.sentio_api._sentioData.device_type))
        logging.info("SerialNumber         = {0}".format(self.sentio_api._sentioData.serial_number))
        logging.info("FW Major             = {0}".format(self.sentio_api._sentioData.firmware_version_major))
        logging.info("FW Minor             = {0}".format(self.sentio_api._sentioData.firmware_version_minor))
        #self.sentio_api.readCMVDeviceData()

    def cleanup(self):
        self.sentio_api.disconnect()
    
    def updateData(self):
        self.sentio_api.updateData()

    def showRooms(self):
        #self.sentio_api.updateRoomData()
        rooms = self.sentio_api.availableRooms
        #logging.info("-- available rooms: {0}".format(rooms))
        for room in rooms:
            logging.info("-- {0}".format(room))
            logging.info("-- Mode {0}".format(room.getRoomMode()))
            logging.info("-- Setpoint {0} °C".format(room.getRoomSetpoint()))
            logging.info("-- CurrTemp {0} °C".format(room.getRoomActualTemperature()))
            logging.info("-- RelHumid {0}%".format(room.getRoomRelativeHumidity()))
            logging.info("-- FloorTmp {0} °C".format(room.getRoomFloorTemperature()))
            logging.info("-- DewPoint {0} °C".format(room.getRoomCalculatedDewPoint()))
            logging.info("-- CO2Level {0} ppm".format(room.getRoomCO2Level()))
            logging.info("-- HeatingState = {0}".format(room.getRoomHeatingState()))
            if room.roomBlockingMode != None:
                logging.info("-- Blocking reason = {0}".format(room.roomBlockingMode))

    def getRoom(self, roomIndex):
        rooms = self.sentio_api.getRooms()
        for room in rooms:
            if room.index == roomIndex:
                return room
        return None

    def showItcCircuits(self):
        for itcCircuit in self.sentio_api.availableItcs:
            logging.info("-- {0}".format(itcCircuit.name))
            logging.info("-- Index      {0}".format(itcCircuit.index))
            logging.info("-- State      {0}".format(itcCircuit._state))
            logging.info("-- PumpState  {0}".format(itcCircuit._pumpState))
            if itcCircuit._inletMeasured:
                logging.info("-- InletTemp  {0} °C".format(itcCircuit._inletMeasured))
            if itcCircuit._inletDesired:
                logging.info("-- InletDes   {0} °C".format(itcCircuit._inletDesired))
            if itcCircuit._returnTemp:
                logging.info("-- ReturnTemp {0} °C".format(itcCircuit._returnTemp))
            if itcCircuit._supplierTemp:
                logging.info("-- SupplierTmp{0} °C".format(itcCircuit._supplierTemp))


    def getHCState(self):
        logging.info("Main HC Source state {0}".format(self.sentio_api._sentioData.hc_source_state))

    def getoutdoorTemp(self):
        logging.info("Outdoor temp = {0} °C".format(self.sentio_api._sentioData.outdoor_temperature))

    def getRoomHeatingState(self, roomIndex):
        heatingState = self.sentio_api.getRoomHeatingState(roomIndex)
        logging.info("Room {0} state {1}".format(roomIndex, heatingState))
        return heatingState

    def getRoomMode(self, roomIndex):
        roomMode = self.sentio_api.getRoomMode(roomIndex)
        logging.info("Room {0} state {1}".format(roomIndex, roomMode))
        return roomMode

    def setRoomToSchedule(self, roomIndex):
        self.sentio_api.setRoomMode(roomIndex, SentioRoomMode.SCHEDULE)
        pass
    
    def setRoomToManual(self, roomIndex):
        self.sentio_api.setRoomMode(roomIndex, SentioRoomMode.MANUAL)
        pass

    def setRoomTemperature(self, roomIndex, temperatureSetpoint):
        self.sentio_api.setRoomSetpoint(roomIndex, temperatureSetpoint)



#Execute Tests
testInstance = TestClass()
assert testInstance.init() == 0, "Failed to connect"
testInstance.readData()
testInstance.detectGlobalPeripherals()

testInstance.updateData()
testInstance.showRooms()

#Show rooms and outdoor temp
testInstance.getoutdoorTemp()
testInstance.showRooms()

testInstance.showItcCircuits()



#cleanup
testInstance.cleanup()