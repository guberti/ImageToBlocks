# Author: B4E4
from PIL import Image
from blockmodel import BlockModel
import keyboard, mouse, pause
import sys, time, json, datetime, os
import pyaudio, struct, math

# Arguments
#IMAGE_PATH = "bear.png"
IMAGE_PATH = "protoTech_floor_v2_full.png"
#IMAGE_PATH = "nameplate.png"
MINOR_DELAY = 0.25
MAJOR_DELAY = MINOR_DELAY * 2
DELAY_BETWEEN_BLOCKS = 3.0 # Seconds
BLOCK_WIDTH = 16
GENERATE_FULL_PREVIEW = True
GENREATE_SCHEMATIC = False
DO_KEYPRESSES = True
CALIBRATE_DISTANCE = 64

IMAGE_DIRECTORY = IMAGE_PATH.split(".")[0] + "/"
PREV_PROGRESS_PATH = IMAGE_DIRECTORY + "save_progress.json"


with open('colors.json') as color_data:
    COLORS = json.load(color_data)

with open('block_ids.json') as color_data:    
    BLOCK_IDS = json.load(color_data)

with open('mouse_positions.json') as color_data:    
    MOUSE_POSITIONS = json.load(color_data)

# AUDIO DETECTION

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
VOLUME_CUTOFF = 0.1
TIME_TO_LISTEN = 5

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt16,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=2,
                frames_per_buffer=CHUNK)

def rms(data):
    count = len(data)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, data )
    sum_squares = 0.0
    for sample in shorts:
        n = sample * (1.0/32768)
        sum_squares += n*n
    return math.sqrt( sum_squares / count )

def get_closest(rgb):
    best_color_index = -1
    lowest_distance = 3 * (255**2) + 1 # > max distance

    for color_index in range (0, len(COLORS)):
        dist = (COLORS[color_index][1][0] - rgb[0])**2 + \
               (COLORS[color_index][1][1] - rgb[1])**2 + \
               (COLORS[color_index][1][2] - rgb[2])**2

        if dist < lowest_distance:
            best_color_index = color_index
            lowest_distance = dist

    return best_color_index

def get_block_id_meta(name):
    for block in BLOCK_IDS:
        if block['text_type'] == name:
            return [block['type'], block['meta']]
    print "Could not find id for '" + name + "'"
    print "Aborting program..."
    sys.exit()
#
# Slot breakdown:
# (x=0)                           (x=9)
# [27, 28, 29, 30, 31, 32, 33, 34, 35] (y=2)
# [18, 19, 20, 21, 22, 23, 24, 25, 26]
# [09, 10, 11, 12, 13, 14, 15, 16, 17] (y=0)
# ------------------------------------
# [00, 01, 02, 03, 04, 05, 06, 07, 08]

def switch_to_hotbar(invpos, hotbar): # 0-35
    time.sleep(MINOR_DELAY)
    keyboard.press_and_release("e") # Open inventory
    time.sleep(MAJOR_DELAY) # Give time for MC to load inventory

    x_fact = invpos % 9
    y_fact = (invpos / 9) - 1

    x_diff = float(MOUSE_POSITIONS[1][0] - MOUSE_POSITIONS[0][0])/(8.0)
    y_diff = float(MOUSE_POSITIONS[1][1] - MOUSE_POSITIONS[0][1])/(2.0)

    x = MOUSE_POSITIONS[0][0] + x_diff*x_fact
    y = MOUSE_POSITIONS[0][1] + y_diff*y_fact

    mouse.move(x, y, absolute=True, duration=0)
    time.sleep(MINOR_DELAY)
    keyboard.press_and_release(str(hotbar + 1))
    time.sleep(MINOR_DELAY)
    keyboard.press_and_release("e") # Close inventory
    time.sleep(MAJOR_DELAY)

def right_click():
    counts = 0
    while True:
        mouse.right_click()
        time.sleep(0.20)
        mouse.right_click()
        time.sleep(0.20)
        mouse.right_click()
        break
        '''for i in range(0, int(RATE / CHUNK * TIME_TO_LISTEN)):
            vol = rms(stream.read(CHUNK))
            #print vol
            if vol > VOLUME_CUTOFF:
                return
        print "Did not hear note block!"
        print "Placing block again"
        counts += 1
        print "This has happened " + str(counts) + " times this block"'''


im = Image.open(IMAGE_PATH)
pix = im.load()

if GENERATE_FULL_PREVIEW:
    complete_preview = Image.new('RGB', (im.size[0] * 16, im.size[1] * 16))
    preview_pix = complete_preview.load()
    compl_prev_index = 0

if GENREATE_SCHEMATIC:
    schematic_source = []

print "Loading '" + IMAGE_PATH + "'"
print "Dimensions (w, h): " + str(im.size)

SLOT_ASSIGNMENTS = []
SLOT_COUNTS = []

#if len(pix[0,0])

for i in range(0, im.size[0]):
    for k in range(0, im.size[1]):
        #print pix[i,k]

        best_color_index = get_closest(pix[i,k])

        # Edit and export the image
        pix[i,k] = tuple(COLORS[best_color_index][1])

        if GENERATE_FULL_PREVIEW:
            block_pix = Image.open('textures/' + COLORS[best_color_index][0] + '.png', 'r')
            complete_preview.paste(block_pix, (i*BLOCK_WIDTH, k*BLOCK_WIDTH))

        if GENREATE_SCHEMATIC:
            id_meta = get_block_id_meta(COLORS[best_color_index][0])
            schematic_source.append([i, 0, k, id_meta[0], id_meta[1]])

        # We now know the best color
        # If we already know we need it, add it to tally
        if (best_color_index in SLOT_ASSIGNMENTS):
            SLOT_COUNTS[SLOT_ASSIGNMENTS.index(best_color_index)] += 1
            continue

        # If we have nine colors and need another, stop running
        if len(SLOT_ASSIGNMENTS) > 360:
            print "We need " + COLORS[best_color_index][0] + \
            " but we're out of slots!"
            print "Aborting program..."
            sys.exit()

        # Otherwise, add our color
        SLOT_ASSIGNMENTS.append(best_color_index)
        print "Slot " + str(len(SLOT_ASSIGNMENTS)) + \
        ": " + COLORS[best_color_index][0]
        SLOT_COUNTS.append(1)

print "--"
print "Block counts:"
print
for s in range(0, len(SLOT_ASSIGNMENTS)):
    print COLORS[SLOT_ASSIGNMENTS[s]][0] + ": " + str(SLOT_COUNTS[s])
print
print "Image loaded"

PRESSES = ""

# Export preview
if not os.path.exists(IMAGE_DIRECTORY[:-1]):
    os.makedirs(IMAGE_DIRECTORY[:-1])

outpath = IMAGE_DIRECTORY + "preview." + IMAGE_PATH.split(".")[1]
im.save(outpath)
print "Preview exported as '" + outpath + "'"

if GENERATE_FULL_PREVIEW:
    complete_outpath = IMAGE_DIRECTORY + \
        "complete." + IMAGE_PATH.split(".")[1]
    complete_preview.save(complete_outpath)
    print "Detailed preview exported as '" + complete_outpath + "'"

if GENREATE_SCHEMATIC:
    schematic_outpath = IMAGE_DIRECTORY + ".schematic"
    bobj = BlockModel.from_sparse_json(json.dumps(schematic_source), max_size=None)
    with open(schematic_outpath, 'wb') as f:
        f.write(bobj.schematic)
    print "Schematic exported as '" + schematic_outpath + "'"

COLOR_ORDER = []
for i in range(0, im.size[0]):
    for k in reversed(range(0, im.size[1])):
        best_color_index = get_closest(pix[i,k])
        if (not len(COLOR_ORDER)) or COLOR_ORDER[-1] != best_color_index:
            COLOR_ORDER.append(best_color_index)

print "Calculated ordering (length " + str(len(COLOR_ORDER)) + ")"

e_time = (DELAY_BETWEEN_BLOCKS) * im.size[0] * im.size[1]
print "Estimated time: " + str(e_time) + " seconds"
print "Press CTRL+SHIFT+O to start placing"
keyboard.wait('ctrl+shift+o')
time.sleep(1)
print "Starting placer..."

prev_best_index = get_closest(pix[0,0])

# Calculate starting positions
i_start = 0
k_start = im.size[1]
print im.size[1]
if os.path.isfile(PREV_PROGRESS_PATH):
    with open(PREV_PROGRESS_PATH) as start_data:    
        starts = json.load(start_data)
        i_start = starts["i"]
        k_start = starts["k"]
        print "Resuming progress from " + str(start_data)

print "SIZE: " + str(im.size[1])

blocks_placed = 0

for i in range(i_start, im.size[0]):
    k = im.size[1]
    while k > 0:
        k -= 1

        # Account for starting positions
        if k_start < im.size[1]:
            k = k_start

        # Now, we're in the right position
        # Make sure we don't skip again
        k_start = im.size[1]

        best_color_index = get_closest(pix[i,k])
        #print "Want to place " + COLORS[best_color_index][0]

        print "NUMS: " + str(i) + ", " + str(k)
        if (best_color_index != prev_best_index):
            COLOR_ORDER.pop(0)
        prev_best_index = best_color_index

        slot = SLOT_ASSIGNMENTS.index(best_color_index)

        # Navigate to correct block
        if slot <= 8: # Use arrow keys
            #print "Placed " + str(COLORS[SLOT_ASSIGNMENTS[slot]][0])
            PRESSES += str(slot+1)

            if DO_KEYPRESSES:
                keyboard.press_and_release(str(slot+1))
                time.sleep(0.05)
                keyboard.press_and_release(str(slot+1))
                time.sleep(0.05)
                time.sleep(DELAY_BETWEEN_BLOCKS / 2.0)
                right_click()
                time.sleep(DELAY_BETWEEN_BLOCKS / 2.0)
        else:
            # We need to figure out which block we'll use last
            slot_to_replace = -1
            distance_to_replaced = -1
            for j in range (0, 9):
                try:
                    d = COLOR_ORDER.index(SLOT_ASSIGNMENTS[j])
                    if d > distance_to_replaced:
                        distance_to_replaced = d
                        slot_to_replace = j
                except ValueError: # No more occurrances
                    slot_to_replace = j
                    break # We can't do any better

            # Switch the positions in our list

            SLOT_ASSIGNMENTS[slot], SLOT_ASSIGNMENTS[slot_to_replace] = \
            SLOT_ASSIGNMENTS[slot_to_replace], SLOT_ASSIGNMENTS[slot]

            #print "Placed " + str(COLORS[SLOT_ASSIGNMENTS[slot]][0])
            PRESSES += str(slot+1)

            if DO_KEYPRESSES:
                switch_to_hotbar(slot, slot_to_replace)
                # Click the mouse
                keyboard.press_and_release(str(slot_to_replace + 1))

                time.sleep(DELAY_BETWEEN_BLOCKS / 2.0)
                right_click()
                # Wait any extra time
                time.sleep(DELAY_BETWEEN_BLOCKS / 2.0)

        blocks_placed += 1 # We just placed a block

        # Check if we need to recalibrate
        if blocks_placed % CALIBRATE_DISTANCE == 0:
            keyboard.press("space")
            time.sleep(1)
            keyboard.release("space")
            time.sleep(5) # 5 seconds to reset is generous

        # Check if we should pause
        if keyboard.is_pressed('p'):
            print "Pausing program, press CTRL+SHIFT+O to continue"
            print "Or, press CTRL+SHIFT+X to save progress and stop"
            while (True):
                if keyboard.is_pressed('ctrl+shift+o'):
                    print "Program resumed"
                    break
                if keyboard.is_pressed('ctrl+shift+x'):
                    print "Saving progress..."
                    progress = {"i": i, "k": k - 1}
                    f = open(PREV_PROGRESS_PATH, 'w')
                    f.write(json.dumps(progress))
                    print "Progress saved"
                    sys.exit()


    print "Finished column " + str(i+1) + "/" + str(im.size[0]) + " at " + str(time.time())

print "---------------"
print "Finished placing '" + IMAGE_PATH + "'"

print PRESSES

if GENERATE_FULL_PREVIEW:
    complete_outpath = IMAGE_DIRECTORY + \
        "actual_complete." + IMAGE_PATH.split(".")[1]
    complete_preview.save(complete_outpath)
    print "Detailed preview exported as '" + complete_outpath + "'"