import enviro.constants as constants
import machine
import math


# miscellany
# ===========================================================================
def uid():
    return "{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}{:02x}".format(
        *machine.unique_id())


# temperature and humidity helpers
# ===========================================================================

# https://www.calctool.org/atmospheric-thermodynamics/absolute-humidity#what-is-and-how-to-calculate-absolute-humidity
def relative_to_absolute_humidity(relative_humidity, temperature_in_c):
    temperature_in_k = celcius_to_kelvin(temperature_in_c)
    actual_vapor_pressure = get_actual_vapor_pressure(relative_humidity, temperature_in_k)

    return actual_vapor_pressure / (constants.WATER_VAPOR_SPECIFIC_GAS_CONSTANT * temperature_in_k)


def absolute_to_relative_humidity(absolute_humidity, temperature_in_c):
    temperature_in_k = celcius_to_kelvin(temperature_in_c)
    saturation_vapor_pressure = get_saturation_vapor_pressure(temperature_in_k)

    return (constants.WATER_VAPOR_SPECIFIC_GAS_CONSTANT * temperature_in_k * absolute_humidity) / saturation_vapor_pressure * 100


def celcius_to_kelvin(temperature_in_c):
    return temperature_in_c + 273.15


# https://www.calctool.org/atmospheric-thermodynamics/absolute-humidity#actual-vapor-pressure
# http://cires1.colorado.edu/~voemel/vp.html
def get_actual_vapor_pressure(relative_humidity, temperature_in_k):
    return get_saturation_vapor_pressure(temperature_in_k) * (relative_humidity / 100)


def get_saturation_vapor_pressure(temperature_in_k):
    v = 1 - (temperature_in_k / constants.CRITICAL_WATER_TEMPERATURE)

    # empirical constants
    a1 = -7.85951783
    a2 = 1.84408259
    a3 = -11.7866497
    a4 = 22.6807411
    a5 = -15.9618719
    a6 = 1.80122502

    return constants.CRITICAL_WATER_PRESSURE * math.exp(
           constants.CRITICAL_WATER_TEMPERATURE /
           temperature_in_k *
           (a1 * v + a2 * v ** 1.5 +
            a3 * v ** 3 +
            a4 * v ** 3.5 +
            a5 * v ** 4 +
            a6 * v ** 7.5)
    )
