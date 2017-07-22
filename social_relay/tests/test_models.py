from unittest.mock import patch, Mock

from social_relay.models import Profile


class TestProfile:
    def test_get_public_key(self, profile):
        assert Profile.get_public_key(profile.identifier) == profile.public_key

    @patch("social_relay.models.retrieve_remote_profile", return_value=None)
    def test_get_profile(self, mock_retrieve, profile):
        # Local
        assert Profile.get_profile(profile.identifier) == profile

        # Not existing
        assert not Profile.get_profile("foobar")
        mock_retrieve.assert_called_once_with("foobar")

    def test_from_remote_profile(self, profile):
        # New
        new_profile = Profile.from_remote_profile(Mock(
            handle="identifier", public_key="public_key",
        ))
        assert new_profile.identifier == "identifier"
        assert new_profile.public_key == "public_key"

        # Existing
        Profile.from_remote_profile(Mock(
            handle=profile.identifier, public_key="new public key",
        ))
        profile = Profile.get(Profile.identifier == profile.identifier)
        assert profile.public_key == "new public key"
