# coding: utf-8

import os
import sys
from configure import Configuration

current_dir = os.path.dirname(os.path.abspath(__file__))
config = Configuration.from_file(current_dir + '/settings.yml').configure()

sys.modules[__name__] = config
