# mixins.py

# =============================================================================

class PaddingMixin:
    def set_padding(self, owner, pad_left, pad_right, pad_top, pad_bottom):
        """This is a constructor helper that deals with the size of the
        container holding the effect. It takes the associated `owner` widget
        that the effect will overlay and any padding values.

        The owner and padding values are stored, then used to reposition and
        size the container that this is mixed into. It also sets `width` and
        `height` attributes as shortcut helpers.

        :param owner: widget being overlayed, used for sizing calculations
        :param pad_left: left padding on widget, useful if owner has a border
            you don't want covered by the effect
        :param pad_right: right padding on widget
        :param pad_top: top padding on widget
        :param pad_bottom: bottom padding on widget
        """
        self.owner = owner
        self.pad_left = pad_left
        self.pad_right = pad_right
        self.pad_top = pad_top
        self.pad_bottom = pad_bottom

        self.styles.offset = (self.pad_left, self.pad_top)
        self.styles.height = (self.owner.size.height - self.pad_top -
            self.pad_bottom)
        self.styles.width = (self.owner.size.width - self.pad_left -
            self.pad_right)

        self.height = int(self.styles.height.value)
        self.width = int(self.styles.width.value)
