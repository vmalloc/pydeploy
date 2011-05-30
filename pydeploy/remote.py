import subprocess

_BOOTSTRAPPER_BOILERPLATE = ";".join(
    """import sys
boilerplate_length=int(sys.stdin.readline())
exec sys.stdin.read(boilerplate_length)""".splitlines())

_BOOTSTRAPPER_LAZY_FETCHER = """
try:
    from pydeploy.entry_points.pydeploy import main
except ImportError:
    import urllib2
    data = urllib2.urlopen("https://github.com/vmalloc/pydeploy/raw/master/scripts/bootstrapper.py").read()
    exec data
else:
    sys.exit(main())"""

def deploy_via_ssh(hostname, deployment_script, directory, args=()):
    command, stdin = get_deployment_command_and_stdin(deployment_script, directory)
    cmd = ["ssh", hostname, command]
    cmd.extend(args)
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    p.stdin.write(stdin)
    p.stdin.close()
    return p.wait()

def get_deployment_command_and_stdin(deployment_script, directory):
    lazy_fetcher_length = len(_BOOTSTRAPPER_LAZY_FETCHER)
    stdin = "{0}\n{1}".format(lazy_fetcher_length, _BOOTSTRAPPER_LAZY_FETCHER)
    if isinstance(deployment_script, basestring):
        arg = deployment_script
    else:
        arg = "-"
        stdin += deployment_script.read()
    return "python -c '{0}' {1} {2}".format(_BOOTSTRAPPER_BOILERPLATE, arg, directory), stdin

