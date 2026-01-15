import argparse
import time
from kuksa_client.grpc import VSSClient, Datapoint
from can_driver import CANDriver

class ZonalApp:
    # VSS signal paths
    PADS_VSS_SIGNAL = 'Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn'
    PADL_VSS_SIGNAL = 'Vehicle.Cabin.Seat.Row1.PassengerSide.Airbag.IsDeployed'
    PAEL_VSS_SIGNAL = 'Vehicle.Cabin.Seat.Row1.PassengerSide.AirbagIndicator.AirbagIsEnable.IsSignaling'

    def __init__(self, broker_ip='192.168.1.1', broker_port=55555, loopback_mode=0):
        """Initialize ZonalApp with configuration"""
        self.loopback_mode  = loopback_mode
        self.PADL_data      = 0x00  # Passenger Airbag Disable Lamp status
        self.PAEL_data      = 0x01  # Passenger Airbag Enable Lamp status
        self.PADS_data      = 0x00  # Passenger Airbag Deactivated Status
        self.can_driver     = None
        self.client         = None
        self.broker_ip      = broker_ip
        self.broker_port    = broker_port

    def initialize(self):
        """Initialize CAN driver and connect to databroker"""
        self.can_driver = CANDriver('/app/src/libcontrolcanfd.so')
        self.can_driver.initialize()
        RETRY_DELAY = 1
        self.client = VSSClient(self.broker_ip, self.broker_port)
        while True:
            print("Attemp to connect...")
            try:
                self.client.connect()
                if self.client.connected:
                    print("Succesfully connected to databroker")
                    break
            except Exception as e:
                print(f"Exception: {e}")
                print(f"Retry to connect in {RETRY_DELAY}")
                time.sleep(RETRY_DELAY)
                

    def cleanup(self):
        """Clean up resources"""
        if self.can_driver:
            self.can_driver.cleanup()

    def process_airbag_status(self):
        """Process airbag status updates from CAN bus"""
        wait_count = 0
        status_received = False
        
        while not status_received and wait_count < 10:
            status_received, padl_status, pael_status = self.can_driver.receive_airbag_status()
            
            if status_received:
                self._update_padl_status(padl_status)
                # self._update_pael_status(pael_status)
            else:
                time.sleep(0.1)
                wait_count += 1

    def _update_padl_status(self, padl_status):
        """Update PADL status in VSS"""
        if padl_status != self.PADL_data:
            self.PADL_data = padl_status
            self.client.set_current_values({self.PADL_VSS_SIGNAL: Datapoint(bool(self.PADL_data))})
            if self.PADL_data == 1:
                print(f"Passenger Airbag Disable Lamp from Airbag is ON")
            else:
                print(f"Passenger Airbag Disable Lamp from Airbag is OFF")

    def _update_pael_status(self, pael_status):
        """Update PAEL status in VSS"""
        if pael_status != self.PAEL_data:
            self.PAEL_data = pael_status
            self.client.set_current_values({self.PAEL_VSS_SIGNAL: Datapoint(bool(self.PAEL_data))})
            if self.PAEL_data == 1:
                print(f"Passenger Airbag Enable Lamp from Airbag is ON")
            else:
                print(f"Passenger Airbag Enable Lamp from Airbag is OFF")

    def process_loopback(self):
        """Process loopback mode if enabled"""
        if self.loopback_mode == 1:
            wait_count = 0
            success, padl_data_temp, pael_data_temp = False, None, None
            
            while not success and wait_count < 10:
                success, padl_data_temp, pael_data_temp = self.can_driver.process_loopback()
                if not success:
                    time.sleep(0.1)
                    wait_count += 1

    def run(self):
        """Main application loop"""
        try:
            self.initialize()
            
            while True:
                # Get current airbag disabled status from VSS
                is_disabled = self.client.get_current_values([self.PADS_VSS_SIGNAL])
                
                # Determine airbag command based on VSS data
                enable_airbag = False
                if is_disabled[self.PADS_VSS_SIGNAL] is not None:
                    enable_airbag = not bool(is_disabled[self.PADS_VSS_SIGNAL].value)
                else:
                    print(f"Error: is_disabled[PADS_VSS_SIGNAL] is None")
                
                # Send command to CAN bus
                success, data_sent = self.can_driver.send_airbag_command(enable_airbag)
                
                # Log status changes if any 
                current_status_code = 129 if enable_airbag else 128
                if self.PADS_data != current_status_code:
                    if enable_airbag:
                        print(f"Zonal forwards to Airbag ECU: ENABLE Passenger Airbag")
                    else:
                        print(f"Zonal forwards to Airbag ECU: DISABLE Passenger Airbag")
                
                # Process loopback if enabled
                self.process_loopback()
                
                # Process airbag status
                self.process_airbag_status()
                
                # Update previous state
                self.PADS_data = current_status_code
                
                # Delay before next cycle
                time.sleep(0.02)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.cleanup()

def main():
    """Main entry point"""
    databroker_ip   = '192.168.1.1'
    databroker_port = '55555'

    parser = argparse.ArgumentParser(description='CAN communication application with loopback option')
    parser.add_argument('-loopback', type=int, choices=[0, 1], default=0,
                        help='Set loopback mode: 0 for disabled, 1 for enabled')
    # parser.add_argument('-broker-ip', type=str, default='10.89.0.4',
    #                     help='IP address of the databroker (default: 10.89.0.4)')
    # parser.add_argument('-broker-port', type=int, default=55555,
    #                     help='Port of the databroker (default: 55555)')
    parser.add_argument('databroker', nargs='?', default=databroker_ip+':'+databroker_port,
                    help='Databroker in format IP:PORT (e.g., 192.168.1.1:55555)')
    args = parser.parse_args()

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

    app = ZonalApp(broker_ip=databroker_ip, broker_port=databroker_port, loopback_mode=args.loopback)
    app.run()

if __name__ == "__main__":
    main()




