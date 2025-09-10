from grohe import GroheClient, GroheDevice
import asyncio
import json

client = GroheClient("kirstin.weber25@gmail.com", "Uut7fvdG<aKK")

async def main():
    await client.login()
    
    # ------------------------------- Get Devices ------------------------------ #
    devices = await GroheDevice.get_devices(client)

    for device in devices:
        print(f"Device name: {device.name}")
        print(f"Device type: {device.type}")

    device = devices[0]

    # ------------------------------- Get Dashboard ------------------------------ #
    # Get raw data from the Grohe API
    #dashboard = await client.get_dashboard()
    #print(f"Dashboard: {dashboard}")

    # ---------------------------------------------------------------------------- #
    #                                   Appliance                                  #
    # ---------------------------------------------------------------------------- #

    # --------------------------- Get Appliance Details -------------------------- #
    details = await client.get_appliance_details(device.location_id, device.room_id, device.appliance_id)
    #print(f"Appliance details: {details}")
    with open('details.json', 'w') as f:
        json.dump(details, f, indent=4)

    # --------------------------- Get Appliance Command -------------------------- #
    commands = await client.get_appliance_command(device.location_id, device.room_id, device.appliance_id)
    #print(f"Appliance commands: {commands}")
    with open('commands.json', 'w') as f:
        json.dump(commands, f, indent=4)

    # --------------------------- Get Appliance Status --------------------------- #
    status = await client.get_appliance_status(device.location_id, device.room_id, device.appliance_id)
    #print(f"Appliance status: {status}")
    with open('status.json', 'w') as f:
        json.dump(status, f, indent=4)

    # ---------------------------- Get Appliance Info ---------------------------- #
    info = await client.get_appliance_info(device.location_id, device.room_id, device.appliance_id)
    #print(f"Appliance info: {info}")
    with open('info.json', 'w') as f:
        json.dump(info, f, indent=4)

    # ------------------------ Get Appliance Notifications ----------------------- #
    #notifications = await client.get_appliance_notifications(device.location_id, device.room_id, device.appliance_id)
    #print(f"Appliance notifications: {notifications}")

    # ---------------------------------------------------------------------------- #
    #                                 Notifications                                #
    # ---------------------------------------------------------------------------- #

    # ------------------------- Get profile notifications ------------------------ #
    #notifications = await client.get_profile_notifications()
    #print(f"Notifications: {notifications}")

asyncio.run(main())