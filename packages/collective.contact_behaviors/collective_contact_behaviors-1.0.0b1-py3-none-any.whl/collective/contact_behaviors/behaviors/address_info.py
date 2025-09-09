from collective.contact_behaviors import _
from plone import api
from plone.autoform.directives import read_permission
from plone.autoform.interfaces import IFormFieldProvider
from plone.supermodel import directives
from plone.supermodel import model
from zope import schema
from zope.interface import provider
from zope.schema.interfaces import IContextAwareDefaultFactory


PERMISSION = "collective.contact_behaviors.address_info.view"
PERMISSION_DETAILS = "collective.contact_behaviors.address_info_details.view"
REGISTRY_PREFIX = "contact"


@provider(IContextAwareDefaultFactory)
def default_state(context):
    key = f"{REGISTRY_PREFIX}.default_state"
    return api.portal.get_registry_record(key, default=None)


@provider(IContextAwareDefaultFactory)
def default_country(context):
    key = f"{REGISTRY_PREFIX}.default_country"
    return api.portal.get_registry_record(key, default=None)


@provider(IFormFieldProvider)
class IAddressInfo(model.Schema):
    directives.fieldset(
        "address_info",
        label=_("label_address_info", default="Address Information"),
        fields=(
            "address",
            "address_2",
            "city",
            "state",
            "postal_code",
            "country",
        ),
    )

    read_permission(
        address=PERMISSION_DETAILS,
        address_2=PERMISSION_DETAILS,
        city=PERMISSION,
        state=PERMISSION,
        postal_code=PERMISSION,
        country=PERMISSION,
    )

    address = schema.TextLine(
        title=_("label_address", default="Address"), required=False
    )

    address_2 = schema.TextLine(
        title=_("label_address_2", default="Additional Info"),
        description=_("description_address_2", default="Example: Room 2"),
        required=False,
    )

    city = schema.TextLine(
        title=_("label_address_city", default="City"),
        description=_("description_address_city", default="Example: Brasília"),
        required=False,
    )

    state = schema.TextLine(
        title=_("label_address_state", default="State / Province"),
        description=_("description_address_state", default="DF"),
        required=False,
        defaultFactory=default_state,
    )

    postal_code = schema.TextLine(
        title=_("label_address_postal_code", default="Postal Code"),
        description=_("description_address_postal_code", default="70123"),
        required=False,
    )

    country = schema.Choice(
        title=_("label_address_country", default="Country"),
        description=_("description_address_country", default="Please select a country"),
        vocabulary="collective.contact_behaviors.available_countries",
        required=False,
        defaultFactory=default_country,
    )
