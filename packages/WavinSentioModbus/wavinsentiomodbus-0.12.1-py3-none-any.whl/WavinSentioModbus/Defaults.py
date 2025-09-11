class Singleton:  # pylint: disable=too-few-public-methods
    """Singleton base class.
    https://mail.python.org/pipermail/python-list/2007-July/450681.html
    """

    def __new__(cls, *args, **kwargs):  # pylint: disable=unused-argument
        """Create a new instance."""
        if "_inst" not in vars(cls):
            cls._inst = object.__new__(cls)
        return cls._inst

class Defaults(Singleton):
    TcpPort = 502
    Device_Id = 1
    SerialNumberLength = 14
    SerialNumberPrefixLen = 4
    SerialNumberPrefix = 1530
    
    MaxNumberOfRooms = 24
    MaxNumberOfOutdoors = 1
    MaxNumberOfItcs = 2
    MaxNumberOfHCCs = 3
    MaxNumberOfPGOs = 8
    MaxNumberOfPeripheries = 64
    MaxNumberOfVentilations = 2
    MaxNumberOfDehumidifiers = 4
    
    InvalidFP2_100 = 327.67
    Invalid_UINT16 = 65535
    BaudRate = 19200