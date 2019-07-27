import os
import sys

path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, path)

from hunter import hunt

hunt()
