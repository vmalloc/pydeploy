#scm
env.install(source=SCM("git://github.com/vmalloc/capacity.git"))

# pass blindly to pip
env.install(source=PIP("fs"))
# ...which is also the default
env.install("fs")

# URL of a compressed package, with setup.py inside
env.install(source=URL("https://github.com/vmalloc/pyforge/tarball/master"))

# checkout from git, then do stuff before installing
path = env.checkout(source=SCM("git://github.com/vmalloc/functors.git"))
assert os.path.exists(os.path.join(path, "setup.py"))
# paths take precedence over PIP on install, assuming they exist as local paths
env.install(path)
# but of course you can also use the explicit path
env.install(source=Path(path))

import capacity
import functors
import forge
