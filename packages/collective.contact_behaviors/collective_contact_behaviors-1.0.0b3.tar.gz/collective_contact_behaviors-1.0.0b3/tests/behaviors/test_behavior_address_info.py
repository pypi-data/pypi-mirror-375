from collective.contact_behaviors.behaviors.address_info import IAddressInfo
from plone import api

import pytest


BEHAVIOR = "collective.contact_behaviors.address_info"


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
        assert IAddressInfo.providedBy(content)

    def test_indexer_country(self):
        """Test country indexer."""
        new_country = "BR"
        content = self.content
        content.country = new_country
        content.reindexObject(
            idxs=[
                "country",
            ]
        )
        # Search for country
        brains = api.content.find(country=new_country)
        assert len(brains) == 1
        assert brains[0].country == new_country
