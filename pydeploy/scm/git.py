import os
from .. import command

def clone_to_or_update(url, branch, path):
    if os.path.exists(path):
        update(url, branch, path)
    else:
        clone_to(url, branch, path)

def update(url, branch, path):
    command.execute_assert_success("git fetch {0} {1}".format(url, branch), shell=True, cwd=path)
    command.execute_assert_success("git reset --hard FETCH_HEAD && git clean -fdx", shell=True, cwd=path)

def clone_to(url, branch, path):
    command.execute_assert_success("git clone -b {0} {1} {2}".format(branch, url, path), shell=True)

