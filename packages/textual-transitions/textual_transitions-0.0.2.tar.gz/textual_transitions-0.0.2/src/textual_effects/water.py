# water.py
import asyncio

from textual.containers import Container
from textual.widgets import Label

from textual_effects.mixins import PaddingMixin

# =============================================================================
# Water
# =============================================================================

class Water(Container, PaddingMixin):
    """Starts with a series of drops of water, then turns into a flow from the
    top center of the effect, water then fills up from the bottom.  Once the
    area is flooded, your callback function is called, then the area drains.

    :param owner: Widget being overlayed, used for sizing calculations
    :param drip_time: How long the dripping phase of the effect should take,
        this includes the tap flow that follows the drip. Defaults to 2 seconds.
    :param flood_time: How long the flood and drain portion of the effect
        should take. Defaults to 1 second.
    :param color: Color of the curtain. Defaults to "#00A5F4", which is the
        colour of the bottom of the default drop character on a macOS
    :param drop_char: Character to use as the drop image. Defaults to the drop
        emoji, (U+1F4A7). Note that the background color of the drop is set to
        None so a space won't show up, use a block instead.
    :param drop_sets: Before the screen starts to flood a series of increasing
        drops is shown (1, 2, 3...) as sets. This number determines how many
        sets to show before starting the fill.  Defaults to 3 sets.
    :param callback: Optional function to call at the midpoint of the effect
    :param post_callback: Optional function to call after finishing the effect
    :param pad_left: left padding on widget, useful if owner has a border you
        don't want covered by the effect
    :param pad_right: right padding on widget
    :param pad_top: top padding on widget
    :param pad_bottom: bottom padding on widget
    """
    def __init__(self, owner, drip_time=2, flood_time=1, color="#00A5F4",
            drop_char="💧", drop_sets=3, callback=None, pad_left=0,
            pad_right=0, pad_top=0, pad_bottom=0):
        super().__init__()
        self.set_padding(owner, pad_left, pad_right, pad_top, pad_bottom)

        self.color = color
        self.drop_char = drop_char
        self.drop_sets = drop_sets
        self.callback = callback
        self.post_callback = post_callback

        # Calculate pauses; each set of drops has to travel the height, then a
        # bit extra for the tap
        frames = self.height * (drop_sets + 1)

        # Frame drawing takes some time, trial an error shows about doubling
        # the frame rate seems to get things to be a reasonable stage
        self.drip_pause = drip_time / (2 * frames)

        # Timing for the flood and draining (far less complicated)
        self.flood_pause = flood_time / (2 * self.height)

    def _make_drop(self, x, start):
        drop = Label(self.drop_char)
        drop.styles.position = "absolute"
        drop.styles.offset = (x, start)
        drop.styles.background = None
        drop.styles.visibility = "visible"
        return drop

    async def _animate_drop_set(self, drop_set_size, x):
        drops = []
        start = 0
        next_drop = 0
        start_tap = (self.height // drop_set_size)
        for drop_set_count in range(1, drop_set_size + 1):
            for n in range(drop_set_count):
                drop = self._make_drop(x, start)
                drops.append(drop)
                next_drop += self.height // drop_set_count
                start = 0 - next_drop

        # Animate the dripping of the drop_set
        dripping = len(drops)
        while dripping > 0:
            for i, drop in enumerate(drops):
                y = drop.styles.offset.y.value
                if y == 0:
                    # First time it appears
                    self.mount(drop)

                await asyncio.sleep(self.drip_pause)
                y += 1
                drop.styles.offset = (x, y)

                if y == self.height:
                    drop.remove()
                    dripping -= 1

                # Start the tap
                if self.tap is None and \
                        drops[-1].styles.offset.y.value >= (start_tap - 1):
                    tap = Label(" ")
                    tap.styles.position = "absolute"
                    tap.styles.offset = (x, 0)
                    tap.styles.background = self.color
                    tap.styles.width = 1
                    tap.styles.height = 1
                    tap.styles.visibility = "visible"

                    self.tap = tap
                    self.mount(self.tap)

            if self.tap is not None:
                # Lengthen the size of the flow
                self.tap.styles.height = self.tap.styles.height.value + 1

    async def run(self):
        centre = self.width // 2

        # Create the set of drops
        self.tap = None
        await self._animate_drop_set(self.drop_sets, centre)

        # Finish flow of tap
        for tap_size in range(int(self.tap.styles.height.value), self.height):
            self.tap.styles.height = self.tap.styles.height.value + 1
            await asyncio.sleep(self.drip_pause)

        # Flood the base
        flood = Label("")
        flood.styles.position = "absolute"
        flood.styles.offset = (0, self.height)
        flood.styles.background = self.color
        flood.styles.width = self.width
        flood.styles.height = 1
        flood.styles.visibility = "visible"
        self.mount(flood)

        for h in range(1, self.height + 1):
            flood.styles.height = h
            flood.styles.offset = (0, self.height - h)
            await asyncio.sleep(self.flood_pause)

        # Get ready to drain
        self.tap.remove()
        if self.callback is not None:
            await self.callback()

        # Drain
        for h in range(self.height, 0, -1):
            flood.styles.height = h
            flood.styles.offset = (0, self.height - h)
            await asyncio.sleep(self.flood_pause)

        self.remove()

        if self.post_callback is not None:
            await self.post_callback()
