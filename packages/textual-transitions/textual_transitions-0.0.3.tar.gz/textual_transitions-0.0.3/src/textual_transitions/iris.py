# iris.py
import asyncio

from textual.containers import CenterMiddle
from textual.widgets import Label

from textual_transitions.mixins import PaddingMixin

# =============================================================================
# Iris
# =============================================================================

class Iris(CenterMiddle, PaddingMixin):
    """Starts with a centred block which expands out, then calls your callback
    function, then shrinks the block again.

    Has a left and right drape which close from the sides, calls your callback
    function, then opens the drapes again.

    :param owner: Widget being overlayed, used for sizing calculations
    :param seconds: How long the effect should take. Defaults to 1.
    :param pause: Delay between frames (if given, `seconds` is ignored)
    :param color: Color of the iris. Defaults to "black"
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

        # Growing width at twice the rate of height because terminal
        # characters aren't square; adding one to deal with round down
        # problems
        self.max_size = max(self.width // 2, self.height) + 1

        if pause is not None:
            self.pause = pause
        else:
            self.pause = seconds / (2 * self.max_size)

    def compose(self):
        iris = Label("")
        iris.styles.width = 1
        iris.styles.height = 1
        iris.styles.background = self.color
        iris.styles.visibility = "visible"

        self.iris = iris
        yield iris

    async def run(self):
        # Open iris
        for size in range(self.max_size):
            if size <= self.height:
                self.iris.styles.height = size

            if size * 2 <= self.width:
                self.iris.styles.width = size * 2
            elif (size * 2) - 1 == self.width:
                # Need to deal with off by one problem for odd widths
                self.iris.styles.width = (size * 2) + 1

            await asyncio.sleep(self.pause)

        if self.callback is not None:
            await self.callback()

        # Close iris
        for size in range(self.max_size, 1, -1):
            self.iris.styles.height = self.iris.styles.height.value - 1
            self.iris.styles.width = self.iris.styles.width.value - 2

            await asyncio.sleep(self.pause)

        self.remove()

        if self.post_callback is not None:
            await self.post_callback()
