from json import JSONDecodeError
from zope.i18nmessageid import MessageFactory
from zope.interface import Attribute
from zope.interface import implementer
from zope.schema import Field
from zope.schema._bootstrapinterfaces import WrongType
from zope.schema.interfaces import IField
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import WrongContainedType

import ast
import json
import jsonschema


_ = MessageFactory("plone")


DEFAULT_JSON_SCHEMA = json.dumps({"type": "object", "properties": {}})


class IJSONField(IField):
    """A text field that stores A JSON."""

    schema = Attribute("schema", _("The JSON schema string serialization."))


@implementer(IJSONField, IFromUnicode)
class JSONField(Field):
    def __init__(self, schema=DEFAULT_JSON_SCHEMA, widget=None, **kw):
        if not isinstance(schema, str):
            raise WrongType
        if widget and not isinstance(widget, str):
            raise WrongType

        self.widget = widget

        try:
            self.json_schema = json.loads(schema)
        except ValueError:
            raise WrongType
        super().__init__(**kw)

    def _validate(self, value):
        super()._validate(value)

        try:
            jsonschema.validate(value, self.json_schema)
        except jsonschema.ValidationError as e:
            raise WrongContainedType(e.message, self.__name__)

    def fromUnicode(self, value):
        """Get value from unicode.

        Value can be a valid JSON object:

            JSONField().fromUnicode('{"items": []}')

        or it can be a Python dict stored as string:

            JSONField().fromUnicode("{'items': []}")

        In both cases the result is:

            {"items": []}
        """
        try:
            v = json.loads(value)
        except JSONDecodeError:
            v = ast.literal_eval(value)

        self.validate(v)
        return v
