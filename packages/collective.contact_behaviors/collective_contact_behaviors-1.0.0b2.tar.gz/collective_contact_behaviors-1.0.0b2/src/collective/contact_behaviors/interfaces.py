from zope import schema
from zope.interface import Interface


class IContactBehaviors(Interface):
    default_state = schema.TextLine(
        title="Default State",
        description="Return the default state to be used in addresses",
        default="",
        required=False,
    )
    default_country = schema.TextLine(
        title="Default Country",
        description="Return the default country to be used in addresses",
        default="",
        required=False,
    )
