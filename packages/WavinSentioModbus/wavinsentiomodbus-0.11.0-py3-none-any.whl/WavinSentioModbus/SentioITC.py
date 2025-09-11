import logging

from .SentioRegisterMap import *
from .ModbusWrapper import ModbusWrapper
from .SentioTypes import *
from .Defaults import Defaults

class SentioItcHandler:
    def __init__(self, api:ModbusWrapper):
        self._detectedItcs = []
        self._api = api
        pass

    def initialize(self):
        self._detectedItcs=[]
        for itcCtr in range(Defaults.MaxNumberOfItcs):
            try:
                value = self._api.readRegister(SentioRegisterMap.Itc_Name, _subIndex = itcCtr)
                if value != None:
                    self._detectedItcs.append(SentioItcCircuit(itcCtr, value, self._api))
                #else:
                    #logging.error("ITC Circuit {0} not found".format(itcCtr))
            except Exception as e:
                logging.exception("Exception reading ITC Circuit {0}".format(e))
                return -1

        #for circuit in self._detectedItcs:
        #    logging.debug("ITC Circuit ID={0} | Name={1}".format(circuit.index, circuit.name))
        return 0
    
    def updateData(self):
        for itc in self._detectedItcs:
            itc.updateData()

class SentioItcCircuit:
    def __init__(self, index, name, api:ModbusWrapper):
        self.index = index;
        self.name = name;
        self._state         = None
        self._pumpState     = None
        self._inletMeasured = None
        self._inletDesired  = None
        self._returnTemp    = None
        self._supplierTemp  = None
        self._api = api

    def GetItcIndex(self):
        return self.index
    
    @property
    def getPumpState(self) -> ITC_PumpState:
        return self._pumpState
    
    @property
    def getInletMeasured(self) -> float:
        return self._inletMeasured
    
    @property
    def getInletMeasured(self) -> float:
        return self._inletMeasured
        
    @property
    def getInletDesired(self) -> float:
        return self._inletDesired
    @property
    def getSupplierTemp(self) -> float:
        return self._supplierTemp
    
    @property
    def getReturnTemp(self) -> float:
        return self._returnTemp
    
    def updateData(self):
        state = self._api.readRegister(SentioRegisterMap.Itc_State, _subIndex = self.index)
        if state:
            self._state          = SentioHeatingStates(state)
        pump = self._api.readRegister(SentioRegisterMap.Itc_PumpState, _subIndex = self.index)
        if pump:
            self._pumpState = ITC_PumpState(pump)
        self._inletMeasured  = self._api.readRegister(SentioRegisterMap.Itc_InletTempMeasured, _subIndex = self.index)
        if(self._inletMeasured == Defaults.InvalidFP2_100):
            self._inletMeasured = None
        self._inletDesired   = (self._api.readRegister(SentioRegisterMap.Itc_InletTempDesired, _subIndex = self.index))
        if(self._inletDesired == Defaults.InvalidFP2_100):
            self._inletDesired = None
        self._returnTemp     = (self._api.readRegister(SentioRegisterMap.Itc_ReturnTemperature, _subIndex = self.index))
        if(self._returnTemp == Defaults.InvalidFP2_100):
            self._returnTemp = None
        self._supplierTemp   = (self._api.readRegister(SentioRegisterMap.Itc_SupplierTemperature, _subIndex = self.index))
        if(self._supplierTemp == Defaults.InvalidFP2_100):
            self._supplierTemp = None
        pass

    def printCircuit(self):
        logging.debug("ITC Circuit ID={0} | Name={1} || state {2}, Pump {3}, Inlet = {4} desired={5}, Return ={6}, Supplier ={7}".format(self.index, self.name, self._state, self._pumpState, self._inletMeasured, self._inletDesired, self._returnTemp, self._supplierTemp))
        print("ITC Circuit ID={0} | Name={1} || state {2}, Pump {3}, Inlet = {4} desired={5}, Return ={6}, Supplier ={7}".format(self.index, self.name, self._state, self._pumpState, self._inletMeasured, self._inletDesired, self._returnTemp, self._supplierTemp))