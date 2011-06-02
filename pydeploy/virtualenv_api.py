"""
This utility module imports os stuff (or defines auxiliary API).
Its main use is to be stubbed in unit tests
"""
import os
from virtualenv import create_environment

def activate_environment(path):
    activate_script_path = os.path.join(path, "bin", "activate_this.py")
    execfile(activate_script_path, dict(__file__ = activate_script_path))
