from ctypes import *
import time

# ----- Constants and Configuration -----
# CAN/CANFD constants
VCI_USBCAN2 = 41
STATUS_OK = 1
INVALID_DEVICE_HANDLE = 0
INVALID_CHANNEL_HANDLE = 0
TYPE_CAN = 0
TYPE_CANFD = 1

# CAN message IDs
CAN_ID_AIRBAG_CMD = 0x150
CAN_ID_AIRBAG_RESPONSE = 0x08C

# ----- CAN/CANFD Structures -----
class VCI_INIT_CONFIG(Structure):  
    _fields_ = [("AccCode", c_uint),
                ("AccMask", c_uint),
                ("Reserved", c_uint),
                ("Filter", c_ubyte),
                ("Timing0", c_ubyte),
                ("Timing1", c_ubyte),
                ("Mode", c_ubyte)
                ]  

class VCI_CAN_OBJ(Structure):  
    _fields_ = [("ID", c_uint),
                ("TimeStamp", c_uint),
                ("TimeFlag", c_ubyte),
                ("SendType", c_ubyte),
                ("RemoteFlag", c_ubyte),
                ("ExternFlag", c_ubyte),
                ("DataLen", c_ubyte),
                ("Data", c_ubyte*8),
                ("Reserved", c_ubyte*3)
                ] 
 
class _ZCAN_CHANNEL_CAN_INIT_CONFIG(Structure):
    _fields_ = [("acc_code", c_uint),
                ("acc_mask", c_uint),
                ("reserved", c_uint),
                ("filter",   c_ubyte),
                ("timing0",  c_ubyte),
                ("timing1",  c_ubyte),
                ("mode",     c_ubyte)]

class _ZCAN_CHANNEL_CANFD_INIT_CONFIG(Structure):
    _fields_ = [("acc_code",     c_uint),
                ("acc_mask",     c_uint),
                ("abit_timing",  c_uint),
                ("dbit_timing",  c_uint),
                ("brp",          c_uint),
                ("filter",       c_ubyte),
                ("mode",         c_ubyte),
                ("pad",          c_ushort),
                ("reserved",     c_uint)]

class _ZCAN_CHANNEL_INIT_CONFIG(Union):
    _fields_ = [("can", _ZCAN_CHANNEL_CAN_INIT_CONFIG), ("canfd", _ZCAN_CHANNEL_CANFD_INIT_CONFIG)]

class ZCAN_CHANNEL_INIT_CONFIG(Structure):
    _fields_ = [("can_type", c_uint),
                ("config", _ZCAN_CHANNEL_INIT_CONFIG)]
				
class ZCAN_CAN_FRAME(Structure):
    _fields_ = [("can_id",  c_uint, 29),
                ("err",     c_uint, 1),
                ("rtr",     c_uint, 1),
                ("eff",     c_uint, 1), 
                ("can_dlc", c_ubyte),
                ("__pad",   c_ubyte),
                ("__res0",  c_ubyte),
                ("__res1",  c_ubyte),
                ("data",    c_ubyte * 8)]

class ZCAN_CANFD_FRAME(Structure):
    _fields_ = [("can_id", c_uint, 29), 
                ("err",    c_uint, 1),
                ("rtr",    c_uint, 1),
                ("eff",    c_uint, 1), 
                ("len",    c_ubyte),
                ("brs",    c_ubyte, 1),
                ("esi",    c_ubyte, 1),
                ("__res",  c_ubyte, 6),
                ("__res0", c_ubyte),
                ("__res1", c_ubyte),
                ("data",   c_ubyte * 64)]
				
class ZCAN_Transmit_Data(Structure):
    _fields_ = [("frame", ZCAN_CAN_FRAME), ("transmit_type", c_uint)]

class ZCAN_Receive_Data(Structure):
    _fields_  = [("frame", ZCAN_CAN_FRAME), ("timestamp", c_ulonglong)]

class ZCAN_TransmitFD_Data(Structure):
    _fields_ = [("frame", ZCAN_CANFD_FRAME), ("transmit_type", c_uint)]

class ZCAN_ReceiveFD_Data(Structure):
    _fields_ = [("frame", ZCAN_CANFD_FRAME), ("timestamp", c_ulonglong)]

# ----- CRC Calculation Functions -----
def Crc_CalculateCRC_Profile1(data, length, init_value):
    """Calculate CRC using Profile1 algorithm"""
    crc_save = 0
    crc_temp = init_value

    for i in range(length):
        crc_temp ^= data[i]
        for _ in range(8):
            crc_save = crc_temp
            crc_temp = (crc_temp << 1) & 0xFF
            
            if crc_save & 0x80:
                crc_temp ^= 0x1D

    return crc_temp

def cal_check_sum(msgByteArray):
    """Calculate checksum for CAN message"""
    PID = 0x611D
    protectedDataSize_byte = 2
    crcStartValue = 0x00
    localBuffer = bytearray(3)

    # Extract alive counter
    alive_counter = msgByteArray[1]

    # Set PID based on counter value
    if alive_counter % 2 == 0:
        localBuffer[0] = PID & 0xFF
    else:
        localBuffer[0] = (PID >> 8) & 0xFF

    localBuffer[1] = msgByteArray[0]
    localBuffer[2] = msgByteArray[1]

    return Crc_CalculateCRC_Profile1(localBuffer, 1 + protectedDataSize_byte, crcStartValue)

class CANDriver:
    """CAN Driver class to handle CAN communication"""
    
    def __init__(self, dll_path='/app/demo/libcontrolcanfd.so'):
        """Initialize CAN driver with DLL path"""
        self.dll_path = dll_path
        self.canDLL = None
        self.m_dev = None
        self.dev_ch1 = None  # CAN0
        self.dev_ch2 = None  # CAN1
        self.frame = None
        self.aliveCounter = 0
        
        self._init_can_library()
        
    def _init_can_library(self):
        """Initialize the CAN library and configure function signatures"""
        print('########################################################')
        print('## Chuang Xin USBCANFD python(x64) test program V2.0 ###')
        print('########################################################')
        print(f"Loading CAN library: {self.dll_path}")
        
        self.canDLL = cdll.LoadLibrary(self.dll_path)
        
        # Configure function signatures
        self.canDLL.ZCAN_OpenDevice.restype = c_void_p
        self.canDLL.ZCAN_SetAbitBaud.argtypes = (c_void_p, c_ulong, c_ulong)
        self.canDLL.ZCAN_SetDbitBaud.argtypes = (c_void_p, c_ulong, c_ulong)
        self.canDLL.ZCAN_SetCANFDStandard.argtypes = (c_void_p, c_ulong, c_ulong)
        self.canDLL.ZCAN_InitCAN.argtypes = (c_void_p, c_ulong, c_void_p)
        self.canDLL.ZCAN_InitCAN.restype = c_void_p
        self.canDLL.ZCAN_StartCAN.argtypes = (c_void_p,)
        self.canDLL.ZCAN_Transmit.argtypes = (c_void_p, c_void_p, c_ulong)
        self.canDLL.ZCAN_TransmitFD.argtypes = (c_void_p, c_void_p, c_ulong)
        self.canDLL.ZCAN_GetReceiveNum.argtypes = (c_void_p, c_ulong)
        self.canDLL.ZCAN_Receive.argtypes = (c_void_p, c_void_p, c_ulong, c_long)
        self.canDLL.ZCAN_ReceiveFD.argtypes = (c_void_p, c_void_p, c_ulong, c_long)
        self.canDLL.ZCAN_ResetCAN.argtypes = (c_void_p,)
        self.canDLL.ZCAN_CloseDevice.argtypes = (c_void_p,)

        self.canDLL.ZCAN_ClearFilter.argtypes=(c_void_p,)
        self.canDLL.ZCAN_AckFilter.argtypes=(c_void_p,)
        self.canDLL.ZCAN_SetFilterMode.argtypes=(c_void_p,c_ulong)
        self.canDLL.ZCAN_SetFilterStartID.argtypes=(c_void_p,c_ulong)
        self.canDLL.ZCAN_SetFilterEndID.argtypes=(c_void_p,c_ulong)
    
    def initialize(self):
        """Initialize CAN hardware and channels"""
        self._open_device()
        self._configure_can_channels()
        self._init_can_channels()
        self._prepare_airbag_command_frame()
        return True
        
    def _open_device(self):
        """Open the CAN device"""
        self.m_dev = self.canDLL.ZCAN_OpenDevice(VCI_USBCAN2, 0, 0)
        if self.m_dev == INVALID_DEVICE_HANDLE:
            print("Open Device failed!")
            return False
        print(f"Open Device OK, device handle:0x{self.m_dev:x}")
        return True
        
    def _configure_can_channels(self):
        """Configure the CAN channels with proper settings"""
        # Configure CAN0
        ret = self.canDLL.ZCAN_SetAbitBaud(self.m_dev, 0, 500000)
        if ret != STATUS_OK:
            print("Set CAN0 abit:1M failed!")
            return False
        print("Set CAN0 abit:1M OK!")
        
        ret = self.canDLL.ZCAN_SetDbitBaud(self.m_dev, 0, 500000)
        if ret != STATUS_OK:
            print("Set CAN0 dbit:5M failed!")
            return False
        print("Set CAN0 dbit:5M OK!")

        # Configure CAN1
        ret = self.canDLL.ZCAN_SetAbitBaud(self.m_dev, 1, 500000)
        if ret != STATUS_OK:
            print("Set CAN1 abit:1M failed!")
            return False
        print("Set CAN1 abit:1M OK!")
        
        ret = self.canDLL.ZCAN_SetDbitBaud(self.m_dev, 1, 500000)
        if ret != STATUS_OK:
            print("Set CAN1 dbit:5M failed!")
            return False
        print("Set CAN1 dbit:5M OK!")

        # Set ISO mode for CAN0
        ret = self.canDLL.ZCAN_SetCANFDStandard(self.m_dev, 0, 0)
        if ret != STATUS_OK:
            print("Set CAN0 ISO mode failed!")
            return False
        print("Set CAN0 ISO mode OK!")
        
        # Set ISO mode for CAN1
        ret = self.canDLL.ZCAN_SetCANFDStandard(self.m_dev, 1, 0)
        if ret != STATUS_OK:
            print("Set CAN1 ISO mode failed!")
            return False
        print("Set CAN1 ISO mode OK!")
        return True
        
    def _init_can_channels(self):
        """Initialize and start the CAN channels"""
        # Prepare configuration
        init_config = ZCAN_CHANNEL_INIT_CONFIG()
        init_config.can_type = TYPE_CANFD
        init_config.config.canfd.acc_code = 0x00000000
        init_config.config.canfd.acc_mask = 0xFFFFFFFF  
        init_config.config.canfd.mode = 0

        # Initialize CAN0
        self.dev_ch1 = self.canDLL.ZCAN_InitCAN(self.m_dev, 0, byref(init_config))
        if self.dev_ch1 == INVALID_CHANNEL_HANDLE:
            print("Init CAN0 failed!")
            return False
        print("Init CAN0 OK!")

        # Start CAN0
        ret = self.canDLL.ZCAN_StartCAN(self.dev_ch1)
        if ret != STATUS_OK:
            print("Start CAN0 failed!")
            return False
        print("Start CAN0 OK!")	

        # Initialize CAN1
        self.dev_ch2 = self.canDLL.ZCAN_InitCAN(self.m_dev, 1, byref(init_config))
        if self.dev_ch2 == INVALID_CHANNEL_HANDLE:
            print("Init CAN1 failed!")
            return False
        print("Init CAN1 OK!")

        # Start CAN1
        ret = self.canDLL.ZCAN_StartCAN(self.dev_ch2)
        if ret != STATUS_OK:
            print("Start CAN1 failed!")
            return False
        print("Start CAN1 OK!")
        return True
        
    def _prepare_airbag_command_frame(self):
        """Prepare the frame for sending airbag commands to ECU"""
        self.frame = ZCAN_TransmitFD_Data()
        self.frame.transmit_type = 0      # Normal transmission
        self.frame.frame.eff = 0          # Standard frame format
        self.frame.frame.rtr = 0          # Data frame
        self.frame.frame.brs = 0          # Enable bit rate switching
        self.frame.frame.can_id = CAN_ID_AIRBAG_CMD  # 0x150
        self.frame.frame.len = 3          # Data length = 3 bytes
        
        # Initial payload
        self.frame.frame.data[0] = 128    # Default: passenger airbag deactivate
        self.frame.frame.data[1] = 0      # Alive counter
        self.frame.frame.data[2] = 0      # Checksum
        
    def send_airbag_command(self, enable_airbag):
        """
        Send airbag command
        
        Args:
            enable_airbag (bool): True to enable airbag, False to disable
        
        Returns:
            tuple: (success, data_sent)
        """
        # Set command based on enable flag
        self.frame.frame.data[0] = 129 if enable_airbag else 128
        
        # Update alive counter
        if self.aliveCounter < 14:
            self.aliveCounter += 1
        else:
            self.aliveCounter = 0
            
        self.frame.frame.data[1] = self.aliveCounter
        
        # Calculate and set checksum
        checksum = cal_check_sum(self.frame.frame.data)
        self.frame.frame.data[2] = checksum
        
        # Send frame
        result = self.canDLL.ZCAN_TransmitFD(self.dev_ch1, byref(self.frame), 1)
        data_sent = [hex(self.frame.frame.data[i]) for i in range(self.frame.frame.len)]
        
        # Logging
        print(f"[Driver][send_airbag_command] Airbag command: {data_sent}, result: {result}")
        print(f"[Driver][send_airbag_command] Expected: result = true/1")
        return result > 0, data_sent
        
    def process_loopback(self):
        """
        Process data in loopback mode - simulating ECU responses
        
        Returns:
            tuple: (success, padl_data, pael_data) or (False, None, None)
        """
        ret = self.canDLL.ZCAN_GetReceiveNum(self.dev_ch2, TYPE_CANFD)
        if ret <= 0:
            return False, None, None
            
        rcv_msgs = (ZCAN_ReceiveFD_Data * ret)()
        num = self.canDLL.ZCAN_ReceiveFD(self.dev_ch2, byref(rcv_msgs), ret, 100)
        
        if num <= 0:
            return False, None, None
            
        for i in range(num):
            data = [rcv_msgs[i].frame.data[j] for j in range(rcv_msgs[i].frame.len)]
            print(f"CH2 Received Frame ID: {hex(rcv_msgs[i].frame.can_id)}, Data: [" + 
                  ", ".join([hex(x) for x in data]) + "]")
            
            # Simulate Airbag ECU behavior
            if data[0] == 128:
                print("[Airbag ECU] Deactivate Passenger Airbag")
                padl_data_temp = 0x01  # Disable lamp ON
                pael_data_temp = 0x00  # Enable lamp OFF
            elif data[0] == 129:
                print("[Airbag ECU] Activate Passenger Airbag")
                padl_data_temp = 0x00  # Disable lamp OFF
                pael_data_temp = 0x01  # Enable lamp ON

            # Prepare simulated ECU response
            response = ZCAN_TransmitFD_Data()
            response.transmit_type = 0
            response.frame.eff = 0
            response.frame.rtr = 0
            response.frame.brs = 1
            response.frame.can_id = CAN_ID_AIRBAG_RESPONSE
            response.frame.len = 8  # Standard length for response
            response.frame.data[3] = (padl_data_temp << 3) | (pael_data_temp << 2)  # Set response bits
            
            # Send simulated response
            self.canDLL.ZCAN_TransmitFD(self.dev_ch2, byref(response), 1)
            
            return True, padl_data_temp, pael_data_temp
            
    def receive_airbag_status(self):
        """
        Receive status from airbag ECU
        
        Returns:
            tuple: (success, padl_status, pael_status) or (False, None, None)
        """
        ret_fd = self.canDLL.ZCAN_GetReceiveNum(self.dev_ch1, TYPE_CANFD)
        ret_can = self.canDLL.ZCAN_GetReceiveNum(self.dev_ch1, TYPE_CAN)
        print(f"[Driver][receive_airbag_status] CANFD buffer: {ret_fd}, CAN buffer: {ret_can}")
        
        if ret_fd > 0:
            rcv_msgs = (ZCAN_ReceiveFD_Data * ret_fd)()
            num = self.canDLL.ZCAN_ReceiveFD(self.dev_ch1, byref(rcv_msgs), ret_fd, 100)
            if num > 0:
                for i in range(num):
                    data = [rcv_msgs[i].frame.data[j] for j in range(rcv_msgs[i].frame.len)]
                    print(f"[Driver][receive_airbag_status] CANFD frame ID: {hex(rcv_msgs[i].frame.can_id)}, Data: {[hex(x) for x in data]}")
                    if rcv_msgs[i].frame.can_id == CAN_ID_AIRBAG_RESPONSE:
                        padl_status = (data[3] & 0b00001000) >> 3
                        pael_status = (data[3] & 0b00000100) >> 2
                        return True, padl_status, pael_status
        
        if ret_can > 0:
            rcv_can_msgs = (ZCAN_Receive_Data * ret_can)()
            num_can = self.canDLL.ZCAN_Receive(self.dev_ch1, byref(rcv_can_msgs), ret_can, 100)
            if num_can > 0:
                for i in range(num_can):
                    data = [rcv_can_msgs[i].frame.data[j] for j in range(rcv_can_msgs[i].frame.can_dlc)]
                    print(f"[Driver][receive_airbag_status] CAN frame ID: {hex(rcv_can_msgs[i].frame.can_id)}, Data: {[hex(x) for x in data]}")
                    if rcv_can_msgs[i].frame.can_id == CAN_ID_AIRBAG_RESPONSE:
                        padl_status = (data[3] & 0b00001000) >> 3
                        pael_status = (data[3] & 0b00000100) >> 2
                        return True, padl_status, pael_status
        
        if ret_fd <= 0 and ret_can <= 0:
            print(f"[Driver][receive_airbag_status] No messages in either buffer")
        return False, None, None
        
    def cleanup(self):
        """Clean up resources"""
        if self.dev_ch1:
            self.canDLL.ZCAN_ResetCAN(self.dev_ch1)
        if self.dev_ch2:
            self.canDLL.ZCAN_ResetCAN(self.dev_ch2)
        if self.m_dev:
            self.canDLL.ZCAN_CloseDevice(self.m_dev) 