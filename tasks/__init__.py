from invoke import Collection

import heroku
import radioco
import docker
import docs
import locale


ns = Collection()
ns.add_collection(Collection.from_module(heroku))
ns.add_collection(docker)
ns.add_collection(docs)
ns.add_collection(locale)
ns.add_task(radioco.quickstart)
ns.add_task(radioco.commit_changes)
ns.add_task(radioco.checkout_latest)
