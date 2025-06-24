import time
from hx711 import HX711  # Make sure you have installed the HX711 library

# Set up HX711 (update pin numbers as needed for your wiring)
DT_PIN = 5   # Example GPIO pin for DT
SCK_PIN = 6  # Example GPIO pin for SCK

hx = HX711(DT_PIN, SCK_PIN)
hx.set_reading_format("MSB", "MSB")
hx.reset()
time.sleep(1)

# Tare the scale (zero it)
hx.tare()
time.sleep(1)

# Manually set this after calibration with a 1kg weight
# Place a 1kg weight on the load cell, then read the value and set it here
# Example: 1kg_reading = hx.get_weight(5)
# Replace the value below with your actual 1kg reading
one_kg_reading = 100000  # Replace with your actual reading for 1kg


def getLoad():
    global _last_call
    now = time.time()
    if now - _last_call < 0.01:  # 10ms = 0.01s
        time.sleep(0.01 - (now - _last_call))
    _last_call = time.time()
    raw = hx.get_weight(5)
    # Convert raw value to kg
    weight_kg = raw / one_kg_reading
    weight_lbs = weight_kg * 2.20462
    weight_newtons = weight_kg * 9.80665
    return [weight_newtons, weight_lbs, weight_kg, raw]


