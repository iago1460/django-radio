from invoke import task


@task
def clean(ctx):
    ctx.run("rm -rf docs/build")


@task(pre=[clean], default=True)
def build(ctx):
    ctx.run("sphinx-apidoc -f -o docs/source/source_code .")
    ctx.run("sphinx-build -b html -d docs/build/doctrees -D latex_paper_size=a4 docs/source docs/build/html")


# import os
#
# from utils import chdir, BASE_DIR
# DOCS_DIR = os.path.join(BASE_DIR, 'docs/')
#
#
# @task
# def build_translation(ctx):
#     with chdir(DOCS_DIR):
#         # ctx.run('make gettext') to create initial locales
#         # ctx.run('sphinx-intl update -p build/locale -l es') to create initial locales
#         ctx.run('sphinx-intl update -p build/locale')
