import logging 
#Api regisers and defaults
from pymodbus.client import ModbusTcpClient
from pymodbus.client import ModbusSerialClient
from pymodbus.exceptions import ModbusException, ParameterException
from pymodbus.pdu import ExceptionResponse
import struct

#import Defaults
from .Defaults import Defaults
from .SentioRegisterMap import *
from .SentioTypes import *

class ModbusWrapper:
    def __init__(self, client, device_id):
        self.client = client
        self.device_id = device_id

    def registers_to_string(self, registers):
        """Convert Modbus registers to a UTF-8 string."""
        byte_array = b''.join(struct.pack(">H", reg) for reg in registers)
        return byte_array[:44].decode("utf-8").rstrip("\x00")

    def writeRegister(self, registerMapObject, value, _subIndex=0):
        try:
            if _subIndex != 0:
                address = self._compute_address(registerMapObject, _subIndex)
            else:
                address = registerMapObject.address

            logging.debug(f"Writing to register: {registerMapObject}, resolved address: {address}")

            if registerMapObject.regType in (RegisterType.INPUT_REGISTER, RegisterType.DISCRETE_INPUT):
                logging.error(f"Cannot write to {registerMapObject.regType} registers.")
                return -1

            if registerMapObject.regType == RegisterType.HOLDING_REGISTER:
                return self.client.write_register(address, value, device_id=self.device_id)

            logging.error(f"Unknown register type: {registerMapObject.regType}")
            return -1

        except Exception as e:
            logging.exception(f"Error writing to register: {e}")
            return -1

    def readRegister(self, registerMapObject, _subIndex=0):
        try:
            if _subIndex != 0:
                address = self._compute_address(registerMapObject, _subIndex)
            else:
                address = registerMapObject.address
                
            logging.debug(f"Reading register: {registerMapObject}, resolved address: {address}")

            response = self._read_from_client(registerMapObject, address)

            if not response or response.isError():
                logging.warning(f"Modbus read failed at address {address} with type {registerMapObject.regType}")
                return None

            return self._decode_response(registerMapObject, response)

        except Exception as e:
            logging.exception(f"Exception reading register at address {registerMapObject.address}: {e}")
            return None

    def _compute_address(self, registerMapObject, sub_index):
        """Calculate the adjusted register address based on object type and sub-index."""
        if registerMapObject.objectType in {
            RegisterObjectType.ROOM,
            RegisterObjectType.DEHUMIDIFIERS,
            RegisterObjectType.ITC_CIRCUITS,
            RegisterObjectType.HCCS,
            RegisterObjectType.PGOS,
            RegisterObjectType.PERIPHERIES,
            RegisterObjectType.VENTILATIONS,
            RegisterObjectType.DHW_CONTROLLERS,
            RegisterObjectType.DHW_TANKS,
            RegisterObjectType.OUTDOOR
        }:
            adjusted = sub_index * 100 + registerMapObject.address
            logging.debug(f"Adjusted address for {registerMapObject.objectType}: {adjusted}")
            return adjusted
        return registerMapObject.address

    def _read_from_client(self, registerMapObject, address):
        """Read registers from the client based on register type."""
        if registerMapObject.regType == RegisterType.INPUT_REGISTER:
            return self.client.read_input_registers(address, count=registerMapObject.count, device_id=self.device_id)
        elif registerMapObject.regType == RegisterType.HOLDING_REGISTER:
            return self.client.read_holding_registers(address, count=registerMapObject.count, device_id=self.device_id)
        elif registerMapObject.regType == RegisterType.DISCRETE_INPUT:
            logging.warning("Read for DISCRETE_INPUT is not supported.")
        return None

    def _decode_response(self, registerMapObject, response):
        """Decode the Modbus response based on the register's data type."""
        data_type = registerMapObject.dataType
        count = registerMapObject.count
        registers = getattr(response, "registers", [])

        if isinstance(response, ExceptionResponse) or not registers:
            logging.error(f"Invalid Modbus response: {response}")
            return None

        # Handle numeric types
        if data_type in {RegisterDataType.VAL_U1, RegisterDataType.VAL_U2, RegisterDataType.VAL_U4}:
            return self._decode_numeric(registers, count)

        # Handle string type
        if data_type == RegisterDataType.STRING:
            return self.registers_to_string(registers)

        # Handle fixed-point signed 2-byte /100
        if data_type == RegisterDataType.VAL_D2_FP100:
            return self._decode_signed_fp(registers, count, 100)
        
        if data_type == RegisterDataType.VAL_D2_FP10:
            return self._decode_signed_fp(registers, count, 10)
        
        if data_type == RegisterDataType.VAL_D2:
            return self._decode_signed_fp(registers, count, 1)

        logging.warning(f"No decoder implemented for data type: {data_type}")
        return None

    def _decode_numeric(self, registers, count):
        if count == 1:
            return registers[0]
        if count == 2:
            return self.client.convert_from_registers(registers, data_type=self.client.DATATYPE.INT32)
        if count == 4:
            return self.client.convert_from_registers(registers, data_type=self.client.DATATYPE.INT64)
        logging.error(f"Unsupported numeric register count: {count}")
        return None       
    
    def _decode_signed_fp(self, register, count, divider=100):
        value = register[0]

        if count != 1:
            logging.error(f"Unsupported count for VAL_D2_FP100: {count}")
            return None
        
        if value == 65535:
          return None  # 'nan' value
        elif 0 <= value <= 32767:
            return value / divider
        elif 32768 <= value <= 65534:
            return (value - 65536) / divider
        else:
            raise ValueError("Register out of valid range (0 to 65535)")