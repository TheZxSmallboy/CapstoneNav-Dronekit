#!/usr/bin/env python3

import asyncio
from mavsdk import System
from mavsdk.offboard import OffboardError, PositionGlobalYaw
import csv




async def main():
    ## Connect to the system
    drone = System()
    await drone.connect()
    await drone.offboard.set_position_global(PositionGlobalYaw(44, 44, 55,0, altitude_type=PositionGlobalYaw.AltitudeType.REL_HOME))
    ## check connection before continuing
    print("Waiting for drone to connect")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("Connected to drone!")
            break

    ## Get the absolute above mean sea level of the current location
    print("Fetching amsl altitude at home location")
    async for terrain_info in drone.telemetry.home():
        absolute_altitude = terrain_info.absolute_altitude_m
        print(absolute_altitude)
        break
    
    asyncio.ensure_future(run(drone, absolute_altitude))
    asyncio.ensure_future(altitudeCorrection(drone))

# Altitude correction code
async def altitudeCorrection(drone):
    print("Start altitude correction code")
    async for position in drone.telemetry.position():
        await drone.telemetry.set_rate_position(0.2) # lower the update rate to 5seconds per update
        # print the values in the current part of the flight
        print("Current Altitude is: "+ str(position.relative_altitude_m))
        print("CUrrent coordinates is: "+ str(position.latitude_deg), str(position.longitude_deg))

        # When 60m is exceeded, start offboard mode and update the values it should be 
        if position.relative_altitude_m >= 60:
            print("-- Setting initial setpoint")
            await drone.offboard.set_position_global(PositionGlobalYaw(position.latitude_deg, position.longitude_deg, 55,0, altitude_type=PositionGlobalYaw.AltitudeType.REL_HOME))
            print("-- Starting offboard")
            try:
                await drone.offboard.start()
            except OffboardError as error:
                print(f"Starting offboard mode failed with error code: {error._result.result}")
                print("-- Disarming")
                await drone.action.disarm()
                return
        



async def run(drone, absolute_altitude):
    print("Run a custom mission based on the CSV file")
    ## Arm drone, then takeoff
    print("Arming")
    await drone.action.arm()

    # flying_alt = absolute_altitude + 40.0
    print("Taking off")
    await drone.action.set_takeoff_altitude(40)
    await drone.action.takeoff()
    await asyncio.sleep(30) # pause for 30s


    # Read from csv file to go to a certain location
    file = open('longer_coordinates.csv')
    csvreader = csv.reader(file)
    header = []
    header = next(csvreader)
    print(header)
    rows = []
    for row in csvreader:
        rows.append(row)
    print(rows)
    await asyncio.sleep(10)
    
    for i in rows:
        print(float(i[0]), float(i[1]), float(i[2]))
        await drone.action.goto_location(float(i[0]), float(i[1]),absolute_altitude + float(i[2]),0) # lat, lon, alt, yaw, yaw degree set to 0 as of now
        await asyncio.sleep(40) # pause to allow current goto location to finish


    ## Continue connection
    while True:
        print("Staying connected, press Ctrl-C to exit")
        await asyncio.sleep(30)


##  Runs code till complete
if __name__ == "__main__":
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    asyncio.ensure_future(main())
    asyncio.get_event_loop().run_forever()