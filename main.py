from machine import Pin, Timer
from pimoroni import RGBLED
from secrets import ssid, password

import picographics
import jpegdec
import math
import ntptime
import network
import socket
import json
import time
from time import sleep
import machine
import urequests

display = picographics.PicoGraphics(display=picographics.DISPLAY_PICO_DISPLAY)

RED = display.create_pen(209, 34, 41)
ORANGE = display.create_pen(246, 138, 30)
YELLOW = display.create_pen(255, 216, 0)
GREEN = display.create_pen(0, 255, 64)
INDIGO = display.create_pen(36, 64, 142)
VIOLET = display.create_pen(115, 41, 130)
WHITE = display.create_pen(255, 255, 255)
PINK = display.create_pen(255, 175, 200)
BLUE = display.create_pen(116, 215, 238)
BROWN = display.create_pen(97, 57, 21)
GREY = display.create_pen(99, 99, 99)
BLACK = display.create_pen(0, 0, 0)
MAGENTA = display.create_pen(255, 33, 140)
CYAN = display.create_pen(33, 177, 255)

LED_INTENSITY_HIGH = ()
LED_INTENSITY_MOD = (2,1,0)
LED_INTENSITY_LOW = (0,1,0)

connect_timeout = 30
led = RGBLED(6, 7, 8)

grid_mix_uri = "https://api.carbonintensity.org.uk/regional/regionid/12"

HALF_HOUR = 30 * 60000
MINUTE = 60000
SECOND = 1000

PREV_TIME = "notset"

MONTH_ABBR = [ "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ]

pens = {
    "gas": INDIGO,
    "coal": RED,
    "biomass": BROWN,
    "nuclear": MAGENTA,
    "hydro": CYAN,
    "imports": GREY,
    "other": PINK,
    "wind": GREEN,
    "solar": YELLOW
}

mock_data = '{"data":[{"regionid":12,"dnoregion":"SSE South","shortname":"South England","data":[{"from":"2023-08-14T18:30Z","to":"2023-08-14T19:00Z","intensity":{"forecast":272,"index":"high"},"generationmix":[{"fuel":"biomass","perc":4.1},{"fuel":"coal","perc":2.6},{"fuel":"imports","perc":2.1},{"fuel":"gas","perc":61.5},{"fuel":"nuclear","perc":3.3},{"fuel":"other","perc":0},{"fuel":"hydro","perc":0.2},{"fuel":"solar","perc":4.2},{"fuel":"wind","perc":22.2}]}]}]}'

clock_timer = Timer()
grid_timer = Timer()

def connect():
    led.set_rgb(255,0,0)
    connect_count = 0
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        if connect_count > connect_timeout:
            raise Exception("Could not connect...")
        print('Waiting for connection...')
        sleep(1)
        connect_count += 1
    led.set_rgb(1,1,1)
    print("Wifi connected...")
    print(wlan)
    sleep(1)
    
def draw_startup():
    j = jpegdec.JPEG(display)
    j.open_file("startup.jpg")
    j.decode(0, 0, jpegdec.JPEG_SCALE_FULL, dither=True)

    display.set_font("cursive")
    display.set_thickness(3)
    display.text("pico de la red", 70, 35, scale=1, angle=90)
    display.update()

def set_intensity_led(intensity):
    print(intensity)
    intensity_index = intensity['index'].lower()
    if 'low' in intensity_index:
        led.set_rgb(0,1,0)
        return
    if 'high' in intensity_index:
        led.set_rgb(1,0,0)
        return
    if 'moderate' in intensity_index:
        led.set_rgb(2,1,0)
        return
    led.set_rgb(1,1,1)
    return
    
def draw_mix_1(gen_mix):
    clear_mix()
    print(gen_mix)
    dh = 135
    cstart = dh
    for fuel in gen_mix:
        cval = math.floor(fuel['perc'])
        cstart = cstart - cval
        display.set_pen(pens[fuel['fuel']])
        display.rectangle(cstart, 0, cval, 240)
    display.update()

def draw_mix_2(gen_mix):
    clear_mix()
    print(gen_mix)
    
    y = 6

    for fuel in gen_mix:
        cval = math.floor(fuel['perc'])
        display.set_pen(pens[fuel['fuel']])
        display.rectangle(32, y, cval, 20)
        y = y + 26
    display.update()

def clear_clock():
    display.set_pen(BLACK)
    display.rectangle(0,0,28,240)
    display.update()    

def clear_mix():
    display.set_pen(BLACK)
    display.rectangle(28, 0, 135, 240)
    display.update()
        
def clear():
    display.set_pen(BLACK)
    display.rectangle(0, 0, 135, 240)
    display.update()

def update_clock(timer):
    global PREV_TIME
    now = time.localtime()
    time_str = "{:02d} {} {} {:02d}:{:02d}".format(now[2], MONTH_ABBR[now[1]], now[0] - 2000,  now[3], now[4])
    if PREV_TIME != time_str:
        PREV_TIME = time_str
        clear_clock()
        display.set_font("sans")
        display.set_thickness(2)
        display.set_pen(WHITE)
        display.text(time_str, 12, 14, scale=0.8, angle=90)
        display.update()
    
def read_grid_api(grid_mix_uri):
    r = urequests.get(grid_mix_uri)
    res = json.loads(r.content)
    print(res)
#    res = json.loads(mock_data)
    r.close()
    return res['data'][0]

def update_grid(timer):
    print("Getting grid")
    grid_status_res = read_grid_api(grid_mix_uri)
    set_intensity_led(grid_status_res['data'][0]['intensity'])
    draw_mix_2(grid_status_res['data'][0]['generationmix'])
    
def set_time():
    time_set = False
    tries = 10
    while time_set == False:
        tries = tries - 1
        if tries == 0:
            print("Failed to connect to NTP")
            break
        try:
            ntptime.settime()
            time_set = True
        except Exception as e:
            print(e)
        
draw_startup()

connect()



update_clock(0) # sets current time
update_grid(0)
    
clock_timer.init(period=SECOND, mode=Timer.PERIODIC, callback=update_clock)
grid_timer.init(period=HALF_HOUR, mode=Timer.PERIODIC, callback=update_grid)