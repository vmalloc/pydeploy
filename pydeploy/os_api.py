"""
This utility module imports os stuff (or defines auxiliary API).
Its main use is to be stubbed in unit tests
"""
from os import makedirs
from os.path import isdir as directory_exists
from urllib2 import urlopen
