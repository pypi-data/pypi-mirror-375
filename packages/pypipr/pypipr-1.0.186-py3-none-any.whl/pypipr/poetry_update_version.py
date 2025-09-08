from subprocess import run


def poetry_update_version(mayor=False, minor=False, patch=False):
    if mayor:
        run("poetry version mayor", shell=True)
    if minor:
        run("poetry version minor", shell=True)
    if patch:
        run("poetry version patch", shell=True)
