import board
import busio
import time
from digitalio import DigitalInOut, Direction
import adafruit_requests as requests
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
from adafruit_esp32spi import adafruit_esp32spi

print("ESP32 SPI hardware test")

esp32_cs = DigitalInOut(board.GP17)
esp32_ready = DigitalInOut(board.GP14) # ESP BUSY ?
esp32_reset = DigitalInOut(board.GP13) # EN ?
esp32_gpio0 = DigitalInOut(board.GP12)

port1 = DigitalInOut(board.GP0)
port1.direction = Direction.OUTPUT
port1.value = True

time.sleep(0.25)

port2 = DigitalInOut(board.GP1)
port2.direction = Direction.OUTPUT
port2.value = True

time.sleep(0.25)

port3 = DigitalInOut(board.GP2)
port3.direction = Direction.OUTPUT
port3.value = True

time.sleep(0.25)

port4 = DigitalInOut(board.GP3)
port4.direction = Direction.OUTPUT
port4.value = True

time.sleep(0.25)

port5 = DigitalInOut(board.GP23)
port5.direction = Direction.OUTPUT
port5.value = True

time.sleep(0.25)

port6 = DigitalInOut(board.GP22)
port6.direction = Direction.OUTPUT
port6.value = True

time.sleep(0.25)

port7 = DigitalInOut(board.GP21)
port7.direction = Direction.OUTPUT
port7.value = True

time.sleep(0.25)

port8 = DigitalInOut(board.GP20)
port8.direction = Direction.OUTPUT
port8.value = True

time.sleep(1)

port8.value = False
time.sleep(0.25)
port7.value = False
time.sleep(0.25)
port6.value = False
time.sleep(0.25)
port5.value = False
time.sleep(0.25)
port4.value = False
time.sleep(0.25)
port3.value = False
time.sleep(0.25)
port2.value = False
time.sleep(0.25)
port1.value = False

# Clock MOSI(TX) MISO(RX)
spi = busio.SPI(board.GP18, board.GP19, board.GP16)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset, esp32_gpio0)

requests.set_socket(socket, esp)

if esp.status == adafruit_esp32spi.WL_IDLE_STATUS:
    print("ESP32 found and in idle mode")
print("Firmware vers.", esp.firmware_version)
print("MAC addr:", [hex(i) for i in esp.MAC_address])

for ap in esp.scan_networks():
    print("\t%s\t\tRSSI: %d" % (str(ap['ssid'], 'utf-8'), ap['rssi']))

print("Done!")
