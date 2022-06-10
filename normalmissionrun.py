#!/usr/bin/env python3

import asyncio
from mavsdk import System
from mavsdk.offboard import PositionNedYaw, OffboardError
import csv
from multiprocessing import Process


async def run():
    ## Connect to the system
    drone = System()
    await drone.connect()

    ## check connection before continuing
    print("-----Waiting for drone to connect-----")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-----Connected to drone!-----")
            break

    ## Get the absolute above mean sea level of the current location
    print("-----Fetching amsl altitude at home location-----")
    async for terrain_info in drone.telemetry.home():
        absolute_altitude = terrain_info.absolute_altitude_m
        print("Location amsl altitude is", absolute_altitude)
        break

    ## Arm drone, then takeoff
    print("-----Arming-----")
    await drone.action.arm()

    # flying_alt = absolute_altitude + 40.0
    
    print("-----Taking off-----")
    await drone.action.set_takeoff_altitude(40)
    await drone.action.takeoff()
    await asyncio.sleep(30) # pause for 30s


    # Read from csv file to go to a certain location
    file = open('longer_coordinates.csv')
    csvreader = csv.reader(file)
    header = []
    header = next(csvreader)
#    print(header)
    rows = []
    for row in csvreader:
        rows.append(row)
 #   print(rows)
    await asyncio.sleep(10)
    
    for i in rows:
        print("Waypoint added from csv, Latitude:", float(i[0]),"Longitude:", float(i[1]), "Altitude:", float(i[2]))
        await drone.action.goto_location(float(i[0]), float(i[1]),absolute_altitude + float(i[2]),0) # lat, lon, alt, yaw, yaw degree set to 0 as of now
        await asyncio.sleep(40) # pause to allow current goto location to finish

 
    ## Continue connection
    while True:
        print("Staying connected, press Ctrl-C to exit")
        await asyncio.sleep(30)





## make sure all the code runs before completion
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(run())
    p1 = Process(target=loop.run_until_complete(run()))
    p1.start()
    # p2 = Process(target=loop.run_until_complete(altitudeCorrection()))
    # p2.start()