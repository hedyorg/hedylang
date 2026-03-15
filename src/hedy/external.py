"""Functions that can be configured by the user of this library, such as the gettext function for translation."""

THE_GETTEXT = lambda x: x

def initialize_gettext(gettext_fn):
    """Initialize the gettext function used for translation in this module."""
    global THE_GETTEXT
    THE_GETTEXT = gettext_fn


def gettext(s):
    """Default gettext function that just returns the input string."""
    return THE_GETTEXT(s)