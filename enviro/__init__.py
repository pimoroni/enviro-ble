import enviro.constants as constants
from pimoroni_i2c import PimoroniI2C
from machine import Pin, PWM, Timer
import math
import time

# keep the power rail alive by holding VSYS_EN high as early as possible
# ===========================================================================
hold_vsys_en_pin = Pin(constants.HOLD_VSYS_EN_PIN, Pin.OUT, value=True)

# detect board model based on devices on the i2c bus and pin state
# ===========================================================================
i2c = PimoroniI2C(constants.I2C_SDA_PIN, constants.I2C_SCL_PIN, 100000)
i2c_devices = i2c.scan()
model = None


if 56 in i2c_devices:     # 56 = colour / light sensor and only present on Indoor
    model = "indoor"
elif 35 in i2c_devices:   # 35 = ltr-599 on grow & weather
    pump3_pin = Pin(12, Pin.IN, Pin.PULL_UP)
    model = "weather" if pump3_pin.value() else "grow"
    pump3_pin.init(pull=None)
else:    
    model = "urban"        # otherwise it's urban..


# return the module that implements this board type
def get_board():
    module = f"enviro.boards.{model}"
    return getattr(getattr(__import__(module), "boards"), model)
  

# set up the activity led
# ===========================================================================
activity_led_pwm = PWM(Pin(constants.ACTIVITY_LED_PIN))
activity_led_pwm.freq(1000)
activity_led_pwm.duty_u16(0)


# set the brightness of the activity led
def activity_led(brightness):
    brightness = max(0, min(100, brightness)) # clamp to range
    # gamma correct the brightness (gamma 2.8)
    value = int(pow(brightness / 100.0, 2.8) * 65535.0 + 0.5)
    activity_led_pwm.duty_u16(value)


activity_led_timer = Timer(-1)
activity_led_pulse_speed_hz = 1


def activity_led_callback(t):
    # updates the activity led brightness based on a sinusoid seeded by the current time
    brightness = (math.sin(time.ticks_ms() * math.pi * 2 / (1000 / activity_led_pulse_speed_hz)) * 40) + 60
    value = int(pow(brightness / 100.0, 2.8) * 65535.0 + 0.5)
    activity_led_pwm.duty_u16(value)


# set the activity led into pulsing mode
def pulse_activity_led(speed_hz = 1):
    global activity_led_timer, activity_led_pulse_speed_hz
    activity_led_pulse_speed_hz = speed_hz
    activity_led_timer.deinit()
    activity_led_timer.init(period=50, mode=Timer.PERIODIC, callback=activity_led_callback)


# turn off the activity led and disable any pulsing animation that's running
def stop_activity_led():
    global activity_led_timer
    activity_led_timer.deinit()
    activity_led_pwm.duty_u16(0)


# read the state of vbus to know if we were woken up by USB
vbus_present = Pin("WL_GPIO2", Pin.IN).value()


class logging:
    def info(self, *args, **kwargs):
      pass

    def debug(self, *args, **kwargs):
      pass