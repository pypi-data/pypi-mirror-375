Textual Effects
===============

Textual Effects is a transition effects library for textual TUI applications.
It provides a series of wipe-like transitions as overlays for content similar
to how PowerPoint or Keynote do slide transitions.

The current effects are:

* Blinds: mimics vertical blinds closing
* Curtain: a wipe that starts from the top and descends, then re-ascends
* Drapes: two wipes starting from the left and right
* Fire: simulates setting fire to the screen
* Iris: a centred rectangular block that grows in side until it fills the
  screen
* Matrix: Matrix-movie like green character lines
* Scanline: a right-to left line that transitions from top to bottom
* Water: a dripping water effect until the screen fills

.. image:: capture.gif

Each effect has an optional call-back mechanism that gets triggered in the
middle of the effect. This is typically used to replace the content that you
have overlayed so that when the transition is complete new content is present.

.. _installation:

Installation
============

.. code-block:: bash

    $ pip install textual-effects

.. _quickstart:

Quick Start
===========

The effects are installed as an overlay of an existing widget (typically a
Container) using the ``layers`` CSS directive. Consider the following
structure that you want to overlay:

.. code-block:: python

    def compose(self) -> ComposeResult:
        with Container(id="my_content"):
            yield Static("Stuff in my content")
            # and more widgets


To create an overlay, put your existing widget into a wrapping Container which
will also contains a sibling Container for the effect. The above code would be
replaced with:

.. code-block:: python

    def compose(self) -> ComposeResult:

        with Container(id="effect_holder") as self.effect_holder:
            self.overlay = Container(id="overlay")
            yeild self.overlay

            # Original contents
            with Container(id="my_content"):
                yield Static("Stuff in my content")
                # and more widgets

The original and effects Containers need to be on different layers, and the
overlay must be set to ``hidden``:

.. code-block:: CSS

    #effect_holder {
        layers: below above;
    }

    #overlay {
        layer: above;
        visibility: hidden;
    }

    #my_content {
        layer: below;
    }

To activate the effect, you instantiate a new effect class, mount it within
the overlay, then create a worker with the effect's ``.run()`` method:

.. code-block:: python

    from textual_effect import Curtain

    async def on_key(self, event):
        if event.key == 'c':
            curtain = Curtain(self.effect_holder)
            self.overlay.mount(curtain)
            self.run_worker(curtain.run(), exclusive=True)

All effects support call-back mechanisms, one or more ways of adjusting the
transition speed, and padding controls. Some effects also allow you to
determine the color of the wipe. For full information on each effect, see the
documentation.


Supports
========

This code is still pretty much alpha and doesn't have automated tests. Manual
testing was done in Python 3.13. There are no match/case blocks or walrus
operators, so it should work with earlier versions.

Docs & Source
=============

Docs: http://textual_effects.readthedocs.io/en/latest/

Source: https://github.com/cltrudeau/textual-effects
