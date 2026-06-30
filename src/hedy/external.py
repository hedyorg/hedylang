"""Functions that can be configured by the user of this library, such as the gettext function for translation."""

import copy

THE_GETTEXT = lambda x: x
THE_FRONTEND_ENVIRONMENT = 'local'
THE_FEATURE_FLAGS = {}

def initialize_gettext(gettext_fn):
    """Initialize the gettext function used for translation in this module."""
    global THE_GETTEXT
    THE_GETTEXT = gettext_fn


def gettext(s):
    """Default gettext function that just returns the input string."""
    return THE_GETTEXT(s)


def initialize_frontend_feature_flags(frontend_environment=None, feature_flags=None):
    """Initialize frontend feature-flag settings provided by the parent application.

    Expected format matches the Hedy parent project context processor:
    {
        "frontend_environment": "local",
        "feature_flags": {
            "answer_interpolation": {
                "production": False,
                "local": True,
                "alpha": True,
            }
        },
    }
    """
    global THE_FRONTEND_ENVIRONMENT
    global THE_FEATURE_FLAGS

    if frontend_environment is not None:
        THE_FRONTEND_ENVIRONMENT = frontend_environment
    if feature_flags is not None:
        THE_FEATURE_FLAGS = feature_flags


def initialize_frontend_feature_flags_from_context(context):
    """Initialize feature flags from a context object with environment and flags."""
    initialize_frontend_feature_flags(
        frontend_environment=context.get('frontend_environment'),
        feature_flags=context.get('feature_flags'),
    )


def get_frontend_feature_flags_context():
    """Return the current feature-flag context for save/restore in tests or integrations."""
    return {
        'frontend_environment': THE_FRONTEND_ENVIRONMENT,
        'feature_flags': copy.deepcopy(THE_FEATURE_FLAGS),
    }


def is_feature_enabled(feature_name, default=True):
    """Resolve a feature flag against the configured frontend environment."""
    feature_config = THE_FEATURE_FLAGS.get(feature_name)
    if feature_config is None:
        return default

    if isinstance(feature_config, dict):
        if THE_FRONTEND_ENVIRONMENT in feature_config:
            return bool(feature_config[THE_FRONTEND_ENVIRONMENT])
        return default

    return bool(feature_config)
