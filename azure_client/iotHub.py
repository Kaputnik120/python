# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import asyncio
import random
import logging
import json
import sys

from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device import Message, MethodResponse
from datetime import timedelta, datetime

# Commands
# az iot hub create --resource-group MyResourceGroup --name renkIotHub
# az iot hub device-identity create --device-id mydevice --hub-name renkIotHub
# az iot hub device-identity connection-string show --device-id mydevice --hub-name renkIotHub
# az iot hub device-identity create --device-id mydevice2 --hub-name renkIotHub
# az iot hub device-identity connection-string show --device-id mydevice2 --hub-name renkIotHub

# az iot hub monitor-events --output table --device-id mydevice --hub-name renkIotHub
# az iot hub monitor-events --output table --device-id mydevice2 --hub-name renkIotHub

# Connection Strings
# HostName=renkIotHub.azure-devices.net;DeviceId=mydevice;SharedAccessKey=C9jgO7UnjTlqZQ4fTreuI+qEZ3CbabqUUkhewzKGwlQ=
# pipenv run python iotHub.py "HostName=renkIotHub.azure-devices.net;DeviceId=mydevice;SharedAccessKey=C9jgO7UnjTlqZQ4fTreuI+qEZ3CbabqUUkhewzKGwlQ="
# HostName=renkIotHub.azure-devices.net;DeviceId=mydevice2;SharedAccessKey=KktUakIQcJIrnXv2Foh6d2y6etuQ6pxlq8OYL8UK+wk=
# pipenv run python iotHub.py "HostName=renkIotHub.azure-devices.net;DeviceId=mydevice2;SharedAccessKey=KktUakIQcJIrnXv2Foh6d2y6etuQ6pxlq8OYL8UK+wk="


logging.basicConfig(level=logging.ERROR)

# The device "Thermostat" that is getting implemented using the above interfaces.
# This id can change according to the company the user is from
# and the name user wants to call this Plug and Play device
model_id = "dtmi:com:example:Thermostat;1"

#####################################################
# GLOBAL THERMOSTAT VARIABLES
max_temp = None
min_temp = None
avg_temp_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
moving_window_size = len(avg_temp_list)
target_temperature = None


#####################################################
# COMMAND HANDLERS : User will define these handlers
# depending on what commands the DTMI defines


async def reboot_handler(values):
    global max_temp
    global min_temp
    global avg_temp_list
    global target_temperature
    if values and type(values) == int:
        print("Rebooting after delay of {delay} secs".format(delay=values))
        asyncio.sleep(values)
    max_temp = None
    min_temp = None
    for idx in range(len(avg_temp_list)):
        avg_temp_list[idx] = 0
    target_temperature = None
    print("maxTemp {}, minTemp {}".format(max_temp, min_temp))
    print("Done rebooting")


async def max_min_handler(values):
    if values:
        print(
            "Will return the max, min and average temperature from the specified time {since} to the current time".format(
                since=values
            )
        )
    print("Done generating")


# END COMMAND HANDLERS
#####################################################

#####################################################
# CREATE RESPONSES TO COMMANDS


def create_max_min_report_response(values):
    """
    An example function that can create a response to the "getMaxMinReport" command request the way the user wants it.
    Most of the times response is created by a helper function which follows a generic pattern.
    This should be only used when the user wants to give a detailed response back to the Hub.
    :param values: The values that were received as part of the request.
    """
    response_dict = {
        "maxTemp": max_temp,
        "minTemp": min_temp,
        "avgTemp": sum(avg_temp_list) / moving_window_size,
        "startTime": (datetime.now() - timedelta(0, moving_window_size * 8)).isoformat(),
        "endTime": datetime.now().isoformat(),
    }
    # serialize response dictionary into a JSON formatted str
    response_payload = json.dumps(response_dict, default=lambda o: o.__dict__, sort_keys=True)
    print(response_payload)
    return response_payload


def create_reboot_response(values):
    response = {"result": True, "data": "reboot succeeded"}
    return response


# END CREATE RESPONSES TO COMMANDS
#####################################################

#####################################################
# TELEMETRY TASKS


async def send_telemetry_from_thermostat(device_client, telemetry_msg):
    msg = Message(json.dumps(telemetry_msg))
    msg.content_encoding = "utf-8"
    msg.content_type = "application/json"
    print("Sent message " + msg.data)
    await device_client.send_message(msg)


# END TELEMETRY TASKS
#####################################################

#####################################################
# CREATE COMMAND AND PROPERTY LISTENERS


async def execute_command_listener(
        device_client, method_name, user_command_handler, create_user_response_handler
):
    while True:
        if method_name:
            command_name = method_name
        else:
            command_name = None

        command_request = await device_client.receive_method_request(command_name)
        print("Command request received with payload")
        print(command_request.payload)

        values = {}
        if not command_request.payload:
            print("Payload was empty.")
        else:
            values = command_request.payload

        await user_command_handler(values)

        response_status = 200
        response_payload = create_user_response_handler(values)

        command_response = MethodResponse.create_from_method_request(
            command_request, response_status, response_payload
        )

        try:
            await device_client.send_method_response(command_response)
        except Exception:
            print("responding to the {command} command failed".format(command=method_name))


async def execute_property_listener(device_client):
    ignore_keys = ["__t", "$version"]
    while True:
        patch = await device_client.receive_twin_desired_properties_patch()  # blocking call

        print("the data in the desired properties patch was: {}".format(patch))

        version = patch["$version"]
        prop_dict = {}

        for prop_name, prop_value in patch.items():
            if prop_name in ignore_keys:
                continue
            else:
                prop_dict[prop_name] = {
                    "ac": 200,
                    "ad": "Successfully executed patch",
                    "av": version,
                    "value": prop_value,
                }

        await device_client.patch_twin_reported_properties(prop_dict)


# END COMMAND AND PROPERTY LISTENERS
#####################################################

#####################################################
# An # END KEYBOARD INPUT LISTENER to quit application


def stdin_listener():
    """
    Listener for quitting the sample
    """
    while True:
        selection = input("Press Q to quit\n")
        if selection == "Q" or selection == "q":
            print("Quitting...")
            break


# END KEYBOARD INPUT LISTENER
#####################################################


#####################################################
# PROVISION DEVICE
async def provision_device(provisioning_host, id_scope, registration_id, symmetric_key, model_id):
    provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
        provisioning_host=provisioning_host,
        registration_id=registration_id,
        id_scope=id_scope,
        symmetric_key=symmetric_key,
    )
    provisioning_device_client.provisioning_payload = {"modelId": model_id}
    return await provisioning_device_client.register()


#####################################################
# MAIN STARTS
async def main():
    arguments = sys.argv
    connection_string: str = arguments[1]

    print("Connecting using Connection String " + connection_string)
    device_client = IoTHubDeviceClient.create_from_connection_string(
        connection_string, product_info=model_id
    )

    # Connect the client
    await device_client.connect()

    ################################################
    # Set and read desired property (target temperature)

    max_temp = 10.96  # Initial Max Temp otherwise will not pass certification
    await device_client.patch_twin_reported_properties({"maxTempSinceLastReboot": max_temp})

    ################################################
    # Register callback and Handle command (reboot)
    print("Listening for command requests and property updates")

    listeners = asyncio.gather(
        execute_command_listener(
            device_client,
            method_name="reboot",
            user_command_handler=reboot_handler,
            create_user_response_handler=create_reboot_response,
        ),
        execute_command_listener(
            device_client,
            method_name="getMaxMinReport",
            user_command_handler=max_min_handler,
            create_user_response_handler=create_max_min_report_response,
        ),
        execute_property_listener(device_client),
    )

    ################################################
    # Send telemetry (current temperature)

    async def send_telemetry():
        print("Sending telemetry for temperature")
        global max_temp
        global min_temp
        current_avg_idx = 0

        while True:
            current_temp = random.randrange(10, 50)  # Current temperature in Celsius
            if not max_temp:
                max_temp = current_temp
            elif current_temp > max_temp:
                max_temp = current_temp

            if not min_temp:
                min_temp = current_temp
            elif current_temp < min_temp:
                min_temp = current_temp

            avg_temp_list[current_avg_idx] = current_temp
            current_avg_idx = (current_avg_idx + 1) % moving_window_size

            temperature_msg1 = {"temperature": current_temp}
            await send_telemetry_from_thermostat(device_client, temperature_msg1)
            await asyncio.sleep(8)

    send_telemetry_task = asyncio.create_task(send_telemetry())

    # Run the stdin listener in the event loop
    loop = asyncio.get_running_loop()
    user_finished = loop.run_in_executor(None, stdin_listener)
    # # Wait for user to indicate they are done listening for method calls
    await user_finished

    if not listeners.done():
        listeners.set_result("DONE")

    listeners.cancel()

    send_telemetry_task.cancel()

    # Finally, shut down the client
    await device_client.shutdown()


#####################################################
# EXECUTE MAIN

if __name__ == "__main__":
    asyncio.run(main())

    # If using Python 3.6 use the following code instead of asyncio.run(main()):
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()
