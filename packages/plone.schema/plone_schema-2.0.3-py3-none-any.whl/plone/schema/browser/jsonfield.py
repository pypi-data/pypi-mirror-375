from ..interfaces import IFormLayer
from ..jsonfield import IJSONField
from z3c.form.browser.textarea import TextAreaWidget
from z3c.form.interfaces import IDataConverter
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import ITextAreaWidget
from z3c.form.interfaces import IWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.component import adapts
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer

import json


_ = MessageFactory("plone")


class IJSONFieldWidget(ITextAreaWidget):
    """JSON Widget"""


@implementer(IJSONFieldWidget)
class JSONWidget(TextAreaWidget):
    klass = "json-widget"
    value = None


@adapter(IJSONField, IFormLayer)
@implementer(IFieldWidget)
def JSONFieldWidget(field, request):
    return FieldWidget(field, JSONWidget(request))


@implementer(IDataConverter)
class JSONDataConverter:
    """A JSON data converter."""

    adapts(IJSONField, IWidget)

    def __init__(self, field, widget):
        self.field = field
        self.widget = widget

    def toWidgetValue(self, value):
        """See interfaces.IDataConverter"""
        if value is self.field.missing_value:
            return ""
        return json.dumps(value, indent=True)

    def toFieldValue(self, value):
        """See interfaces.IDataConverter"""

        if value == "":
            return self.field.missing_value

        return self.field.fromUnicode(value)
