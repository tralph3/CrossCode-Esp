#!/usr/bin/env python

import os.path
import sys

project_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(project_dir, "crosscode-localization-engine", "mod-tools", "src"))

import crosslocale.mod_tools

crosslocale.mod_tools.main([f"--project={project_dir}", "download"])
