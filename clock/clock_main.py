# Metro Matrix Clock
# Runs on Airlift Metro M4 with 64x32 RGB Matrix display & shield

import time
import board
import displayio
import terminalio
from adafruit_display_text.label import Label
from adafruit_bitmap_font import bitmap_font
from adafruit_matrixportal.network import Network
from adafruit_matrixportal.matrix import Matrix
import adafruit_fancyled.adafruit_fancyled as fancy

BLINK = True
DEBUG = False

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise
print("    Metro Minimal Clock")
print("Time will be set for {}".format(secrets["timezone"]))

# --- Display setup ---
matrix = Matrix()
display = matrix.display
network = Network(status_neopixel=board.NEOPIXEL, debug=False)

# --- Drawing setup ---
group = displayio.Group()
bitmap = displayio.Bitmap(64, 32, 2)  # Create a bitmap object,width, height, bit depth

# Create a TileGrid using the Bitmap and Palette
color_palette = displayio.Palette(1)
color_palette[0] = 0x080808
tile_grid = displayio.TileGrid(bitmap, pixel_shader=color_palette)
group.append(tile_grid)  # Add the TileGrid to the Group
display.show(group)

font = bitmap_font.load_font("/font-gomme.bdf")

clock_label = Label(font)

palette = [
   fancy.unpack(0x3a3a52),
   fancy.unpack(0x40405c),
   fancy.unpack(0x4a4969),
   fancy.unpack(0x515175),
   fancy.unpack(0x6f71aa),
   fancy.unpack(0x8a76ab),
   fancy.unpack(0xb1b5ea),
   fancy.unpack(0x82addb),
   fancy.unpack(0x94c5f8),
   fancy.unpack(0xa6e6ff),
   fancy.unpack(0x94dfff),
   fancy.unpack(0x9be2fe),
   fancy.unpack(0x90dffe),
   fancy.unpack(0x57c1eb),
   fancy.unpack(0x2d91c2),
   fancy.unpack(0x2473ab),
   fancy.unpack(0x265889),
   fancy.unpack(0x9da671),
   fancy.unpack(0xe9ce5d),
   fancy.unpack(0xe1c45e),
   fancy.unpack(0xb26339),
   fancy.unpack(0xB7490F),
   fancy.unpack(0x8A3B12),
   fancy.unpack(0x59230B),
]

def update_time(*, hours=None, minutes=None, seconds=None, show_colon=False):
    now = time.localtime()  # Get the time values we need
    if hours is None:
        hours = now[3]

    if minutes is None:
        minutes = now[4]

    if seconds is None:
        seconds = now[5]

    if minutes % 5 == 0:
        color = fancy.palette_lookup(palette, (hours*60. + minutes) / 1440.)
#        color = fancy.gamma_adjust(color, brightness=0.8)
        clock_label.color = color.pack()

    if BLINK:
        colon = ":" if show_colon or seconds % 2 else " "
    else:
        colon = ":"
    
    clock_label.text = "{hours:02d}{colon}{minutes:02d}".format(
        hours=hours, minutes=minutes, colon=colon
    )
    bbx, bby, bbwidth, bbh = clock_label.bounding_box
    # Center the label
    clock_label.x = round(display.width / 2 - bbwidth / 2)
    clock_label.y = round(display.height / 2 - bbh / 2)
    if DEBUG:
        #print("Label bounding box: {},{},{},{}".format(bbx, bby, bbwidth, bbh))
        #print("Label x: {} y: {}".format(clock_label.x, clock_label.y))
        print(f"{clock_label.text} with color {clock_label.color:08x}")


last_check = None
update_time(show_colon=True)  # Display whatever time is on the board
group.append(clock_label)  # add the clock label to the group

minute = 0
hour = 0
second = 0
while True:
    if last_check is None or time.monotonic() > last_check + 3600:
        try:
            update_time(
                show_colon=True
            )  # Make sure a colon is displayed while updating
            network.get_local_time()  # Synchronize Board's clock to Internet
            last_check = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
    update_time()
    time.sleep(1)
