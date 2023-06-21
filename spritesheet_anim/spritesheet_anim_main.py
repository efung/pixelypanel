import time
import os
import board
import displayio
from digitalio import DigitalInOut, Pull
from adafruit_matrixportal.matrix import Matrix
from adafruit_debouncer import Debouncer

SPRITESHEET_FOLDER = "/bmps"
DEFAULT_FRAME_DURATION = 0.1  # 100ms

# --- Display setup ---
matrix = Matrix(bit_depth=4)
sprite_group = displayio.Group()
matrix.display.show(sprite_group)

# --- Button setup ---
pin_down = DigitalInOut(board.BUTTON_DOWN)
pin_down.switch_to_input(pull=Pull.UP)
button_down = Debouncer(pin_down)
pin_up = DigitalInOut(board.BUTTON_UP)
pin_up.switch_to_input(pull=Pull.UP)
button_up = Debouncer(pin_up)

file_list = [
    "shoppy-horiz.bmp",
    ]

if len(file_list) == 0:
    raise RuntimeError("No images found")

current_image = 0
current_frame = 0
frame_count = 0
frame_duration = DEFAULT_FRAME_DURATION

def load_background():
    bg_bitmap = displayio.Bitmap(64, 32, 1)
    bg_palette = displayio.Palette(1)
    bg_palette[0] = 0x000b16
    bg_sprite = displayio.TileGrid(
        bg_bitmap,
        pixel_shader=bg_palette
    )

    sprite_group.append(bg_sprite)

def load_image():
    """
    Load an image as a sprite
    """
    # pylint: disable=global-statement
    global current_frame, frame_count, frame_duration

    filename = SPRITESHEET_FOLDER + "/" + file_list[current_image]

    # CircuitPython 7+ compatible
    bitmap = displayio.OnDiskBitmap(filename)
    bitmap_shader = bitmap.pixel_shader
    bitmap_shader.make_transparent(0)
    sprite = displayio.TileGrid(
        bitmap,
        pixel_shader=bitmap_shader,
        width=1,
        height=1,
        tile_width=32,
        tile_height=32,
        x=0
    )

    sprite_group.append(sprite)

    current_frame = 0
    frame_count = int(bitmap.width / 32)
    frame_duration = DEFAULT_FRAME_DURATION


def advance_frame():
    """
    Advance to the next frame and loop back at the end
    """
    # pylint: disable=global-statement
    global current_frame
    current_frame = current_frame + 1
    if current_frame >= frame_count:
        current_frame = 0
    sprite_group[1][0] = current_frame

    if sprite_group[1].x < -32 or sprite_group[1].x > 64:
        sprite_group[1].flip_x = not sprite_group[1].flip_x
    direction = 1 if sprite_group[1].flip_x else -1

    sprite_group[1].x += direction

load_background()
load_image()

while True:
    button_down.update()
    button_up.update()
    if button_down.fell:
        sprite_group[1].flip_x = not sprite_group[1].flip_x
    advance_frame()
    time.sleep(frame_duration)
