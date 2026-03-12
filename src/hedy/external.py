"""Functions that can be configured by the user of this library, such as the gettext function for translation."""

def initialize_gettext(gettext_fn):
    """Initialize the gettext function used for translation in this module."""
    global gettext
    gettext = gettext_fn


def gettext(s):
    """Default gettext function that just returns the input string."""
    return s