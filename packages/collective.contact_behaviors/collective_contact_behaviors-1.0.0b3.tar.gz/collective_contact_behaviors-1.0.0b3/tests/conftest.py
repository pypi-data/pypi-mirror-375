from collective.contact_behaviors.testing import FUNCTIONAL_TESTING
from collective.contact_behaviors.testing import INTEGRATION_TESTING
from plone import api
from pytest_plone import fixtures_factory

import pytest


pytest_plugins = ["pytest_plone"]


globals().update(
    fixtures_factory((
        (FUNCTIONAL_TESTING, "functional"),
        (INTEGRATION_TESTING, "integration"),
    ))
)


@pytest.fixture
def contents_payload() -> list:
    """Payload to create two content items."""
    return [
        {
            "type": "Content",
            "id": "content-1",
            "title": "Content 1",
            "description": "A Plone Content",
            "address": "Riesstraße 21",
            "address_2": "",
            "city": "Bonn",
            "state": "NW",
            "postal_code": "53113",
            "country": "DE",
            "contact_email": "foo@bar.de",
            "contact_website": "https://plone.org",
            "contact_phone": "+4917637752521",
        },
        {
            "type": "Content",
            "id": "content-2",
            "title": "Content 2",
            "description": "Another Plone Content",
            "address": "Maison Olympique",
            "address_2": "",
            "city": "Lausanne",
            "state": "",
            "postal_code": "1007",
            "country": "CH",
            "contact_email": "foo@bar.ch",
            "contact_website": "https://plone.org/ch",
            "contact_phone": "+41 765-5556-40",
        },
    ]


@pytest.fixture
def contents(portal, contents_payload) -> dict:
    """Create provider content items."""
    response = {}
    with api.env.adopt_roles([
        "Manager",
    ]):
        for data in contents_payload:
            content = api.content.create(container=portal, **data)
            response[content.UID()] = content.title
    return response


@pytest.fixture
def content(contents) -> dict:
    """Return one content item."""
    content_uid = next(iter(contents))
    brains = api.content.find(UID=content_uid)
    return brains[0].getObject()
