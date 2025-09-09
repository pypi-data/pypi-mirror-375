from plone import api
from zope.i18nmessageid import MessageFactory
from zope.interface import provider
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import pycountry


_ = MessageFactory("iso_3166-1")


@provider(IVocabularyFactory)
def available_countries_vocabulary(context):
    """Vocabulary of all countries that could be used."""
    terms = []
    for country in pycountry.countries:
        code = country.alpha_2
        title = _(country.name)
        terms.append(SimpleTerm(code, code, title))
    # Sort by title
    terms = sorted(terms, key=lambda x: x.title)
    return SimpleVocabulary(terms)


@provider(IVocabularyFactory)
def countries_vocabulary(context):
    """Vocabulary of countries already in use."""
    terms = []
    ct = api.portal.get_tool("portal_catalog")
    for alpha_2 in ct.uniqueValuesFor("country"):
        country = pycountry.countries.get(alpha_2=alpha_2)
        code = country.alpha_2
        title = _(country.name)
        terms.append(SimpleTerm(code, code, title))
    return SimpleVocabulary(terms)
