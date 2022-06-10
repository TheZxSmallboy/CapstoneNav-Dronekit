import asyncio

from mavsdk import System
from mavsdk.offboard import (OffboardError, PositionNedYaw)


async def run():
    """ Does Offboard control using position NED coordinates. """

    drone = System()
    await drone.connect()

    print("Waiting for drone to connect...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print(f"-- Connected to drone!")
            break

    print("Waiting for drone to have a global position estimate...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok and health.is_home_position_ok:
            print("-- Global position estimate OK")
            break

    print("-- Arming")
    await drone.action.arm()

    print("-- Setting initial setpoint")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))

    print("-- Starting offboard")
    try:
        await drone.offboard.start()
    except OffboardError as error:
        print(f"Starting offboard mode failed with error code: {error._result.result}")
        print("-- Disarming")
        await drone.action.disarm()
        return

    print("-- Go 0m North, 0m East, -40m Down within local coordinate system")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -40.0, 0.0))
    await asyncio.sleep(20)

    print("-- Go 50m North, 0m East, -20m Down within local coordinate system, turn to face East")
    await drone.offboard.set_position_ned(PositionNedYaw(50.0, 0.0, -40.0, 0.0))
    await asyncio.sleep(20)

    print("-- Go 50m North, 0m East, -20m Down within local coordinate system")
    await drone.offboard.set_position_ned(PositionNedYaw(50.0, 50.0, -40.0, 0.0))
    await asyncio.sleep(20)

    print("-- Go 0m North, 0m East, -20m Down within local coordinate system, turn to face South")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 50.0, -40.0, 0.0))
    await asyncio.sleep(20)


    print("-- Go 0m North, 0m East, -20m Down within local coordinate system, turn to face South")
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))
    await asyncio.sleep(50)

    print("-- Stopping offboard")
    try:
        await drone.offboard.stop()
    except OffboardError as error:
        print(f"Stopping offboard mode failed with error code: {error._result.result}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())