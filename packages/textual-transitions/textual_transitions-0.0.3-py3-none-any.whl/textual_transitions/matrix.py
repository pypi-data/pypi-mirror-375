# matrix.py
import asyncio
from dataclasses import dataclass
from random import randint

from textual.containers import Container
from textual.widgets import Static

from textual_transitions.mixins import PaddingMixin

# =============================================================================
# Matrix
# =============================================================================

@dataclass
class MatrixTrail:
    length: int
    gap: int
    current: int = 0

    styles = [
        "[lime bold]",
        "[lime]",
        "[limegreen bold]",
        "[limegreen]",
        "[green]",
    ]

    def get_content(self, height, complete):
        if self.gap > 0:
            # Trail is between sets of chars, reduce gap count
            self.gap -= 1
            return " "

        # We're in a char set, move to the next one
        self.current += 1

        if self.current > self.length:
            # End of self, reset it
            self.current = 0
            max_trail_height = max(height // 3, 4)
            self.length = randint(3, max_trail_height)

            if complete:
                # Done creating new sets, make sure nothing but blanks from
                # here on
                self.gap = height * 2
            else:
                self.gap = randint(3, 7)
            return " "

        # else, Print a character for this char set
        letter = randint(32, 126)
        if 91 <= letter <= 93:
            # Markup's special characters ([, / ]), can't use them
            letter += 4

        index = -1 if self.current >= len(MatrixTrail.styles) \
            else self.current - 1
        return f"{self.styles[index]}{chr(letter)}[/]"


class Matrix(Container, PaddingMixin):
    """Drops Matrix style green text lines from the top to fill the screen,
    calls your callback function, then the effect drops off the screen.

    :param owner: widget being overlayed, used for sizing calculations
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
    def __init__(self, owner, seconds=1, pause=None, callback=None,
            pad_left=0, pad_right=0, pad_top=0, pad_bottom=0):
        super().__init__()
        self.set_padding(owner, pad_left, pad_right, pad_top, pad_bottom)

        self.callback = callback
        self.post_callback = post_callback

        if pause is not None:
            self.pause = pause
        else:
            # There are two screen fulls, plus another third or so of trails
            # to run down
            self.pause = seconds / (2.3 * self.height)

    async def run(self):
        line = Static("")
        line.styles.width = "100%"
        line.styles.position = "absolute"
        line.styles.offset = (0, 0)
        line.styles.background = "black 0%"
        line.styles.visibility = "visible"

        trails = []
        space = randint(2, 5)
        for x in range(self.width):
            letter = randint(32, 126)
            if 91 <= letter <= 93:
                # Markup's special characters, can't use them
                letter += 4

            # Start with random spacing between the beginning of columns
            space -= 1
            max_trail_height = max(self.height // 3, 4)
            trail_length = randint(3, max_trail_height)

            if space == 0:
                space = randint(2, 5)
                trail = MatrixTrail(length=trail_length, gap = 0)
            else:
                trail = MatrixTrail(length=trail_length, gap=randint(1, 7))

            trails.append(trail)

        contents = []
        for count in range(self.height):
            # Generate a new line
            output = ""
            for trail in trails:
                output += trail.get_content(self.height, False)

            contents.insert(0, output)
            line.update("\n".join(contents))
            if count == 0:
                self.mount(line)

            await asyncio.sleep(self.pause)

        # Stop generating new char sets
        longest = max([t.length - t.current for t in trails])

        # Loop longest trail length past the terminal height so everything
        # gets pushed down
        for count in range(self.height + longest):
            contents = contents[0:-1]

            # Generate a new line
            output = ""
            for trail in trails:
                output += trail.get_content(self.height, True)

            contents.insert(0, output)
            line.update("\n".join(contents))

            await asyncio.sleep(self.pause)

        # Call back before cleaning up
        if self.callback:
            await self.callback()

        self.remove()

        if self.post_callback is not None:
            await self.post_callback()
