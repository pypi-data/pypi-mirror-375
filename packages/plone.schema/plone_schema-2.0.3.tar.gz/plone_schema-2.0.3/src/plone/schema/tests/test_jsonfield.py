import unittest


class TestJsonField(unittest.TestCase):

    def test_fromUnicode(self):
        from plone.schema.jsonfield import JSONField

        # Value can be a valid JSON object:
        self.assertDictEqual(
            JSONField().fromUnicode('{"items": []}'),
            {"items": []},
        )

        # or it can be a Python dict stored as string:
        self.assertDictEqual(JSONField().fromUnicode("{'items': []}"), {"items": []})
