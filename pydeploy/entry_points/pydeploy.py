from __future__ import absolute_import
import argparse
import sys
import logging
from pydeploy.environment import Environment

parser = argparse.ArgumentParser()
parser.add_argument('-v', action='append_const', const=1, dest='verbose', default=[])
parser.add_argument("--pdb", action="store_true", default=False)
parser.add_argument("deployment_file")
parser.add_argument("dir")

def main():
    args, remainder_argv = parser.parse_known_args()
    _configure_logging(args)
    env = Environment(args.dir, remainder_argv)
    env.create_and_activate()
    try:
        env.execute_deployment_file(args.deployment_file)
    except:
        if args.pdb:
            import pdb
            pdb.post_mortem(sys.exc_info()[-1])
        raise
    return 0



def _configure_logging(args):
    level = logging.ERROR
    verbosity_level = sum(args.verbose)
    if verbosity_level > 0:
        if verbosity_level == 1:
            level = logging.INFO
        else:
            level = logging.DEBUG
    logging.basicConfig(
        stream=sys.stderr,
        level=level,
        format="--> %(message)s"
        )
