"""External configuration hooks exposed by hedylang integrations."""

from __future__ import annotations

from copy import deepcopy


FRONTEND_ENVIRONMENT = None
FEATURE_FLAGS = {}

THE_GETTEXT = lambda x: x

def initialize_gettext(gettext_fn):
    """Initialize the gettext function used for translation in this module."""
    global THE_GETTEXT
    THE_GETTEXT = gettext_fn


def gettext(s):
    """Default gettext function that just returns the input string."""
    return THE_GETTEXT(s)


def initialize_frontend_feature_flags(frontend_environment=None, feature_flags=None):
    """Initialize frontend environment and feature flags for this process."""
    global FRONTEND_ENVIRONMENT, FEATURE_FLAGS
    FRONTEND_ENVIRONMENT = frontend_environment
    FEATURE_FLAGS = feature_flags if isinstance(feature_flags, dict) else {}


def initialize_frontend_feature_flags_from_context(context):
    """Initialize feature flags from a context dict provided by the parent project."""
    context = context if isinstance(context, dict) else {}
    initialize_frontend_feature_flags(
        frontend_environment=context.get('frontend_environment'),
        feature_flags=context.get('feature_flags'),
    )


def get_frontend_feature_flags_context():
    """Return current frontend environment and feature flags context."""
    return {
        'frontend_environment': FRONTEND_ENVIRONMENT,
        'feature_flags': deepcopy(FEATURE_FLAGS),
    }


def is_feature_enabled(feature_name, default=True):
    """Check if a feature is enabled for the current frontend environment."""
    feature_definition = FEATURE_FLAGS.get(feature_name)

    if feature_definition is None:
        return default

    if isinstance(feature_definition, bool):
        return feature_definition

    if isinstance(feature_definition, dict):
        if FRONTEND_ENVIRONMENT is None:
            return default
        return feature_definition.get(FRONTEND_ENVIRONMENT, default)

    return default
