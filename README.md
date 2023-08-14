# Pico de la Red
## Grid Intensity on a Pi Pico Display (with clock)
A couple of years ago I made a Pi-based display to show the UK Grid Intensity and fuel mix - https://github.com/petecliff/ngmx_blinky

I made a new version now for a colleague of mine who is heading off to a new role. He likes microcontrollers so I made this version for a Pi Pico W and
Pimoroni's fancy Pico Display.

This is version 1 - it could do with a bit of work for error handling and maybe status updates on the screen (e.g. NTP failed or getting grid update).
One day I'll try threading the two timers too (as currently the grid update blocks the time update) and maybe adding a button listener to change
the display (e.g. toggle 'tween display_mix_1 and display_mix_2).

## Getting this working
If you've not already, get connection to the Pico working and flash the LED... :-)
https://projects.raspberrypi.org/en/projects/getting-started-with-the-pico

With Thonny setup, create a new folder with the content of this repo in it. Then copy `secrets.template.py` to `secrets.py` and put your wifi deets in.

Next check `main.py` and update the grid API URI to reflect your region - see https://carbon-intensity.github.io/api-definitions/#region-list for a list and
the map at https://carbonintensity.org.uk/.

Finally copy `main.py`, `startup.jpg` and `secrets.py` to `/` on the Pico using Thonny and restart the Pico.

Pico Display examples are here:

https://github.com/pimoroni/pimoroni-pico/tree/main/micropython/examples/pico_display

and this is worth a read if you want to change the startup image:

https://github.com/pimoroni/pimoroni-pico/blob/main/micropython/modules/picographics/README.md

## Startup Image
It one I took on the way to Thurso. The A9 to Thurso from Inverness is pretty exciting for wind turbine fans... :-)

