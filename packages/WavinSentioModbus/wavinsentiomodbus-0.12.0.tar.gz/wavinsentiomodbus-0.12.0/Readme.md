# Wavin Sentio API

Wavin sentio modbus interface usable to control the Wavin Sentio devices

## dependencies
 - PyModbus (https://pymodbus.readthedocs.io/en/latest/readme.html)

### Install Dependencies (if required)
```
python -m pip install pymodbus
```

## Usage
Some snippets on example usage:
### Construct Modbus TCP
```
sentio_api = SentioModbus("10.0.0.10", SentioApi.ModbusType.MODBUS_TCPIP)
```

### Construct Modbus RTU (Serial)
```
sentio_api = SentioModbus("/dev/ttyS5", SentioApi.ModbusType.MODBUS_RTU, 19200, 1, _loglevel=logging.DEBUG)
```

### Connect
Connect using the python modbus library
```
if sentio_api.connect() == 0:
  if sentio_api.initialize() == 0:
    print("Connected to Sentio and initialized devicedata")
  else:
    print("physical connected succeeded but initialization failed, check logs")
else:
  print("Connection failed")
```
for more detailed usage see test folder where functional tests are executed

## Run Tests
```
python -m unittest test.test_SentioApi
```

## Release History
TBD

## Status
 - [x] Modbus
 - [x] Logging
 - [x] Auto detect Rooms
 - [x] Auto detect Global Peripherals
   - [x] CMV
   - [x] (DE)Humidifiers
   - [x] DHW
- [ ] Validate and Use Global Peripherals
  - [ ] CMV
  - [ ] DHW
  - [ ] (DE)Humidifiers
- [x] Room Control 
    - [x] Set Temperature
    - [x] Read Temperature

## TODO
- [ ] Fix Todo's in code
- [ ] Fix automatic versioning and publishing. 

## Running
`
pip install virtualenv
virtualenv venv
.\venv\Scripts\activate
pip install --no-cache-dir -r requirements.txt
python test/test_sentioApi.py
`