import time

from micropython import const

import uasyncio as asyncio
import aioble
import bluetooth

import struct

import enviro

board = enviro.get_board()


# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.characteristic.temperature
_ENV_SENSE_TEMP_UUID = bluetooth.UUID(0x2A6E)
_ENV_SENSE_PRESS_UUID = bluetooth.UUID(0x2A6D)
_ENV_SENSE_HUM_UUID = bluetooth.UUID(0x2A6F)
_ENV_SENSE_RAIN_UUID = bluetooth.UUID(0x2A78)
_ENV_SENSE_IRRADIANCE = bluetooth.UUID(0x2A77)  # It's not Lux, but it'll do for now
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_THERMOMETER = const(768)

# How frequently to send advertising beacons.
_ADV_INTERVAL_MS = 250_000



class EnviroSensor(aioble.Characteristic):
    UUID = {
        "temperature": bluetooth.UUID(0x2A6E),
        "pressure": bluetooth.UUID(0x2A6D),
        "humidity": bluetooth.UUID(0x2A6F),
        "rain_per_second": bluetooth.UUID(0x2A78),
        "luminance": bluetooth.UUID(0x2A77)   # It's not Lux, but it'll do for now
    }

    def __init__(self, service, property, read=True, notify=True):
        aioble.Characteristic.__init__(self, service, self.UUID[property], read, notify)
        self.property = property
        self.encoder = getattr(self, f"_encode_{property}")

    def update_from_dict(self, readings):
        self.write(self.encoder(readings.get(self.property)))

    # Helper to encode the temperature characteristic encoding (sint16, hundredths of a degree).
    def _encode_temperature(self, temp_deg_c):
        return struct.pack("<h", int(temp_deg_c * 100))

    def _encode_pressure(self, press_pa):
        return struct.pack("<h", int(press_pa * 10))

    def _encode_humidity(self, hum):
        # uint16t: % with a resolution of 0.01
        return struct.pack("<h", int(hum * 100))

    def _encode_rain_per_second(self, rainfall):
        # uint16t: meters with a resolution of 1mm- so, basically mm then?!
        return struct.pack("<h", int(rainfall))

    def _encode_luminance(self, light):
        # 0.1 W/m2
        # 1 W/m2 ~= 120 Lux
        # 1,000 W/m2 (1 Sun) ~= 120,000 Lux
        scale = 120 / 10
        return struct.pack("<h", int(light / scale))


sensors = []

# Register GATT server.
environmental_sensing = aioble.Service(_ENV_SENSE_UUID)

# All boards have Temperature, Humidity and Pressure readings
sensors.append(EnviroSensor(environmental_sensing, "temperature"))
sensors.append(EnviroSensor(environmental_sensing, "humidity"))
sensors.append(EnviroSensor(environmental_sensing, "pressure"))

if board.model == "weather":
    sensors.append(EnviroSensor(environmental_sensing, "rain_per_second"))

if board.model in ("grow", "weather", "indoor"):
    sensors.append(EnviroSensor(environmental_sensing, "luminance"))

aioble.register_services(environmental_sensing)


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
        enviro.activity_led(100 * toggle)
        toggle = not toggle
        await asyncio.sleep_ms(1000)


# Run both tasks.
async def main():
    t1 = asyncio.create_task(sensor_task())
    t2 = asyncio.create_task(peripheral_task())
    t3 = asyncio.create_task(blink_task())
    await asyncio.gather(t1, t2, t3)


asyncio.run(main())

