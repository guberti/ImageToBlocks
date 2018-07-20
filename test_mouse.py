import json, keyboard, time, mouse
with open('mouse_positions.json') as mouse_data:    
    POSITIONS = json.load(mouse_data)

MINOR_DELAY = 0.2
MAJOR_DELAY = MINOR_DELAY * 2
def select(invpos, MOUSE_POSITIONS): # 0-35
    time.sleep(MAJOR_DELAY) # Give time for MC to load inventory

    x_fact = invpos % 9
    y_fact = (invpos / 9) - 1

    x_diff = float(MOUSE_POSITIONS[1][0] - MOUSE_POSITIONS[0][0])/(8.0)
    y_diff = float(MOUSE_POSITIONS[1][1] - MOUSE_POSITIONS[0][1])/(2.0)

    x = MOUSE_POSITIONS[0][0] + x_diff*x_fact
    y = MOUSE_POSITIONS[0][1] + y_diff*y_fact

    mouse.move(x, y, absolute=True, duration=0)
    time.sleep(0.5)
    mouse.click()
    time.sleep(0.5)
    mouse.click()
    time.sleep(0.5)


print "Testing positions"
keyboard.wait('ctrl+r')
time.sleep(0.5)

keyboard.press_and_release("e") # Open inventory
time.sleep(.5)

for i in range (9, 36):
	select(i, POSITIONS)

time.sleep(.5)
keyboard.press_and_release('e')
time.sleep(0.5)
mouse.move(POSITIONS[2][0], POSITIONS[2][1], absolute=True, duration=0)