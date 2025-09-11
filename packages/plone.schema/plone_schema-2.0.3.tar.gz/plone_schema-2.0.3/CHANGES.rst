.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

2.0.3 (2025-09-10)
------------------

Internal:


- Move distribution to src layout [gforcada] (#4217)


2.0.2 (2025-02-21)
------------------

Bug fixes:


- Fix email validation:
  * allow apostrophes
  * allow accented characters
  * allow ampersand in the user part
  * do not allows spaces.
  * accept TLDs with more than 4 characters
  [maurits] (#30)


Tests


- Refactor the ``jsonfield`` doctest to a simpler unit test.
  [maurits] (#5)
- Add basic tests for the email field.
  [maurits] (#5)


2.0.1 (2023-10-07)
------------------

Internal:


- Update configuration files.
  [plone devs] (cfffba8c)


2.0.0 (2023-04-06)
------------------

Breaking changes:


- Drop Python 2 support.
  Housecleaning: pyupgrade, isort, black.
  Introduce extras `plone.schema[supermodel]` and `plone.schema[schemaeditor]`.
  The package works in its vanilla installation as an addon for z3c.form, without any other plone dependencies.
  [jensens] (#17)


Bug fixes:


- Fix #12: no transitive circular dependency over `plone.app.z3c.form` anymore.
  This removes the registration on `IPloneFormLayer` and uses the base layer of z3c.form `IFormLayer`.
  [jensens] (#12)


Internal:


- Update configuration files.
  [plone devs] (93ecbf56)


1.4.0 (2022-04-28)
------------------

New features:


- Use indent in json.dumps to make JSON readable in the widget [MrTango] (#16)


1.3.0 (2021-03-24)
------------------

New features:


- Adjust JSONField to include widget name
  [sneridagh] (#10)


1.2.1 (2020-04-22)
------------------

Bug fixes:


- Minor packaging updates. (#1)
- Fix JSONField with default values saved to `model_source` XML
  [avoinea] (#7)
- Initialize towncrier.
  [gforcada] (#2548)


1.2.0 (2018-06-24)
------------------

New features:

- Improve and complete Plone integration of the JSONField (z3c.form, plone.supermodel, plone.schemaeditor)
  [sneridagh]


1.1.0 (2018-06-23)
------------------

New Features:

- Add new JSONField field and JSONSchema auto validation.
  [sneridagh]


1.0.0 (2016-02-25)
------------------

Fixes:

- Moved translation to plone.app.locales
  [staeff]

- Fixed install_requires to specify correct dependencies.
  [gforcada]


1.0a1 (2014-04-17)
------------------

- Initial release.
  [ianderso,davisagli,frapell]
