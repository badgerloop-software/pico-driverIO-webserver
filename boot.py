"""
Boot script for Raspberry Pi Pico W
This file runs automatically when the Pico boots up.
"""

from machine import Pin

# Turn on the onboard LED to indicate power
led = Pin("LED", Pin.OUT)
led.on()

# Import and run the main web server
import main
main.main()