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

def reset_submodules(path):
    command.execute_assert_success("git submodule update --init", cwd=path, shell=True)

class Ref(str):
    def to_ref_name(self):
        return str(self)
class Branch(Ref):
    pass
class Tag(Ref):
    def to_ref_name(self):
        return "tags/{0}".format(self)

def get_remote_references_dict(url):
    returned = {}
    _, output = command.execute_assert_success("git ls-remote {0}".format(url), shell=True)
    for line in output.splitlines():
        hash, ref = line.split(None, 1)
        if ref.startswith('refs/heads/'):
            ref = Branch(ref.split('/', 2)[-1])
        elif ref.startswith('refs/tags/'):
            ref = Tag(ref.split('/', 2)[-1])
        else:
            continue
        returned[ref] = hash
    return returned
