import sys
import time

from micropython import const

import uasyncio as asyncio
import aioble
import bluetooth

import enviroble
from enviroble.helpers import uid
from enviroble.constants import ENVIRO_BLE_VERSION

board = enviroble.get_board()


# org.bluetooth.service.enviro_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
_DEVICE_INFO_UUID = bluetooth.UUID(0x180A)

# org.bluetooth.characteristic.temperature
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)

# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 250_000



device_info = aioble.Service(_DEVICE_INFO_UUID)
# Manufacturer
aioble.Characteristic(device_info, bluetooth.UUID(0x2A29), read=True, initial="Pimoroni")
# Model
aioble.Characteristic(device_info, bluetooth.UUID(0x2A24), read=True, initial=board.model)
# Serial
aioble.Characteristic(device_info, bluetooth.UUID(0x2A25), read=True, initial=uid())
# FW Version
aioble.Characteristic(device_info, bluetooth.UUID(0x2A26), read=True, initial=sys.version)
# Enviro BLE Version
aioble.Characteristic(device_info, bluetooth.UUID(0x2A28), read=True, initial=ENVIRO_BLE_VERSION)

sensors = []

enviro_sensing = aioble.Service(_ENV_SENSE_UUID)

# All boards have Temperature, Humidity and Pressure readings
sensors.append(enviroble.EnviroSensor(enviro_sensing, "temperature"))
sensors.append(enviroble.EnviroSensor(enviro_sensing, "humidity"))
sensors.append(enviroble.EnviroSensor(enviro_sensing, "pressure"))

if board.model == "weather":
    sensors.append(enviroble.EnviroSensor(enviro_sensing, "rain_per_second"))
    sensors.append(enviroble.EnviroSensor(enviro_sensing, "wind_direction"))

if board.model in ("grow", "weather", "indoor"):
    sensors.append(enviroble.EnviroSensor(enviro_sensing, "luminance"))

aioble.register_services(enviro_sensing, device_info)


# This would be periodically polling a hardware sensor.
async def sensor_task():
    last_reading = time.ticks_ms()
    while True:
        seconds_since_last = (time.ticks_ms() - last_reading) / 1000
        readings = board.get_sensor_readings(seconds_since_last)
        print(readings)
        last_reading = time.ticks_ms()
        for sensor in sensors:
            sensor.update_from_dict(readings)
        await asyncio.sleep_ms(1000 * 60)


# Serially wait for connections. Don't advertise while a central is
# connected.
async def peripheral_task():
    while True:
        try:
            async with await aioble.advertise(
                _ADV_INTERVAL_MS,
                name=f"enviro-{board.model}",
                services=[_ENV_SENSE_UUID],
                appearance=_ADV_APPEARANCE_GENERIC_THERMOMETER,
            ) as connection:
                print("Connection from", connection.device)
                await connection.disconnected()
        except asyncio.CancelledError:
            print("Disconnected?")


async def blink_task():
    toggle = True
    while True:
        enviroble.activity_led(100 * toggle)
        toggle = not toggle
        await asyncio.sleep_ms(1000)


# Run both tasks.
async def main():
    t1 = asyncio.create_task(sensor_task())
    t2 = asyncio.create_task(peripheral_task())
    t3 = asyncio.create_task(blink_task())
    await asyncio.gather(t1, t2, t3)


asyncio.run(main())
