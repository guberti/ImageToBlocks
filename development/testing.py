from PIL import Image
from blockmodel import BlockModel
import keyboard, mouse, pause
import sys, time, json, datetime

MINOR_DELAY = 0.05
MAJOR_DELAY = MINOR_DELAY * 2

with open('mouse_positions.json') as color_data:    
    MOUSE_POSITIONS = json.load(color_data)

def switch_to_first_hotbar_slot(slot): # 0-35
    time.sleep(MINOR_DELAY)
    if slot <= 8:
        mouse.move(MOUSE_POSITIONS[2][0], \
            MOUSE_POSITIONS[2][1], absolute=True, duration=0)
    else:
        x_fact = slot % 9
        y_fact = (slot / 9) - 1
        print y_fact

        x_diff = float(MOUSE_POSITIONS[1][0] - MOUSE_POSITIONS[0][0])/(8.0)
        y_diff = float(MOUSE_POSITIONS[1][1] - MOUSE_POSITIONS[0][1])/(2.0)
        print y_diff

        x = MOUSE_POSITIONS[0][0] + x_diff*x_fact
        y = MOUSE_POSITIONS[0][1] + y_diff*y_fact
        print y
        print "-"

        mouse.move(x, y, absolute=True, duration=0)

keyboard.wait("ctrl+r")
time.sleep(1)
keyboard.press_and_release("e") # Open inventory
for i in range(0, 36):
	switch_to_first_hotbar_slot(i)
	time.sleep(0.25)
	switch_to_first_hotbar_slot(i)
	time.sleep(0.25)