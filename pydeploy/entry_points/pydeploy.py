from __future__ import absolute_import
import argparse
import sys
from pydeploy.environment import Environment

parser = argparse.ArgumentParser()
parser.add_argument("--pdb", action="store_true", default=False)
parser.add_argument("deployment_file")
parser.add_argument("dir")

def main():
    args, remainder_argv = parser.parse_known_args()
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
