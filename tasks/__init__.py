from invoke import Collection

import heroku
import radioco
import docker
import docs


ns = Collection()
ns.add_collection(Collection.from_module(heroku))
ns.add_collection(Collection.from_module(docker))
ns.add_collection(Collection.from_module(docs))
ns.add_task(radioco.quickstart)
ns.add_task(radioco.commit_changes)
ns.add_task(radioco.checkout_latest)
