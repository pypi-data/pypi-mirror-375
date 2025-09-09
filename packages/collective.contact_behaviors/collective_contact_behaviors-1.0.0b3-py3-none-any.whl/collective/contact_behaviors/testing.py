from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

import collective.contact_behaviors


class BehaviorsLayer(PloneSandboxLayer):
    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        self.loadZCML(package=collective.contact_behaviors)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "collective.contact_behaviors:default")
        applyProfile(portal, "collective.contact_behaviors:testing")


FIXTURE = BehaviorsLayer()


INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name="BehaviorsLayer:IntegrationTesting",
)


FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE, PLONE_RESTAPI_DX_FUNCTIONAL_TESTING),
    name="BehaviorsLayer:FunctionalTesting",
)
