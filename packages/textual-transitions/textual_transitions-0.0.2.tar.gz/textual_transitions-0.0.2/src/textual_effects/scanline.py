# scanline.py
import asyncio
import math

from textual.containers import Container
from textual.widgets import Label

from textual_effects.mixins import PaddingMixin

# =============================================================================
# Scanline
# =============================================================================

class Scanline(Container, PaddingMixin):
    """Draws a line from left to right until it hits the edge, then moves down
    a line and starts again. Once the screen is filled the `callback` function
    gets called, then the effect empties from top to bottom.

    :param owner: Widget being overlayed, used for sizing calculations
    :param thickness: Thickness of the line
    :param cursor_color: Color of the lead cursor that moves along. Defaults
        to "green"
    :param fill_color: Color of the fill line. Defaults to "black"
    :param seconds: How long the effect should take. Defaults to 1.
    :param pause: Delay between frames (if given, `seconds` is ignored)
    :param callback: Optional function to call at the midpoint of the effect
    :param post_callback: Optional function to call after finishing the effect
    :param pad_left: left padding on widget, useful if owner has a border you
        don't want covered by the effect
    :param pad_right: right padding on widget
    :param pad_top: top padding on widget
    :param pad_bottom: bottom padding on widget
    """
    def __init__(self, owner, thickness=1, cursor_color="green",
            fill_color="black", seconds=1, pause=None, callback=None,
            pad_left=0, pad_right=0, pad_top=0, pad_bottom=0):
        super().__init__()
        self.set_padding(owner, pad_left, pad_right, pad_top, pad_bottom)

        self.thickness = thickness
        self.cursor_color = cursor_color
        self.fill_color = fill_color
        self.callback = callback
        self.post_callback = post_callback

        if pause is not None:
            self.pause = pause
        else:
            frames = 2 * self.width * (self.height / thickness)
            self.pause = seconds / frames

    def compose(self):
        snake = Label("")
        snake.styles.position = "absolute"
        snake.styles.offset = (0, 0)
        snake.styles.width = 1
        snake.styles.height = self.thickness
        snake.styles.background = self.fill_color
        snake.styles.visibility = "visible"

        self.snake = snake
        yield snake

        head = Label("")
        head.styles.position = "absolute"
        head.styles.offset = (0, 0)
        head.styles.width = 1
        head.styles.height = self.thickness
        head.styles.background = self.cursor_color
        head.styles.visibility = "visible"

        self.head = head
        yield head

    async def run(self):
        top_fill = Label("")
        top_fill.styles.width = self.width
        top_fill.styles.height = self.thickness
        top_fill.styles.position = "absolute"
        top_fill.styles.offset = (0, 0)
        top_fill.styles.background = self.fill_color
        top_fill.styles.visibility = "visible"

        # Start eating from left to right
        fill_steps = math.ceil(self.height / self.thickness)

        for y in range(0, fill_steps):
            pos_y = y * self.thickness

            for line_width in range(1, self.width + 1):
                if line_width != self.width:
                    self.head.styles.offset = (line_width, pos_y)

                self.snake.styles.width = line_width
                await asyncio.sleep(self.pause)

            if y == 0:
                # Populate the top fill
                self.mount(top_fill)

            # Bump up top fill's size, then reset the snake
            top_fill.styles.height = (y + 1) * self.thickness

            self.snake.styles.width = 1
            snake_y = pos_y + self.thickness
            self.snake.styles.offset = (0, snake_y)
            self.head.styles.offset = (0, snake_y)

        await asyncio.sleep(0.5)

        if self.callback is not None:
            await self.callback()

        # Tail of the snake
        self.head.remove()

        self.snake.styles.width = self.width
        self.snake.styles.offset = (0, 0)

        for y in range(0, fill_steps):
            fill_y = self.height - ((y + 1) * self.thickness)
            if fill_y <= 0:
                top_fill.remove()
            else:
                top_fill.styles.height = fill_y
                top_fill.styles.offset = (0, (y + 1) * self.thickness)

            for line_width in range(self.width, 1, -1):
                x = self.width - line_width
                self.snake.styles.width = line_width
                self.snake.styles.offset = (x, y * self.thickness)

                await asyncio.sleep(self.pause)

        self.remove()

        if self.post_callback is not None:
            await self.post_callback()
