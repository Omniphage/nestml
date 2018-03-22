#
# TargetFile.py
#
# This file is part of NEST.
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

import os
from abc import ABCMeta, abstractmethod

from jinja2 import Template

from pynestml.frontend.FrontendConfiguration import FrontendConfiguration


class TargetFile(object):
    __metaclass__ = ABCMeta

    def __init__(self, _path, _template):
        # type: (str, Template) -> None
        self.path = _path
        self.template = _template

    def generate(self):
        # type: () -> None
        self.create_target_directory()
        with open(self.path, 'w+') as f:
            f.write(self.template.render(self.setup_namespace()))

    @abstractmethod
    def setup_namespace(self):
        # type: () -> dict
        pass

    @staticmethod
    def create_target_directory():
        # type: () -> None
        target_dir = FrontendConfiguration.getTargetPath()
        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)
