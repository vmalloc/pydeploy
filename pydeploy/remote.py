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

def deploy_via_ssh(hostname, deployment_script, directory):
    command, stdin = get_deployment_command_and_stdin(deployment_script, directory)
    p = subprocess.Popen(["ssh", hostname, command], stdin=subprocess.PIPE)
    p.stdin.write(stdin)
    return p.wait()

def get_deployment_command_and_stdin(deployment_script, directory):
    lazy_fetcher_length = len(_BOOTSTRAPPER_LAZY_FETCHER)
    stdin = "{0}\n{1}{2}".format(lazy_fetcher_length, _BOOTSTRAPPER_LAZY_FETCHER, deployment_script)
    return "python -c '{0}' {1}".format(_BOOTSTRAPPER_BOILERPLATE, directory), stdin

if __name__ == '__main__':
    command, stdin = get_deployment_command_and_stdin("print 2", "/tmp/deployment")
    print command
    print stdin
