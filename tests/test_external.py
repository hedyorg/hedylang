import unittest

from hedy.external import (
    get_frontend_feature_flags_context,
    initialize_frontend_feature_flags,
    initialize_frontend_feature_flags_from_context,
    is_feature_enabled,
)


class TestExternalFeatureFlags(unittest.TestCase):
    def setUp(self):
        self.previous_context = get_frontend_feature_flags_context()

    def tearDown(self):
        initialize_frontend_feature_flags_from_context(self.previous_context)

    def test_is_feature_enabled_uses_environment_mapping(self):
        initialize_frontend_feature_flags(
            frontend_environment='production',
            feature_flags={
                'answer_interpolation': {
                    'production': False,
                    'local': True,
                }
            },
        )

        self.assertFalse(is_feature_enabled('answer_interpolation', default=True))

    def test_is_feature_enabled_returns_default_for_missing_feature(self):
        initialize_frontend_feature_flags(frontend_environment='local', feature_flags={})

        self.assertTrue(is_feature_enabled('missing_feature', default=True))
        self.assertFalse(is_feature_enabled('missing_feature', default=False))

    def test_context_initializer_handles_non_dict_context(self):
        initialize_frontend_feature_flags_from_context(None)

        self.assertTrue(is_feature_enabled('answer_interpolation', default=True))
