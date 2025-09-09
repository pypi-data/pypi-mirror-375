# fire.py
import asyncio
from random import randint, random
from statistics import mean

from textual.containers import Container
from textual.widgets import Label

from textual_transitions.mixins import PaddingMixin

# =============================================================================
# Fire
# =============================================================================

class Fire(Container, PaddingMixin):
    ### Fire effects adapted from Asciimatics:
    #
    # https://github.com/peterbrittain/asciimatics
    #
    # Who adapted it from Hugo Elias:
    #
    # https://web.archive.org/web/20160418004150/http://freespace.virgin.net/hugo.elias/models/m_fire.htm
    #
    # Basic concept: a list-of-lists is used as a buffer with pixel intensity
    # values. Fire animation randomly cools some of the spots as well as
    # convects the pixels upwards. After random cooling, a smoothing function is
    # run average the heat value of each pixel based on the four around it.
    #
    # To start, the fire is a single line at the bottom of the screen made up of
    # a random number of pixels based on `.intensity`. Each time convection
    # happens a new row is inserted and the top-most one is cycled out.
    #
    # The Label isn't based on the whole buffer, any empty lines at the top
    # aren't included to keep transparency happening until the burn has consumed
    # the whole screen.
    """
    Simulates fire burning on the screen. Starts as a series of single pixel
    emitters which then "grow" the flame.

    :param owner: widget being overlayed, used for sizing calculations
    :param pause: Amount of time to wait between frames, defaults to 0.05
        seconds
    :param callback: Optional function to call at the midpoint of the effect
    :param post_callback: Optional function to call after finishing the effect
    :param pad_left: left padding on widget, useful if owner has a border
        you don't want covered by the effect
    :param pad_right: right padding on widget
    :param pad_top: top padding on widget
    :param pad_bottom: bottom padding on widget
    :param spot: how hot the emitter values are, effects flame growth,
        defaults to 60
    :param intensity: random percentage for a new emitter, defaults to 0.80
    :param frames_after_consumption: how long after filling the screen should
        the fire continue. Defaults to 20 frames
    :param percentage_cooling_spots: percentage of pixels to cool off, allows
        for flow effect of the flame. Defaults to 0.02

    """

    DEFAULT_CSS = """
        Fire {
            background: black 0%;
        }
    """

    COLOURS = [
        "#000000",
        "#5F0000",
        "#870000",
        "#AF0000",
        "#D70000",
        "#FF0000",
        "#FF5F00",
        "#FF8700",
        "#FFAF00",
        "#FFD700",
        "#FFFF00",
        "#FFFF5F",
        "#FFFF87",
        "#FFFFAF",
        "#FFFFD7",
        "#FFFFFF",
    ]

    def __init__(self, owner, pause=0.05, callback=None, pad_left=0,
            pad_right=0, pad_top=0, pad_bottom=0, spot=60, intensity=0.8,
            frames_after_consumption=20, percentage_cooling_spots=0.02):
        super().__init__()
        self.set_padding(owner, pad_left, pad_right, pad_top, pad_bottom)

        self.callback = callback
        self.post_callback = post_callback

        self.pause = pause
        self.spot = spot
        self.intensity = intensity
        self.frames_after_consumption = frames_after_consumption
        self.percentage_cooling_spots = percentage_cooling_spots

    def convert_pixels(self, max_height=1):
        # Converts the internal list-of-lists buffer with the heat values into
        # a string that can be used by a Label
        content = ""

        content = ""
        for count, pixels in enumerate(self.pixel_lines):
            fire_height = count + 1
            line = ""
            for pixel in pixels:
                index = min(len(self.COLOURS) - 1, pixel)
                if index < 0:
                    index = 0

                line += f"[on {self.COLOURS[index]}] [/]"

            if count == 0:
                content = line
            else:
                content = line + "\n" + content

            if fire_height >= max_height:
                # We've hit the maximum allowed height, stop generating text
                break

        return content

    def emitter_line(self, width, extinguish=0):
        # Generate a new line of heat values
        line = []
        for _ in range(width):
            if random() < self.intensity - extinguish:
                line.append(randint(1, self.spot))
            else:
                line.append(0)

        return line

    async def animate_fire(self, duration, growth=True, extinguish=0):
        for frame in range(duration):
            # Convection pushes everything up, sticking a new emitter at the
            # bottom (pixel array is upside down)
            self.pixel_lines.insert(0, self.emitter_line(self.width,
                frame * extinguish))
            del self.pixel_lines[-1]

            # Seed some random cooling spots
            num_spots = (frame * self.width * self.percentage_cooling_spots)
            for _ in range(int(num_spots)):
                row = randint(0, self.height - 1)
                col = randint(0, self.width - 1)
                self.pixel_lines[row][col] -= 10

            # Simulate cooling by averaging surrounding pixels
            for row in range(self.height):
                for col in range(self.width):
                    values = []
                    # To the right
                    if col + 1 < self.width:
                        values.append(self.pixel_lines[row][col + 1])
                    # To the left
                    if col - 1 > 0:
                        values.append(self.pixel_lines[row][col - 1])
                    # Above
                    if row + 1 < self.height:
                        values.append(self.pixel_lines[row + 1][col])
                    # Below
                    if row - 1 > 0:
                        values.append(self.pixel_lines[row - 1][col])

                    # Average the values
                    self.pixel_lines[row][col] = int(mean(values))

            max_height = self.height
            if growth:
                max_height = min(self.height, frame)

            content = self.convert_pixels(max_height)
            self.label.update(content)

            # Re-adjust the positioning based on the new label size
            down = self.height - self.label.size.height
            self.label.styles.offset = (0, down)

            await asyncio.sleep(self.pause)

    async def run(self):
        label = Label("")
        label.styles.width = self.width
        label.styles.position = "absolute"
        label.styles.offset = (0, self.height)
        label.styles.visibility = "visible"

        self.label = label

        # Create a pixel buffer the size of the screen with zero values, then
        # stick an emitter line at the bottom of it
        self.pixel_lines = [
            [0 for _ in range(self.width)] for _ in range(self.height - 1)
        ]
        self.pixel_lines.insert(0, self.emitter_line(self.width))

        # Generate the display text and show the label
        content = self.convert_pixels()
        self.label.update(content)
        self.mount(self.label)

        await self.animate_fire(self.height)
        await self.animate_fire(self.frames_after_consumption, False, 0.08)

        # Trigger callback before going away
        if self.callback is not None:
            await self.callback()

        self.remove()

        if self.post_callback is not None:
            await self.post_callback()
