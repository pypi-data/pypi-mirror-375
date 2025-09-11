Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

4.0.0a1 (2025-09-10)
--------------------

Breaking changes:


- Moved ``plone.locking.browser.info.LockInfoViewlet`` template to ``plone.app.layout.viewlets``.
  [cihanandac] (#3953)


Internal:


- Update configuration files.
  [plone devs]


3.0.2 (2025-01-24)
------------------

Bug fixes:


- Fix DeprecationWarnings. [maurits] (#4090)


3.0.1 (2024-01-22)
------------------

Internal:


- Update configuration files.
  [plone devs] (6e36bcc4, 7723aeaf)


3.0.0 (2023-04-16)
------------------

Breaking changes:


- Drop python 2.7. (#1)


New features:


- Update the info viewlet css classes to Bootstrap 5.
  [ewohnlich] (bs5)


Internal:


- Update configuration files.
  [plone devs] (234bb1d6, 5cc689e5)


2.3.0 (2023-02-08)
------------------

Bug fixes:


- Update to Zope4 only including troove classifiers. [jensens] (#19)


2.2.5 (2021-10-09)
------------------

Bug fixes:


- Register a fallback @@plone_lock_info view to allow objects without plone.locking behavior to be edited.
  [ericof] (#3331)


2.2.4 (2020-04-20)
------------------

Bug fixes:


- Minor packaging updates. (#1)


2.2.3 (2018-09-27)
------------------

Bug fixes:

- More Python 2 / 3 compatibility fixes.
  [thet]


2.2.2 (2018-02-05)
------------------

Bug fixes:

- Update tests to not use plone.app.testing.bbb code.
  This should avoid test isolation problems.
  [gforcada]


2.2.1 (2018-02-02)
------------------

Bug fixes:

- Add Python 2 / 3 compatibility
  [pbauer]


2.2 (2017-06-08)
----------------

New features:

- All LockingOperations method can optionally redirect to the context view
  [ale-rt]

Bug fixes:

- Test fix: Use print in doctest (Python 3/ Zope 4 compat)
  [MatthewWilkes]


2.1.3 (2016-09-09)
------------------

New features:

- Update README.rst with Compatibility
  [djowett]


2.1.2 (2016-08-15)
------------------

Fixes:

- Use zope.interface decorator.
  [gforcada]


2.1.1 (2015-10-27)
------------------

New:

- Use registry lookup for types_use_view_action_in_listings
  [esteele]

- Locks stored on annotations are a safe write on read.
  [gforcada]


2.1.0 (2015-09-07)
------------------

- Pull lock_on_ttw_edit setting from the configuration registry
  [esteele]


2.0.8 (2015-07-20)
------------------

- Fix write on read CSRF issues with latest plone.protect
  [vangheem]


2.0.7 (2015-06-05)
------------------

- Fix possible package problem with Python 2.6 and old setuptools (at
  least 0.6c11) not finding the ``README.txt``.
  [maurits]


2.0.6 (2015-06-05)
------------------

- Pep8.
  [vangheem]


2.0.5 (2014-10-20)
------------------

- Adding "create_lock" to "plone_lock_operations"
  [hman]

- The locking timeout is now modifiable through LockType definition
  [parruc]

- Ported to plone.app.testing
  [tomgross]


2.0.4 (2012-10-20)
------------------

- Do not download the file when we click on "unlock" in the context of a file.
  Refs https://dev.plone.org/ticket/13191
  [thomasdesvenain]


2.0.3 (2012-01-04)
------------------

- Check if context is not joined to zodb connection for transaction where lock
  is added.
  [fafhrd91]

2.0.2 (2011-11-29)
------------------

- Do not cleanup stale lock if database is in read-only mode.
  http://dev.plone.org/ticket/12239
  [fafhrd91]


2.0.1 - 2011-05-12
------------------

- Make plone.locking check for the global lock settings if a context-specific
  adapter is not found. Fixes http://dev.plone.org/plone/ticket/11779
  [ggozad]

- Add MANIFEST.in.
  [WouterVH]


2.0 - 2010-07-18
----------------

- Define all package dependencies.
  [hannosch]

- Update license to GPL version 2 only.
  [hannosch]


1.2.1 - 2010-07-01
------------------

- Load the ``cmf.*`` permissions from Products.CMFCore.
  [hannosch]


1.2.0 - 2009-03-04
------------------

- Added IRefreshableLockable interface and TTWLockable implementation.
  [davisagli]

- Changed default lock timeout to 10 minutes.
  [davisagli]


1.1.0
-----

- Clarified license and copyright statements.
  [hannosch]

- Declare test dependencies in an extra. Avoid dependency on Plone.
  [hannosch]

- Specify package dependencies.
  [hannosch]

- Fix missing internationalization (#8609 thanks to Vincent Fretin)
  [encolpe]


1.0.5 - 2008-01-03
------------------

- Fix lock timeout which was set by default to 12 minutes, it is
  now set to maxtimeout (71582788 minutes).
  Fixes http://dev.plone.org/plone/ticket/7358
  [jfroche]

- Fix TypeError when an anonymous user locks content.  Fixes
  http://dev.plone.org/plone/ticket/7246
  [maurits]


1.0 - 2007-08-17
----------------

- Initial release.
