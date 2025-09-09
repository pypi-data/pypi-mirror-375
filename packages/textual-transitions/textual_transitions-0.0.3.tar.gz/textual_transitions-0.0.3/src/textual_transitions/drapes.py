# drapes.py
import asyncio

from textual.containers import Container
from textual.widgets import Label

from textual_transitions.mixins import PaddingMixin

# =============================================================================
# Drapes
# =============================================================================

class Drapes(Container, PaddingMixin):
    """Has a left and right drape which close from the sides, calls your
    callback function, then opens the drapes again.

    :param owner: widget being overlayed, used for sizing calculations
    :param seconds: How long the effect should take. Defaults to 1.
    :param pause: Delay between frames (if given, `seconds` is ignored)
    :param color: Color of the drapes. Defaults to "black"
    :param callback: Optional function to call at the midpoint of the effect
    :param post_callback: Optional function to call after finishing the effect
    :param pad_left: left padding on widget, useful if owner has a border you
        don't want covered by the effect
    :param pad_right: right padding on widget
    :param pad_top: top padding on widget
    :param pad_bottom: bottom padding on widget
    """
    def __init__(self, owner, seconds=1, pause=None, color="black",
            callback=None, pad_left=0, pad_right=0, pad_top=0, pad_bottom=0):
        super().__init__()
        self.set_padding(owner, pad_left, pad_right, pad_top, pad_bottom)

        self.color = color
        self.callback = callback
        self.post_callback = post_callback

        if pause is not None:
            self.pause = pause
        else:
            # Close and re-open is 2*width of frames
            self.pause = seconds / (2 * self.width)

    def compose(self):
        self.left_drape = Label("")
        self.right_drape = Label("")
        yield self.left_drape
        yield self.right_drape

    async def run(self):
        centre = self.width // 2

        left = self.left_drape
        left.styles.position = "absolute"
        left.styles.offset = (0, 0)
        left.styles.height = self.height
        left.styles.width = 1
        left.styles.background = self.color
        left.styles.visibility = "visible"

        right = self.right_drape
        right.styles.position = "absolute"
        right.styles.offset = (self.width - 1, 0)
        right.styles.height = self.height
        right.styles.width = 1
        right.styles.background = self.color
        right.styles.visibility = "visible"

        # Close drapes
        while left.styles.width.value <= centre + 1:
            left.styles.width = left.styles.width.value + 1
            right.styles.width = right.styles.width.value + 1
            right.styles.offset = (self.width - right.styles.width.value, 0)
            await asyncio.sleep(self.pause)

        if self.callback is not None:
            await self.callback()

        # Open Drapes
        while left.styles.width.value >= 1:
            left.styles.width = left.styles.width.value - 1
            right.styles.width = right.styles.width.value - 1
            right.styles.offset = (self.width - right.styles.width.value, 0)
            await asyncio.sleep(self.pause)

        left.styles.visibility = "hidden"
        right.styles.visibility = "hidden"
        self.remove()

        if self.post_callback is not None:
            await self.post_callback()
