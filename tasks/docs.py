from invoke import Collection, task


@task
def clean(ctx):
    ctx.run("rm -rf docs/build")


@task(pre=[clean], default=True)
def build(ctx):
    ctx.run("sphinx-apidoc -f -o docs/source/documentation .")
    ctx.run("sphinx-build -b html -d docs/build/doctrees -D latex_paper_size=a4 docs/source docs/build/html")

ns = Collection(clean, build)
