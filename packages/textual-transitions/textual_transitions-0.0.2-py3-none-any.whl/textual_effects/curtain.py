# curtain.py
import asyncio

from textual.containers import Container
from textual.widgets import Label

from textual_effects.mixins import PaddingMixin

# =============================================================================
# Curtain
# =============================================================================

class Curtain(Container, PaddingMixin):
    """Drops a curtain from the top, calls your callback function, then
    raises the curtain again.

    :param owner: widget being overlayed, used for sizing calculations
    :param seconds: How long the effect should take. Defaults to 1.
    :param pause: Delay between frames (if given, `seconds` is ignored)
    :param color: Color of the curtain. Defaults to "black"
    :param callback: Optional function to call at the midpoint of the effect
    :param post_callback: Optional function to call after finishing the effect
    :param pad_left: left padding on widget, useful if owner has a border
        you don't want covered by the effect
    :param pad_right: right padding on widget
    :param pad_top: top padding on widget
    :param pad_bottom: bottom padding on widget
    """
    def __init__(self, owner, seconds=1, pause=None, color="black",
            callback=None, post_callback=None, pad_left=0, pad_right=0,
            pad_top=0, pad_bottom=0):
        super().__init__()
        self.set_padding(owner, pad_left, pad_right, pad_top, pad_bottom)

        self.color = color
        self.callback = callback
        self.post_callback = post_callback

        if pause is not None:
            self.pause = pause
        else:
            self.pause = seconds / self.height

    def compose(self):
        self.label = Label("")
        yield self.label

    async def run(self):
        curtain = self.label
        curtain.styles.position = "absolute"
        curtain.styles.offset = (0, 0)
        curtain.styles.height = 1
        curtain.styles.width = self.styles.width
        curtain.styles.background = self.color

        curtain.styles.visibility = "visible"

        height = int(self.styles.height.value)

        # Drop curtain
        for count in range(1, height + 1):
            curtain.styles.height = count
            await asyncio.sleep(self.pause)

        if self.callback is not None:
            await self.callback()

        # Raise curtain
        for count in range(height, 0, -1):
            curtain.styles.height = count
            await asyncio.sleep(self.pause)

        curtain.styles.visibility = "hidden"
        self.remove()

        if self.post_callback is not None:
            await self.post_callback()
