import unittest


class TestEmail(unittest.TestCase):

    def test_fromUnicode(self):
        from plone.schema.email import Email
        from plone.schema.email import InvalidEmail

        # Value must be string
        self.assertEqual(
            Email().fromUnicode("arthur@example.org"),
            "arthur@example.org",
        )

        # We strip spaces.
        self.assertEqual(
            Email().fromUnicode("    arthur@example.org  "),
            "arthur@example.org",
        )

        # We do some validation
        with self.assertRaises(InvalidEmail):
            Email().fromUnicode("arthur")
        with self.assertRaises(InvalidEmail):
            Email().fromUnicode("arthur@")
        with self.assertRaises(InvalidEmail):
            Email().fromUnicode("arthur@one")
        with self.assertRaises(InvalidEmail):
            Email().fromUnicode("@one.two")

    def test_fromBytes(self):
        from plone.schema.email import Email
        from plone.schema.email import InvalidEmail

        # Value must be bytes
        self.assertEqual(
            Email().fromBytes(b"arthur@example.org"),
            "arthur@example.org",
        )

        # We strip spaces.
        self.assertEqual(
            Email().fromBytes(b"    arthur@example.org  "),
            "arthur@example.org",
        )

        # We do some validation
        with self.assertRaises(InvalidEmail):
            Email().fromBytes(b"arthur@one")

    def test_validation(self):
        # Let's test the email validation directly, without the field.
        from plone.schema.email import _isemail

        # Some good:
        self.assertTrue(_isemail("arthur@example.org"))

        # Some bad:
        self.assertFalse(_isemail(""))
        self.assertFalse(_isemail(" "))
        self.assertFalse(_isemail(" arthur@example.org"))
        self.assertFalse(_isemail("arthur@example.org\n"))
        self.assertFalse(_isemail("arthur\t@example.org"))
        self.assertFalse(_isemail("arthur@one"))
        self.assertFalse(_isemail("arthur@example@org"))
        self.assertFalse(_isemail("me@.me"))
        self.assertFalse(_isemail("x" * 254 + "@too.long"))

        # Explicitly test some examples from the docstring,
        # reported in the issue tracker.

        # 1. allow apostrophes
        self.assertTrue(_isemail("o'hara@example.org"))

        # 2. allow accented characters
        self.assertTrue(_isemail("jens@österreich.example.com"))

        # 3. allow ampersand in the user part
        self.assertTrue(_isemail("q&a@example.com"))

        # 4. do not allows spaces.
        self.assertFalse(_isemail("test@aha.ok   hello"))

        # 5. accept TLDs with more than 4 characters
        self.assertTrue(_isemail("me@you.online"))
        self.assertTrue(_isemail("me@example.museum"))
