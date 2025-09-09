# blinds.py
import asyncio
import math

from textual.containers import Container
from textual.widgets import Label

from textual_transitions.mixins import PaddingMixin

# =============================================================================
# Blinds
# =============================================================================

class Blinds(Container, PaddingMixin):
    """Displays `num_blinds` vertical blinds, closes them, calls your
    callback function, then opens them again.

    :param owner: Widget being overlayed, used for sizing calculations
    :param num_blinds: Number of blinds on the screen
    :param seconds: How long the effect should take. Defaults to 1.
    :param pause: Delay between frames (if given, `seconds` is ignored)
    :param color: Color of the blinds. Defaults to "black"
    :param callback: Optional function to call at the midpoint of the effect
    :param post_callback: Optional function to call after finishing the effect
    :param pad_left: left padding on widget, useful if owner has a border
        you don't want covered by the effect
    :param pad_right: right padding on widget
    :param pad_top: top padding on widget
    :param pad_bottom: bottom padding on widget
    """
    def __init__(self, owner, num_blinds=3, seconds=1, pause=None,
            color="black", callback=None, pad_left=0, pad_right=0, pad_top=0,
            pad_bottom=0):
        super().__init__()
        self.set_padding(owner, pad_left, pad_right, pad_top, pad_bottom)

        self.num_blinds = num_blinds
        self.color = color
        self.callback = callback
        self.post_callback = post_callback

        self.max_blind_height = math.ceil(self.height / self.num_blinds)

        if pause is not None:
            self.pause = pause
        else:
            self.pause = seconds / (2 * self.max_blind_height)

    def compose(self):
        self.blinds = []

        for count in range(self.num_blinds):
            y = count * self.max_blind_height

            blind = Label("")
            blind.styles.position = "absolute"
            blind.styles.offset = (0, y)
            blind.styles.height = 1
            blind.styles.width = self.width
            blind.styles.background = self.color
            blind.styles.visibility = "visible"
            self.blinds.append(blind)

            yield blind

    async def run(self):
        # Close blinds
        for h in range(self.max_blind_height):
            for blind in self.blinds:
                blind.styles.height = h

            await asyncio.sleep(self.pause)

        if self.callback is not None:
            await self.callback()

        # Open blinds
        for h in range(self.max_blind_height, 1, -1):
            for blind in self.blinds:
                blind.styles.height = h

            await asyncio.sleep(self.pause)

        self.remove()

        if self.post_callback is not None:
            await self.post_callback()
