from __future__ import absolute_import
import argparse
from pydeploy.environment import Environment

parser = argparse.ArgumentParser()
parser.add_argument("deployment_file")
parser.add_argument("dir")

def main():
    args = parser.parse_args()
    env = Environment(args.dir)
    env.create_and_activate()
    env.execute_deployment_file(args.deployment_file)
    return 0
