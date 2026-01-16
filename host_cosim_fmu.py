import numpy as np
import matplotlib.pyplot as plt
from fmpy import simulate_fmu, read_model_description, extract
from enum import IntEnum
from fmpy.fmi2 import FMU2Slave
import threading
import time
import cosim_environment
import argparse

from kuksa_client.grpc import VSSClient
from kuksa_client.grpc import Datapoint

class code_stage_en(IntEnum):
    development = 0
    testing = 1
    release = 2

CODE_STAGE = code_stage_en.testing

def print_terminal(arg, code_stage: list[code_stage_en] = [code_stage_en.development,code_stage_en.testing]) -> None: 
    if CODE_STAGE in code_stage or code_stage:
        print(arg)
class CoSim_Host:
    def __init__(self, kuksa_host='localhost', kuksa_port=55555):
        self.step_size = 0.01
        self.time = time.time()
        self.kuksa_host = kuksa_host
        self.kuksa_port = kuksa_port

    def connect_to_broker_thread(self):
        while True:
            try:
                with VSSClient(self.kuksa_host, self.kuksa_port) as client:           
                    signals_from_kuksha = client.get_current_values([
                        'Vehicle.Cabin.Seat.Row1.PassengerSide.Seating.Length',
                        'Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn',
                        'Vehicle.Cabin.Seat.Row1.PassengerSide.Position',
                        'Vehicle.Cabin.Seat.Row1.PassengerSide.Height',
                        'Vehicle.Cabin.Seat.Row1.PassengerSide.Airbag.IsDeployed',
                        'Vehicle.Cabin.Seat.Row1.PassengerSide.Massage',
                    ])

                    if(cosim_environment.from_kuksha_UserConfirmAirbagState_se != signals_from_kuksha['Vehicle.Cabin.Seat.Row1.PassengerSide.Seating.Length'].value):
                        print_terminal("from_kuksha_UserConfirmAirbagState_se: {}->{}".format(cosim_environment.from_kuksha_UserConfirmAirbagState_se,signals_from_kuksha['Vehicle.Cabin.Seat.Row1.PassengerSide.Seating.Length'].value))
                        cosim_environment.from_kuksha_UserConfirmAirbagState_se = signals_from_kuksha['Vehicle.Cabin.Seat.Row1.PassengerSide.Seating.Length'].value
                                    
                    if(cosim_environment.from_kuksha_PassengerAirbagIsDisabled_bo != signals_from_kuksha['Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn'].value):
                        print_terminal("from_kuksha_PassengerAirbagIsDisabled_bo: {}->{}".format(cosim_environment.from_kuksha_PassengerAirbagIsDisabled_bo,signals_from_kuksha['Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn'].value))
                        cosim_environment.from_kuksha_PassengerAirbagIsDisabled_bo = signals_from_kuksha['Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn'].value
                    
                    if(cosim_environment.from_kuksha_PassengerAirbagWarningState_se != signals_from_kuksha['Vehicle.Cabin.Seat.Row1.PassengerSide.Position'].value):
                        print_terminal("from_kuksha_PassengerAirbagWarningState_se: {}->{}".format(cosim_environment.from_kuksha_PassengerAirbagWarningState_se,signals_from_kuksha['Vehicle.Cabin.Seat.Row1.PassengerSide.Position'].value))
                        cosim_environment.from_kuksha_PassengerAirbagWarningState_se = signals_from_kuksha['Vehicle.Cabin.Seat.Row1.PassengerSide.Position'].value

                    if(cosim_environment.to_kuksha_UserConfirmAirbagState_se != signals_from_kuksha['Vehicle.Cabin.Seat.Row1.PassengerSide.Height'].value):
                        print_terminal("to_kuksha_UserConfirmAirbagState_se: {}->{}".format(signals_from_kuksha['Vehicle.Cabin.Seat.Row1.PassengerSide.Height'].value, cosim_environment.to_kuksha_UserConfirmAirbagState_se))
                        client.set_current_values({'Vehicle.Cabin.Seat.Row1.PassengerSide.Height': Datapoint(cosim_environment.to_kuksha_UserConfirmAirbagState_se)})

                    if(cosim_environment.to_kuksha_PassengerAirbagDisableLamp_bo != signals_from_kuksha['Vehicle.Cabin.Seat.Row1.PassengerSide.Airbag.IsDeployed'].value):
                        print_terminal("to_kuksha_PassengerAirbagDisableLamp_bo: {}->{}".format(signals_from_kuksha['Vehicle.Cabin.Seat.Row1.PassengerSide.Airbag.IsDeployed'].value, cosim_environment.to_kuksha_PassengerAirbagDisableLamp_bo))
                        client.set_current_values({'Vehicle.Cabin.Seat.Row1.PassengerSide.Airbag.IsDeployed': Datapoint(cosim_environment.to_kuksha_PassengerAirbagDisableLamp_bo)})

                    if(cosim_environment.to_kuksha_PassengerAirbagWarningState_se != signals_from_kuksha['Vehicle.Cabin.Seat.Row1.PassengerSide.Massage'].value):
                        print_terminal("to_kuksha_PassengerAirbagWarningState_se: {}->{}".format(signals_from_kuksha['Vehicle.Cabin.Seat.Row1.PassengerSide.Massage'].value, cosim_environment.to_kuksha_PassengerAirbagWarningState_se))
                        client.set_current_values({'Vehicle.Cabin.Seat.Row1.PassengerSide.Massage': Datapoint(cosim_environment.to_kuksha_PassengerAirbagWarningState_se)})

            except Exception as e:
                if(time.time() - self.time) > 1:
                    self.time = time.time()
                    print_terminal("Waiting for Kuksa Databroker online...",list(code_stage_en))
            time.sleep(self.step_size)

    def run_cosim_thread(self):
        cosim_environment.cosim_fmus()

    def start_cosim_host(self):
        try:
            # Declare threads
            cosim_thread = threading.Thread(target=self.run_cosim_thread, args=())
            kuksa_connection_thread = threading.Thread(target=self.connect_to_broker_thread, args=())

            # Start threads
            cosim_thread.start()
            kuksa_connection_thread.start()

            # Wait threads to finish
            cosim_thread.join()
            kuksa_connection_thread.join()

        except Exception as e:
            print_terminal("[ERROR] {}".format(e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Host CoSim and connect to KUKSA VAL')
    parser.add_argument('kuksa_address', nargs='?', default='localhost:55555',
                        help='KUKSA VAL address in format <host>:<port> (default: localhost:55555)')
    
    args = parser.parse_args()
    
    try:
        if ':' in args.kuksa_address:
            kuksa_host, kuksa_port_str = args.kuksa_address.rsplit(':', 1)
            kuksa_port = int(kuksa_port_str)
        else:
            print_terminal(f"[ERROR] Invalid address format. Expected <host>:<port>, got: {args.kuksa_address}", list(code_stage_en))
            print_terminal("Using default: localhost:55555", list(code_stage_en))
            kuksa_host = 'localhost'
            kuksa_port = 55555
    except ValueError as e:
        print_terminal(f"[ERROR] Invalid port number: {e}", list(code_stage_en))
        print_terminal("Using default: localhost:55555", list(code_stage_en))
        kuksa_host = 'localhost'
        kuksa_port = 55555
    
    print_terminal(f"Connecting to KUKSA VAL at {kuksa_host}:{kuksa_port}", list(code_stage_en))
    
    cosim_host = CoSim_Host(kuksa_host=kuksa_host, kuksa_port=kuksa_port)
    cosim_host.start_cosim_host()
        

