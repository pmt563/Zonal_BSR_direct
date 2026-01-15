from ctypes import *
from kuksa_client.grpc import VSSClient, Datapoint
import threading
import time
import argparse

# Add argument parser
parser = argparse.ArgumentParser(description='CAN communication application with loopback option')
parser.add_argument('-loopback', type=int, choices=[0, 1], default=0,
                    help='Set loopback mode: 0 for disabled, 1 for enabled')
parser.add_argument('databroker', nargs='?', default='192.168.1.1:55555',
                    help='Databroker in format IP:PORT (e.g., 192.168.1.1:55555)')
args = parser.parse_args()

# Parse databroker positional argument
if ':' in args.databroker:
    databroker_ip, port = args.databroker.split(':', 1)
    try:
        databroker_port = int(port)
    except ValueError:
        print("Invalid port in databroker argument. Use IP:PORT (e.g., 192.168.1.1:55555)")
        exit(1)
else:
    print("Invalid databroker format. Use IP:PORT (e.g., 192.168.1.1:55555)")
    exit(1)

VCI_USBCAN2 = 41
STATUS_OK = 1
INVALID_DEVICE_HANDLE  = 0
INVALID_CHANNEL_HANDLE = 0
TYPE_CAN = 0
TYPE_CANFD = 1

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
 
### structure
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

	
CanDLLName = './libcontrolcanfd.so' 
# canDLL = cdll.LoadLibrary('./libcontrolcanfd.so')
canDLL = cdll.LoadLibrary('/app/demo/libcontrolcanfd.so')
print('########################################################')
print('## Chuang Xin USBCANFD python(x64) test program V2.0 ###')
print('########################################################')
print(CanDLLName)


canDLL.ZCAN_OpenDevice.restype = c_void_p
canDLL.ZCAN_SetAbitBaud.argtypes = (c_void_p, c_ulong, c_ulong)
canDLL.ZCAN_SetDbitBaud.argtypes = (c_void_p, c_ulong, c_ulong)
canDLL.ZCAN_SetCANFDStandard.argtypes = (c_void_p, c_ulong, c_ulong)
canDLL.ZCAN_InitCAN.argtypes = (c_void_p, c_ulong, c_void_p)
canDLL.ZCAN_InitCAN.restype = c_void_p
canDLL.ZCAN_StartCAN.argtypes = (c_void_p,)
canDLL.ZCAN_Transmit.argtypes = (c_void_p, c_void_p, c_ulong)
canDLL.ZCAN_TransmitFD.argtypes = (c_void_p, c_void_p, c_ulong)
canDLL.ZCAN_GetReceiveNum.argtypes = (c_void_p, c_ulong)
canDLL.ZCAN_Receive.argtypes = (c_void_p, c_void_p, c_ulong, c_long)
canDLL.ZCAN_ReceiveFD.argtypes = (c_void_p, c_void_p, c_ulong, c_long)
canDLL.ZCAN_ResetCAN.argtypes = (c_void_p,)
canDLL.ZCAN_CloseDevice.argtypes = (c_void_p,)

canDLL.ZCAN_ClearFilter.argtypes=(c_void_p,)
canDLL.ZCAN_AckFilter.argtypes=(c_void_p,)
canDLL.ZCAN_SetFilterMode.argtypes=(c_void_p,c_ulong)
canDLL.ZCAN_SetFilterStartID.argtypes=(c_void_p,c_ulong)
canDLL.ZCAN_SetFilterEndID.argtypes=(c_void_p,c_ulong)

m_dev = canDLL.ZCAN_OpenDevice(VCI_USBCAN2, 0, 0)
if m_dev == INVALID_DEVICE_HANDLE:
    print("Open Device failed!")
    exit(0)
print("Open Device OK, device handle:0x%x." %(m_dev))
 
ret = canDLL.ZCAN_SetAbitBaud(m_dev,0,500000)
if ret != STATUS_OK:
	print("Set CAN0 abit:1M failed!")
	exit(0)
print("Set CAN0 abit:1M OK!")
ret = canDLL.ZCAN_SetDbitBaud(m_dev,0,2000000)
if ret != STATUS_OK:
	print("Set CAN0 dbit:5M failed!")
	exit(0)
print("Set CAN0 dbit:5M OK!")


ret = canDLL.ZCAN_SetAbitBaud(m_dev,1,500000)
if ret != STATUS_OK:
	print("Set CAN1 abit:1M failed!")
	exit(0)
print("Set CAN1 abit:1M OK!")
ret = canDLL.ZCAN_SetDbitBaud(m_dev,1,2000000)
if ret != STATUS_OK:
	print("Set CAN1 dbit:5M failed!")
	exit(0)
print("Set CAN1 dbit:5M OK!")

ret = canDLL.ZCAN_SetCANFDStandard(m_dev,0,0)
if ret != STATUS_OK:
	print("Set CAN0 ISO mode failed!")
	exit(0)
print("Set CAN0 ISO mode OK!")
ret = canDLL.ZCAN_SetCANFDStandard(m_dev,1,0)
if ret != STATUS_OK:
	print("Set CAN1 ISO mode failed!")
	exit(0)
print("Set CAN1 ISO mode OK!")

init_config = ZCAN_CHANNEL_INIT_CONFIG()
init_config.can_type = TYPE_CANFD
init_config.config.canfd.mode = 0

dev_ch1 = canDLL.ZCAN_InitCAN(m_dev, 0, byref(init_config))
if dev_ch1 == INVALID_CHANNEL_HANDLE:
    print("Init CAN0 failed!")
    exit(0)
print("Init CAN0 OK!")

ret = canDLL.ZCAN_StartCAN(dev_ch1)
if ret != STATUS_OK:
    print("Start CAN0 failed!")
    exit(0)
print("Start CAN0 OK!")	

dev_ch2 = canDLL.ZCAN_InitCAN(m_dev, 1, byref(init_config))
if dev_ch2 == INVALID_CHANNEL_HANDLE:
    print("Init CAN1 failed!")
    exit(0)
print("Init CAN1 OK!")


###################################################################
#    在 ZCAN_InitCAN 之后， ZCAN_StartCAN之前配置
#	设置通道1  滤波:只接收 扩展帧,ID范围 5~6
###################################################################
# canDLL.ZCAN_ClearFilter(dev_ch1)
# canDLL.ZCAN_SetFilterMode(dev_ch2,1)
# canDLL.ZCAN_SetFilterStartID(dev_ch1,0x150)
# canDLL.ZCAN_SetFilterEndID(dev_ch1,0x150)
# canDLL.ZCAN_AckFilter(dev_ch2)

ret = canDLL.ZCAN_StartCAN(dev_ch2)
if ret != STATUS_OK:
    print("Start CAN1 failed!")
    exit(0)
print("Start CAN1 OK!")	


#################################
### CANFD frame send&&recv 
#################################
aliveCounter = 0
Checksum = 0

frame = ZCAN_TransmitFD_Data()
frame.transmit_type = 0  # 2 = self-send-and-receive
frame.frame.eff = 0      # extended frame
frame.frame.rtr = 0      # data frame
frame.frame.brs = 1      # bit rate switching
frame.frame.can_id = 0x150
frame.frame.len = 3     # max data length for CAN FD

# Fill data payload
frame.frame.data[0] = 128
frame.frame.data[1] = 0
frame.frame.data[2] = 0

def Crc_CalculateCRC_Profile1(data, length, init_value):
    i = 0
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
    PID = 0x611D
    protectedDataOffset_byte = 0
    protectedDataSize_byte = 2
    crcStartValue = 0x00
    calculatedCrcValue = 0x00
    localBuffer = bytearray(3)

    global buffer
    global alive_counter
    global checksum

    # Cal Alive counter
    alive_counter = msgByteArray[1]

    # Assuming Msg.AliveCounter and Msg.byte() are defined somewhere
    if alive_counter % 2 == 0:
        localBuffer[0] = PID & 0xFF
    else:
        localBuffer[0] = (PID >> 8) & 0xFF

    localBuffer[1] = msgByteArray[0]
    localBuffer[2] = msgByteArray[1]

    calculatedCrcValue = Crc_CalculateCRC_Profile1(localBuffer, 1 + protectedDataSize_byte, crcStartValue)

    return calculatedCrcValue

'''
main operation
'''

PADS_vss_signal      = 'Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn'
PADL_vss_signal      = 'Vehicle.Cabin.Seat.Row1.PassengerSide.Airbag.IsDeployed'
# PAEL_vss_signal      = 'Vehicle.Cabin.Seat.Row1.PassengerSide.AirbagIndicator.AirbagIsEnable.IsSignaling'

PADL_data = 0x00
PAEL_data = 0x01
PADS_data = 0x00

try:
    with VSSClient(databroker_ip, databroker_port) as client:
        print("Connected to databroker")
        while True:
            IsDisabled = client.get_current_values([PADS_vss_signal])

            if IsDisabled[PADS_vss_signal] is not None:
                if bool(IsDisabled[PADS_vss_signal].value):
                    frame.frame.data[0] = 128 # 1 passenger airbag deactivate
                    
                else:
                    frame.frame.data[0] = 129 # 0 passenger airbag activate
            else:
                print(f"Error: IsDisabled[PADS_vss_signal] is None")

            
            if PADS_data != frame.frame.data[0] : # 1 passenger airbag activate
                if frame.frame.data[0] == 129:
                    print(f"Zonal forwards to Airbag ECU: ENABLE Passenger Airbag")
                elif frame.frame.data[0] == 128:
                    print(f"Zonal forwards to Airbag ECU: DISABLE Passenger Airbag")
            else:
                pass
            
            aliveCounter = frame.frame.data[1]

            if aliveCounter < 14:
                aliveCounter += 1
            else:
                aliveCounter = 0
            
            frame.frame.data[1] = aliveCounter
            Checksum = cal_check_sum(frame.frame.data)
            frame.frame.data[2] = Checksum

            canDLL.ZCAN_TransmitFD(dev_ch1, byref(frame), 1)
            data_sent = [hex(frame.frame.data[i]) for i in range(frame.frame.len)]
            # print(f"CH1 Sent Frame ID: {hex(frame.frame.can_id)}, Data: {data_sent}")

            if args.loopback == 1:
                # Receive on dev_ch2
                while True:
                    ret = canDLL.ZCAN_GetReceiveNum(dev_ch2, TYPE_CANFD)
                    if ret > 0:
                        rcv_msgs = (ZCAN_ReceiveFD_Data * ret)()
                        num = canDLL.ZCAN_ReceiveFD(dev_ch2, byref(rcv_msgs), ret, 100)
                        
                        for i in range(num):
                            data = [rcv_msgs[i].frame.data[j] for j in range(rcv_msgs[i].frame.len)]
                            print(f"CH2 Received Frame ID: {hex(rcv_msgs[i].frame.can_id)}, Data: [" + 
                                    ", ".join([hex(x) for x in data]) + "]")
                            
                            #Simulate PADS behavior
                            if data[0] == 128:
                                print("[Airbag ECU] Deactivate Passenger Airbag")
                                PADL_data_temp = 0x01
                                PAEL_data_temp = 0x00
                            elif data[0] == 129:
                                print("[Airbag ECU] Activate Passenger Airbag")
                                PADL_data_temp = 0x00
                                PAEL_data_temp = 0x01
                            ###

                            # Prepare response from CH2 back to CH1
                            response = ZCAN_TransmitFD_Data()
                            response.transmit_type = 0
                            response.frame.eff = 0
                            response.frame.rtr = 0
                            response.frame.brs = 1
                            response.frame.can_id = 0x08C
                            response.frame.len = 8  # Standard length for response
                            response.frame.data[3] = (PADL_data_temp << 3) | (PAEL_data_temp << 2)  # Set response bits
                            
                            # Send response from CH2 to CH1
                            canDLL.ZCAN_TransmitFD(dev_ch2, byref(response), 1)
                            # print(f"CH2 Responded Frame ID: {hex(response.frame.can_id)}, Data[3]: {hex(response.frame.data[3])}")
                        break
                    time.sleep(0.1)
            # '''Receive'''
            while True:
                ret = canDLL.ZCAN_GetReceiveNum(dev_ch1, TYPE_CANFD)
                if ret > 0:
                    rcv_msgs = (ZCAN_ReceiveFD_Data * ret)()
                    num = canDLL.ZCAN_ReceiveFD(dev_ch1, byref(rcv_msgs), ret, 100)
                    
                    for i in range(num):
                        data = [rcv_msgs[i].frame.data[j] for j in range(rcv_msgs[i].frame.len)]
                        if rcv_msgs[i].frame.can_id == 0x08C:
                            if (data[3] & 0b00001000) >> 3 != PADL_data:
                                PADL_data = (data[3] & 0b00001000) >> 3
                                client.set_current_values({PADL_vss_signal: Datapoint(bool(PADL_data))})
                                if PADL_data == 1:
                                    print(f"Passenger Airbag Disable Lamp from Airbag is ON")
                                else:
                                    print(f"Passenger Airbag Disable Lamp from Airbag is OFF")

                            # if (data[3] & 0b00000100) >> 2 != PAEL_data:
                            #     PAEL_data = (data[3] & 0b00000100) >> 2
                            #     client.set_current_values({PAEL_vss_signal: Datapoint(bool(PAEL_data))})
                            #     if PAEL_data == 1:
                            #         print(f"Passenger Airbag Enable Lamp from Airbag is ON")
                            #     else:
                            #         print(f"Passenger Airbag Enable Lamp from Airbag is OFF")

                    break  # exit wait loop after receiving
                time.sleep(0.1)  # short delay before retry

            PADS_data = frame.frame.data[0]
            time.sleep(0.02)

except Exception as e:
    print(f"Error: {e}")



