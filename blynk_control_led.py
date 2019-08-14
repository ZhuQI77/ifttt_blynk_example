import BlynkLib
import time
import threading
from gpiozero import LED

# Initialize Blynk
blynk = BlynkLib.Blynk('RGPzrL9DYGvbFDXmjj7zSJwHvrdUomGX')
humidity_led = LED(17)
temperature_led = LED(18)

def led_switch(led, daley):
    for i in range(0, daley):
        if ((i % 2) == 0):
            led.on()
        else:
            led.off()
        time.sleep(1)
    led.off()

# Register Virtual Pins
@blynk.VIRTUAL_WRITE(1)
def my_write_handler(value):
    if 1 != len(value):
        return
    print('Current V1 value: {}'.format(value))
    if value[0] == '2':
        print('temperature geen led')
        t_temperature = threading.Thread(target=led_switch, args=(temperature_led, 3))
        t_temperature.start()
    if value[0] == '1':
        print('humidity red led')
        t_humidity = threading.Thread(target=led_switch, args=(humidity_led, 3))
        t_humidity.start()

@blynk.VIRTUAL_READ(2)
def my_read_handler():
    # this widget will show some time in seconds..
    v2var = int(time.time())
    blynk.virtual_write(2, v2var)
    print('send to v2 value %d' % v2var)
while True:
    blynk.run()
