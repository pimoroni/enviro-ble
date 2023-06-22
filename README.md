# Enviro MicroPython - Bluetooth Low-energy Firmware <!-- omit in toc -->

- [About Enviro BLE](#about-enviro-ble)
- [About Enviro](#about-enviro)
- [Powering Enviro boards](#powering-enviro-boards)
- [Supported products](#supported-products)

## About Enviro BLE

Enviro BLE is an alternate firmware for your Pimoroni Enviro boards that blasts sensor readings over Bluetooth low-energy.

The focus here is upon making each Enviro board as simple as possible- there's no on-device logging, no data upload, nothing to configure. It's just plug and play!

You must use a client Pico W, a Raspberry Pi or other BLE-enabled device to gather and make sense of these readings. We'll provide a small client library to give you some clues how to do this, but each board advertises two services:

* Device Information
* Environmental Sensing

Device Information includes the make (that's us, Pimoroni) the model (one of "indoor", "weather", "urban" or "grow"), the serial number (a unique ID provided by the Pico W's onboard flash chip), the Firmware version (that's the version of our custom MicroPython) and, finally, the Software version (that's the version of Enviro BLE currently running).

With this information you should be able to figure out which board you're talking to, though in practise it doesn't necessarily matter since you can peek at the Environmental Sensing service to see what sensors are available.

## About Enviro

Our Enviro range of boards offer a wide array of environmental sensing and data logging functionality. They are designed to be setup in location for months at a time and take regular measurements.

On top of their individual features the boards all share a common set of functions:

- on-board Pico W with RP2040 MCU and WiFi functionality
- accurate real-time clock (RTC) to maintain the time between boots
- a collection of wake event triggers (user button, RTC, external trigger)
- battery power input suitable for 1.8-5.5V input (ideal for 2x or 3x alkaline/NiMH cells or a single cell LiPo)
- reset button for frictionless debugging
- user button to trigger wake events or enter provisioning mode
- activity and warn LEDs to show current status
- Qw/ST connector to allow you to customise your sensor suite

These common features mean that the modules can run off very little power for long periods of time. During sleep (when the RTC remains active) the boards only consume a few microamps of power meaning they can last for months on a small battery pack. The modules wake up at regular intervals (or on a fixed schedule) to take a reading, store it, and go back to sleep.

## Powering Enviro boards

Enviro boards are designed to run for months on a set of batteries so that you can install them wherever they can gather the best data - perhaps on that high shelf in the corner of the kitchen that you can't quite reach, under a Stevenson screen in the back garden, or tucked in the shed.

You can use 3xAA or 3xAAA (either alkaline or NiMH), a single cell LiPo battery, or a USB cable to power Enviro boards.

## Supported products

- Enviro Indoor ([store link](https://shop.pimoroni.com/products/enviro-indoor))
- Enviro Grow ([store link](https://shop.pimoroni.com/products/enviro-grow))
- Enviro Weather ([store link](https://shop.pimoroni.com/products/enviro-weather))
- Enviro Urban ([store link](https://shop.pimoroni.com/products/enviro-urban))
