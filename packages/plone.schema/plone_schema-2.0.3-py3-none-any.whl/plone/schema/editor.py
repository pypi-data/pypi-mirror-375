from .email import Email
from .email import IEmail
from .jsonfield import IJSONField
from .jsonfield import JSONField
from plone.schemaeditor.fields import FieldFactory
from zope.i18nmessageid import MessageFactory
from zope.interface import Attribute
from zope.schema import URI
from zope.schema.interfaces import IURI


_ = MessageFactory("plone")


class IURI(IURI):
    # prevent some settings from being included in the field edit form
    default = Attribute("")


class IEmail(IEmail):
    # prevent some settings from being included in the field edit form
    default = Attribute("")


class IJSON(IJSONField):
    # prevent some settings from being included in the field edit form
    default = Attribute("")


URIFactory = FieldFactory(URI, _("URL"))
EmailFactory = FieldFactory(Email, _("Email"))
JSONFactory = FieldFactory(JSONField, _("JSONField"))
