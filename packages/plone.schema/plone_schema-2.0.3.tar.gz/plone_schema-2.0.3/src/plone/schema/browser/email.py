from ..email import IEmail
from ..interfaces import IFormLayer
from z3c.form.browser.text import TextWidget
from z3c.form.interfaces import IFieldWidget
from z3c.form.interfaces import ITextWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer


_ = MessageFactory("plone")


class IEmailWidget(ITextWidget):
    """Email Widget"""


@implementer(IEmailWidget)
class EmailWidget(TextWidget):
    klass = "email-widget"
    value = None


@adapter(IEmail, IFormLayer)
@implementer(IFieldWidget)
def EmailFieldWidget(field, request):
    return FieldWidget(field, EmailWidget(request))
