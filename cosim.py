import numpy as np
import matplotlib.pyplot as plt
from fmpy import simulate_fmu, read_model_description, extract
from fmpy.fmi2 import FMU2Slave
import time
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FMUS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "fmus")

VECU_AIRBAG_FMU_PATH    = os.path.join(FMUS_DIR, "vECU_Airbag.fmu")
VECU_ZONAL_FMU_PATH     = os.path.join(FMUS_DIR, "vecu_zonal.fmu")
VECU_COCKPIT_FMU_PATH   = os.path.join(FMUS_DIR, "cockpit_test.fmu")

# init value of kuksha buffers
from_kuksha_PassengerAirbagIsDisabled_bo = False
from_kuksha_PassengerAirbagWarningState_se = 0
to_kuksha_UserConfirmAirbagState_se = 0

from_kuksha_UserConfirmAirbagState_se = 0
to_kuksha_PassengerAirbagDisableLamp_bo = 1
to_kuksha_PassengerAirbagWarningState_se = 0

from_kuksha = {
    'Vehicle.Cabin.Light.Spotlight.Row1.PassengerSide.IsLightOn': from_kuksha_PassengerAirbagIsDisabled_bo,
    'Vehicle.Cabin.Seat.Row1.PassengerSide.Position': from_kuksha_PassengerAirbagWarningState_se,
    'Vehicle.Cabin.Seat.Row1.PassengerSide.Seating.Length': from_kuksha_UserConfirmAirbagState_se
}

to_kuksha = {
    'Vehicle.Cabin.Seat.Row1.PassengerSide.Height': to_kuksha_UserConfirmAirbagState_se,
    'Vehicle.Cabin.Seat.Row1.PassengerSide.Airbag.IsDeployed': to_kuksha_PassengerAirbagDisableLamp_bo
}

def cosim_fmus(zonal_vecu_path=VECU_ZONAL_FMU_PATH, 
                airbag_vecu_path=VECU_AIRBAG_FMU_PATH,
                cockpit_vecu_path=VECU_COCKPIT_FMU_PATH,
                start_time=0.0,
                stop_time=None,
                step_size=0.01
                ):
    """
    Connect two FMUs where outputs from zonal_vecu are used as inputs to airbag_vecu
    
    Parameters:
        zonal_vecu_path (str): Path to the first FMU
        airbag_vecu_path (str): Path to the second FMU
        inout_mapping (dict): Dictionary mapping output variable names from zonal_vecu to 
                                     input variable names in airbag_vecu
        start_time (float): Simulation start time
        stop_time (float): Simulation end time
        step_size (float): Simulation step size
        
    Returns:
        tuple: (time, zonal_vecu_result, airbag_vecu_result) where results are dictionaries of output variables
    """
    # Read model descriptions
    zonal_vecu_description = read_model_description(zonal_vecu_path)
    airbag_vecu_description = read_model_description(airbag_vecu_path)
    cockpit_vecu_description = read_model_description(cockpit_vecu_path)

    # Unzip fmu
    unzip_zonal_vecu    = extract(zonal_vecu_path)
    unzip_airbag_vecu   = extract(airbag_vecu_path)
    unzip_cockpit_vecu  = extract(cockpit_vecu_path)

    # Get guid
    zonal_vecu_guid   = zonal_vecu_description.guid
    airbag_vecu_guid  = airbag_vecu_description.guid
    cockpit_vecu_guid = cockpit_vecu_description.guid

    # Get model's identifier
    zonal_vecu_iden = zonal_vecu_description.coSimulation.modelIdentifier
    airbag_vecu_iden = airbag_vecu_description.coSimulation.modelIdentifier
    cockpit_vecu_iden = cockpit_vecu_description.coSimulation.modelIdentifier
    
    # Instantiate both FMUs as slaves
    zonal_vecu   = FMU2Slave(guid=zonal_vecu_guid, modelIdentifier=zonal_vecu_iden, unzipDirectory=unzip_zonal_vecu)
    airbag_vecu  = FMU2Slave(guid=airbag_vecu_guid, modelIdentifier=airbag_vecu_iden, unzipDirectory=unzip_airbag_vecu)
    cockpit_vecu = FMU2Slave(guid=cockpit_vecu_guid, modelIdentifier=cockpit_vecu_iden, unzipDirectory=unzip_cockpit_vecu)
    
    # Initialize both FMUs
    zonal_vecu.instantiate()
    airbag_vecu.instantiate()
    cockpit_vecu.instantiate()
    
    # Set up simulation
    zonal_vecu.setupExperiment(startTime=start_time, stopTime=stop_time)
    airbag_vecu.setupExperiment(startTime=start_time, stopTime=stop_time)
    cockpit_vecu.setupExperiment(startTime=start_time, stopTime=stop_time)

    # Enter initialization mode
    zonal_vecu.enterInitializationMode()
    airbag_vecu.enterInitializationMode()
    cockpit_vecu.enterInitializationMode()
    
    # Exit initialization mode
    zonal_vecu.exitInitializationMode()
    airbag_vecu.exitInitializationMode()
    cockpit_vecu.exitInitializationMode()

    zonal_vecu_ref_ports   = {}
    airbag_vecu_ref_ports  = {}
    cockpit_vecu_ref_ports = {}

    '''
    buffer variables to communicate with kuksha
    '''
    # Zonal vecu
    global from_kuksha_PassengerAirbagIsDisabled_bo
    global from_kuksha_PassengerAirbagWarningState_se
    global to_kuksha_UserConfirmAirbagState_se
    # Cockpit ecu
    global from_kuksha_UserConfirmAirbagState_se
    global to_kuksha_PassengerAirbagDisableLamp_bo
    global to_kuksha_PassengerAirbagWarningState_se
    # from_kuksha_PassengerAirbagIsDisabled_bo      = input("[ZONAL]In_PassengerAirbagIsDisabled_bo: ")
    # from_kuksha_PassengerAirbagWarningState_se = int(input("[ZONAL]In_PassengerAirbagWarningState_se: "))

    # # Input to cockpit vecu
    # from_kuksha_UserConfirmAirbagState_se = int(input("[COCKPIT]In_UserConfirmAirbagState: "))


    '''
    Get inputs and outputs
    '''
    '''
    Zonal vECU
    '''
    for var in zonal_vecu_description.modelVariables:
        zonal_vecu_ref_ports[var.name] = var.valueReference

    '''
    Airbag vECU
    '''
    for var in airbag_vecu_description.modelVariables:
        airbag_vecu_ref_ports[var.name] = var.valueReference

    '''
    Cockpit vECU
    '''
    for var in cockpit_vecu_description.modelVariables:
        cockpit_vecu_ref_ports[var.name] = var.valueReference

    while True:
        # Set inputs zonal vecu
        zonal_vecu.setBoolean([zonal_vecu_ref_ports['In_PassengerAirbagIsDisabled_bo']], [from_kuksha_PassengerAirbagIsDisabled_bo])
        zonal_vecu.setInteger([zonal_vecu_ref_ports['In_PassengerAirbagWarningState_se']], [from_kuksha_PassengerAirbagWarningState_se])

        # Zonal DoStep
        zonal_vecu.doStep(currentCommunicationPoint=start_time, communicationStepSize=step_size)

        # Get output value of zonal vecu
        out_PADS_value = zonal_vecu.getBoolean([zonal_vecu_ref_ports['Out_PassengerAirbagDeactivationSwitch_bo']])[0]
        out_waningState_value = zonal_vecu.getInteger([zonal_vecu_ref_ports['Out_PassengerAirbagWarningState_se']])[0]

        # Set input of airbag vecu
        airbag_vecu.setInteger([airbag_vecu_ref_ports['PADS']], [int(out_PADS_value)])

        # Airbag DoStep
        airbag_vecu.doStep(currentCommunicationPoint=start_time, communicationStepSize=step_size)

        # Get output of airbag vecu
        output_PADL_value = airbag_vecu.getInteger([airbag_vecu_ref_ports['PADL']])[0]
        output_PAEL_value = airbag_vecu.getInteger([airbag_vecu_ref_ports['PAEL']])[0]

        # Set inputs cockpit vecu
        cockpit_vecu.setBoolean([cockpit_vecu_ref_ports['In_PassengerAirbagDisableLamp_bo']], [bool(output_PADL_value)])
        cockpit_vecu.setBoolean([cockpit_vecu_ref_ports['In_PassengerAirbagEnableLamp_bo']], [bool(output_PAEL_value)])
        cockpit_vecu.setInteger([cockpit_vecu_ref_ports['In_PassengerAirbagWarningState_se']], [out_waningState_value])
        cockpit_vecu.setInteger([cockpit_vecu_ref_ports['In_UserConfirmAirbagState']], [from_kuksha_UserConfirmAirbagState_se])

        # Cockpit DoStep
        cockpit_vecu.doStep(currentCommunicationPoint=start_time, communicationStepSize=step_size)

        # Get output of cockpit vecu
        to_kuksha_PassengerAirbagDisableLamp_bo    = cockpit_vecu.getBoolean([cockpit_vecu_ref_ports['Out_PassengerAirbagDisableLamp_bo']])[0]
        to_kuksha_PassengerAirbagWarningState_se   = cockpit_vecu.getInteger([cockpit_vecu_ref_ports['Out_PassengerAirbagWarningState_se']])[0]
        out_cp_userConfirm_value    = cockpit_vecu.getInteger([cockpit_vecu_ref_ports['Out_UserConfirmAirbagState_se']])[0]

        zonal_vecu.setInteger([zonal_vecu_ref_ports['In_UserConfirmAirbagState_se']], [out_cp_userConfirm_value])
        to_kuksha_UserConfirmAirbagState_se = zonal_vecu.getInteger([zonal_vecu_ref_ports['Out_UserConfirmAirbagState_se']])[0]

        start_time += step_size

        time.sleep(step_size)


if __name__ == '__main__':
    cosim_fmus()
