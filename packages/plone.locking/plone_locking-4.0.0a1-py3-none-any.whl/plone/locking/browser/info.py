import zope.deferredimport


zope.deferredimport.initialize()

zope.deferredimport.deprecated(
    "Please use from plone.app.layout.viewlets.locking import LockInfoViewlet",
    LockInfoViewlet="plone.app.layout:viewlets.locking.LockInfoViewlet",
)
