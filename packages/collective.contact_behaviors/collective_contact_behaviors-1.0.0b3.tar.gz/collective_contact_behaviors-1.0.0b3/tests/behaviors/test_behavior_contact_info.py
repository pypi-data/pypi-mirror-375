from collective.contact_behaviors.behaviors.contact_info import IContactInfo
from plone import api

import pytest


BEHAVIOR = "collective.contact_behaviors.contact_info"


class TestAddressInfoBehavior:
    @pytest.fixture(autouse=True)
    def _init(self, portal, content):
        self.portal = portal
        self.content = content

    def test_behavior_enabled(self, get_behaviors):
        """Test if behavior is installed for Content."""
        assert BEHAVIOR in get_behaviors("Content")

    def test_behavior_is_provided(self):
        """Test if behavior is provided by a Content instance."""
        content = self.content
        assert IContactInfo.providedBy(content)

    def test_indexer_contact_email(self):
        """Test contact_email indexer."""
        new_email = "site@plone.org"
        content = self.content
        content.contact_email = new_email
        content.reindexObject(
            idxs=[
                "contact_email",
            ]
        )
        # Search for contact_email
        brains = api.content.find(contact_email=new_email)
        assert len(brains) == 1
        # contact_email is not in the metadata
        obj = brains[0].getObject()
        assert obj.contact_email == new_email
