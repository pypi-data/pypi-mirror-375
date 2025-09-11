from .email import Email
from .jsonfield import JSONField
from plone.supermodel.exportimport import BaseHandler
from zope.schema import URI


URIHandler = BaseHandler(URI)
EmailHandler = BaseHandler(Email)
JSONHandler = BaseHandler(JSONField)
