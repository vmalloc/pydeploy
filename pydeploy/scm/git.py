import os
from .. import command

def clone_to_or_update(url, path):
    if os.path.exists(path):
        update(url, path)
    else:
        clone_to(url, path)

def update(url, path):
    command.execute_assert_success("git fetch {0}".format(url), shell=True, cwd=path)
    command.execute_assert_success("git reset --hard FETCH_HEAD && git clean -fdx".format(url), shell=True, cwd=path)

def clone_to(url, path):
    command.execute_assert_success("git clone {0} {1}".format(url, path), shell=True)

