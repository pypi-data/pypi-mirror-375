from zope.i18nmessageid import MessageFactory
from zope.interface import implementer
from zope.schema import NativeStringLine
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import INativeStringLine
from zope.schema.interfaces import ValidationError


_ = MessageFactory("plone")


class IEmail(INativeStringLine):
    """A field containing an email address"""


class InvalidEmail(ValidationError):
    __doc__ = _("""The specified email is not valid.""")


def _isemail(value):
    r"""Is this a valid email?

    https://www.regular-expressions.info/email.html has some hints on how to
    check for a valid email with regular expressions.  It also gives reasons
    for why you may *not* want to use them.  A too simple regex will work for
    most cases, but may give false negatives: it will treat a rare but valid
    email address as invalid.  A complex regex may still allow some invalid
    email addresses, and is hard to debug in case of errors.

    Originally we had this regex, unchanged between 2013 and 2024:

        import re
        _isemail = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}"
        _isemail = re.compile(_isemail).match

    Problems:

    1. It does not allow apostrophes.
       Example: o'hara@example.org
       See: https://github.com/plone/plone.schema/issues/6

    2. It does not allow accented characters.
       Example: jens@österreich.example.com
       See: https://github.com/plone/plone.schema/issues/9

    3. It does not allow ampersand in the user part.
       Example: q&a@.example.com
       See: https://github.com/plone/plone.schema/issues/15

    4. It allows spaces.
       Example: "test@aha.ok   hello"
       See: https://github.com/plone/plone.schema/issues/30

    5. It correctly accepts TLDs with more than 4 characters,
       but this seems by accident, so it could get lost in an update.
       Example: me@you.online
       See: https://github.com/plone/plone.schema/issues/30
    """
    # We only accept a string.
    if not isinstance(value, str):
        return False

    # It is up to the caller to strip spaces, newlines, etc.
    if value != value.strip():
        return False
    if len(value.split()) != 1:
        return False

    # only one @ sign
    if value.count("@") != 1:
        return False

    # At least one dot in the domain.  And when split on dot,
    # each part must not be empty.
    user, domain = value.split("@")
    if not all(domain.partition(".")):
        return False

    # user part must not be empty
    if not user:
        return False

    # The maximum length of an email address that can be handled by SMTP
    # is 254 characters.
    if len(value) > 254:
        return False

    # We have found no problems.
    return True


@implementer(IEmail, IFromUnicode)
class Email(NativeStringLine):
    """Email schema field"""

    def _validate(self, value):
        super()._validate(value)
        if _isemail(value):
            return

        raise InvalidEmail(value)

    def fromBytes(self, value):
        # Originally, fromBytes was not defined.
        # Upstream NativeStringLine had it, but without the 'strip'
        # that we added in fromUnicode.
        value = value.strip().decode("utf-8")
        self.validate(value)
        return value

    def fromUnicode(self, value):
        v = str(value.strip())
        self.validate(v)
        return v
