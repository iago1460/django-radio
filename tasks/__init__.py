from invoke import Collection

from . import docs, locale


ns = Collection()
ns.add_collection(docs)
ns.add_collection(locale)
