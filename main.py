from machine import Pin, Timer
from pimoroni import RGBLED, Button
from secrets import ssid, password
from summertime import summerTime

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
ntptime.host= "uk.pool.ntp.org"

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

LED_INTENSITY_HIGH = (1,0,0)
LED_INTENSITY_MOD = (2,1,0)
LED_INTENSITY_LOW = (0,1,0)

DAY = 60000 * 60 * 24
HALF_HOUR = 30 * 60000
MINUTE = 60000
SECOND = 1000

button_a = Button(12)
button_b = Button(13)
button_x = Button(14)
button_y = Button(15)

displayType = 0

pens = {
    "gas": CYAN,
    "coal": RED,
    "biomass": BROWN,
    "nuclear": MAGENTA,
    "hydro": INDIGO,
    "imports": VIOLET,
    "other": GREY,
    "wind": GREEN,
    "solar": YELLOW
}

month_abbr = [ "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ]

grid_mix_uri = "https://api.carbonintensity.org.uk/regional/regionid/12"

prev_time = "notset"

connect_tries = 30

led = RGBLED(6, 7, 8)

# mock_data = '{"data":[{"regionid":12,"dnoregion":"SSE South","shortname":"South England","data":[{"from":"2023-08-14T18:30Z","to":"2023-08-14T19:00Z","intensity":{"forecast":272,"index":"high"},"generationmix":[{"fuel":"biomass","perc":4.1},{"fuel":"coal","perc":2.6},{"fuel":"imports","perc":2.1},{"fuel":"gas","perc":61.5},{"fuel":"nuclear","perc":3.3},{"fuel":"other","perc":0},{"fuel":"hydro","perc":0.2},{"fuel":"solar","perc":4.2},{"fuel":"wind","perc":22.2}]}]}]}'

clock_timer = Timer()
grid_timer = Timer()
time_sync_timer = Timer()
button_timer = Timer()

def connect():
    led.set_rgb(132,0,132)
    connect_count = 0
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        if connect_count > connect_tries:
            raise Exception("Could not connect wifi...")
        print('Waiting for wifi connection...')
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

    display.set_pen(WHITE)
    display.set_font("cursive")
    display.set_thickness(2)
    display.text("pico de la red", 70, 35, scale=1, angle=90)
    display.update()

def set_intensity_led(intensity):
    #print(intensity)
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
    
def draw_mix(gen_mix, displayType):
    if displayType == 0:
        clear_mix()
        #print(gen_mix)
        dh = 135
        cstart = dh
        for fuel in gen_mix:
            cval = math.floor(fuel['perc'])
            cstart = cstart - cval
            display.set_pen(pens[fuel['fuel']])
            display.rectangle(cstart, 0, cval, 240)
        display.update()

    if displayType == 1:
        clear_mix()    
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
    global prev_time
    
    curr_time = time.time()
    if summerTime(time.localtime(curr_time)):
        curr_time = curr_time + 3600
    
    now = time.localtime(curr_time)
    
    time_str = "{:02d} {} {} {:02d}:{:02d}".format(now[2], month_abbr[now[1]], now[0] - 2000,  now[3], now[4])
    if prev_time != time_str:
        prev_time = time_str
        clear_clock()
        display.set_font("sans")
        display.set_thickness(2)
        display.set_pen(WHITE)
        display.text(time_str, 12, 14, scale=0.8, angle=90)
        display.update()
    
def read_grid_api(grid_mix_uri):
    r = urequests.get(grid_mix_uri)
    res = json.loads(r.content)
    #print(res)
    r.close()
    return res['data'][0]

def update_grid(timer):
    #print("Getting grid")
    grid_status_res = read_grid_api(grid_mix_uri)
    set_intensity_led(grid_status_res['data'][0]['intensity'])
    
    draw_mix(grid_status_res['data'][0]['generationmix'], displayType=displayType)
    
def sync_time(timer):
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

def button_check(timer):
    global displayType
    
    if button_a.read():
        displayType = 0
        clear_mix()
        grid_status_res = read_grid_api(grid_mix_uri)
        set_intensity_led(grid_status_res['data'][0]['intensity'])
        draw_mix(grid_status_res['data'][0]['generationmix'], displayType=displayType)

    if button_b.read():
        displayType = 1
        clear_mix()
        grid_status_res = read_grid_api(grid_mix_uri)
        set_intensity_led(grid_status_res['data'][0]['intensity'])
        draw_mix(grid_status_res['data'][0]['generationmix'], displayType=displayType)
        
draw_startup()

connect()

sync_time(0)
update_clock(0) # sets current time
update_grid(0)
    
clock_timer.init(period=SECOND, mode=Timer.PERIODIC, callback=update_clock)
grid_timer.init(period=HALF_HOUR, mode=Timer.PERIODIC, callback=update_grid)
time_sync_timer.init(period=DAY, mode=Timer.PERIODIC, callback=sync_time)
button_timer.init(period=500, mode=Timer.PERIODIC, callback=button_check)