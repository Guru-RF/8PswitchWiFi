import time
import rtc
import board
import busio
from digitalio import DigitalInOut, Direction
from adafruit_esp32spi import adafruit_esp32spi, adafruit_esp32spi_wifimanager, PWMOut
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_rgbled
import adafruit_requests as requests
from adafruit_datetime import datetime
import adafruit_wsgi.esp32spi_wsgiserver as server
from adafruit_wsgi.wsgi_app import WSGIApp
import json 
import config

def purple(data):
  stamp = datetime.now()
  return "\x1b[38;5;104m[" + str(stamp) + "] " + data + "\x1b[0m"


def yellow(data):
  return "\x1b[38;5;220m" + data + "\x1b[0m"

def red(data):
  return "\x1b[1;5;31m -- " + data + "\x1b[0m"


# our version
VERSION = "RF.Guru_8P_Switch 0.1" 

# ports and self-test
port1 = DigitalInOut(board.GP0)
port1.direction = Direction.OUTPUT
port1.value = True

time.sleep(0.01)

port2 = DigitalInOut(board.GP1)
port2.direction = Direction.OUTPUT
port2.value = True

time.sleep(0.01)

port3 = DigitalInOut(board.GP2)
port3.direction = Direction.OUTPUT
port3.value = True

time.sleep(0.01)

port4 = DigitalInOut(board.GP3)
port4.direction = Direction.OUTPUT
port4.value = True

time.sleep(0.01)

port5 = DigitalInOut(board.GP23)
port5.direction = Direction.OUTPUT
port5.value = True

time.sleep(0.01)

port6 = DigitalInOut(board.GP22)
port6.direction = Direction.OUTPUT
port6.value = True

time.sleep(0.01)

port7 = DigitalInOut(board.GP21)
port7.direction = Direction.OUTPUT
port7.value = True

time.sleep(0.01)

port8 = DigitalInOut(board.GP20)
port8.direction = Direction.OUTPUT
port8.value = True

time.sleep(1)

ports = {
  "1": port1,
  "2": port2,
  "3": port3,
  "4": port4,
  "5": port5,
  "6": port6,
  "7": port7,
  "8": port8,
}

for number, port in ports.items():
    port.value = False
    time.sleep(0.01)

print(red(config.name + " -=- " + VERSION))

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

esp32_cs = DigitalInOut(board.GP17)
esp32_ready = DigitalInOut(board.GP14)
esp32_reset = DigitalInOut(board.GP13)

# Clock MOSI(TX) MISO(RX)
spi = busio.SPI(board.GP18, board.GP19, board.GP16)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)

if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print(yellow("\nESP32 found and in idle mode"))
print(yellow(("Firmware vers." + str(esp.firmware_version))))
print(yellow("MAC addr: "+ str([hex(i) for i in esp.MAC_address])))

RED_LED = PWMOut.PWMOut(esp, 25)
GREEN_LED = PWMOut.PWMOut(esp, 26)
BLUE_LED = PWMOut.PWMOut(esp, 27)
status_light = adafruit_rgbled.RGBLED(RED_LED, GREEN_LED, BLUE_LED)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)


## Connect to WiFi
print(yellow("\nConnecting to WiFi..."))
wifi.connect()
print(yellow("Connected!\n"))
  
print(yellow("Connected to [" + str(esp.ssid, "utf-8") + "] RSSI [" + str(esp.rssi) + "]"))

now = None
while now is None:
    try:
        now = time.localtime(esp.get_time()[0])
    except OSError:
        pass
rtc.RTC().datetime = now

# Web APP
web_app = WSGIApp()

@web_app.route("/port/<nr>")
def port_on(request, nr):
    wifi.pixel_status((0,100,100))
    try:
        for number, port in ports.items():
            port.value = False
        ports[str(int(nr))].value = True
        print(purple("PORT REQ: Turned port " + str(int(nr)) + " on"))

        ports_state = {}
        for number, port in ports.items():
            if port.value is True:
                ports_state[number] = True
            else:
                ports_state[number] = False
        json_object = json.dumps(ports_state)
        wifi.pixel_status((0,100,0))
        return ("200 OK", [], json_object)
    except:
        wifi.pixel_status((0,100,0))
        return ("400 NOK", [], "Error")


@web_app.route("/state")
def state(request):  # pylint: disable=unused-argument
    wifi.pixel_status((0,100,100))
    ports_state = {}

    for number, port in ports.items():
        if port.value is True:
            ports_state[number] = True
            print(purple("STATE REQ: Active port " + number))
        else:
            ports_state[number] = False
    json_object = json.dumps(ports_state)
    wifi.pixel_status((0,100,0))
    return ("200 OK", [], json_object)


# Here we setup our server, passing in our web_app as the application
server.set_interface(esp)
wsgiServer = server.WSGIServer(80, application=web_app)

print(yellow("IP addr: [" + str(esp.pretty_ip(esp.ip_address)) + "]\n"))

# default port
ports[str(int(config.default_port))].value = True
print(purple("Turned default port " + str(int(config.default_port)) + " on"))

# Start the server
wsgiServer.start()
while True:
    # Our main loop where we have the server poll for incoming requests
    try:
        wsgiServer.update_poll()
        # Could do any other background tasks here, like reading sensors
    except (ValueError, RuntimeError) as e:
        print("Failed to update server, restarting ESP32\n", e)
        wifi.reset()
        continue

