env.install_from_git("git://github.com/vmalloc/capacity.git")

# pass blindly to pip
env.install_using_pip("fs")
# URL of a compressed package, with setup.py inside
env.install_from_url("https://github.com/vmalloc/pyforge/tarball/master")
# install using git

# checkout from git, then do stuff before installing
path = env.checkout_from_git("git://github.com/vmalloc/functors.git")
assert os.path.exists(os.path.join(path, "setup.py"))
env.install_from_dir(path)

import capacity
import functors
import forge
