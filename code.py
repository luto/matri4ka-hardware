import time
import gc
import microcontroller
import busio
from adafruit_neotrellis.neotrellis import NeoTrellis
from adafruit_neotrellis.multitrellis import MultiTrellis
import wifi
import socketpool
import adafruit_requests as requests

OFF = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)


def show_state():
    for y in range(len(state)):
        for x in range(len(state[y])):
            if state[y][x] == 1:
                trellis.color(x, y, RED)
            else:
                trellis.color(x, y, OFF)

    trellis.show()


def request(method, url, *args, **kwargs):
    url = "http://matri4ka.com:44220%s" % url
    kwargs["headers"] = {"X-AUTH-TOKEN": "GeiDoh6ook2top9yevei"}
    print(method, url, args, kwargs)
    return http.request(method, url, *args, **kwargs, timeout=2)


def on_press(xcoord, ycoord, edge):
    y, x = xcoord, ycoord

    if state[x][y] == 1:
        new_state = 0
    else:
        new_state = 1

    request("GET", "/api/set?x=%s&y=%s&v=%s" % (x, y, new_state))

    state[x][y] = new_state
    show_state()


def make_neotrelli(addr):
    return NeoTrellis(i2c_bus, False, auto_write=False, addr=addr)


print("joining network...")
print(wifi.radio.connect(ssid="metalab",password=""))
print("IP address:", wifi.radio.ipv4_address)

socket = socketpool.SocketPool(wifi.radio)
http = requests.Session(socket)

i2c_bus = busio.I2C(microcontroller.pin.GPIO39, microcontroller.pin.GPIO37)  # SCL, SDA

trelli = [
    [make_neotrelli(0x30), make_neotrelli(0x2F), make_neotrelli(0x2E)],
    [make_neotrelli(0x33), make_neotrelli(0x32), make_neotrelli(0x31)],
    [make_neotrelli(0x36), make_neotrelli(0x35), make_neotrelli(0x34)],
]
state = []

trellis = MultiTrellis(trelli)
trellis.brightness = 0.1


for y in range(len(trelli) * 4):
    for x in range(len(trelli) * 4):
        trellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
        trellis.set_callback(x, y, on_press)
        time.sleep(0.02)


while True:
    trellis.sync()
    time.sleep(0.02)

    state = request("GET", "/api/state").json()
    show_state()
