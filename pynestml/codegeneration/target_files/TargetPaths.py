#
# TargetPaths.py
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

from pynestml.frontend.FrontendConfiguration import FrontendConfiguration


class TargetPaths(object):
    def __init__(self):
        # type: () -> None
        self.sli_directory = os.path.join(FrontendConfiguration.getTargetPath(), 'sli')
        self.module_header_path = os.path.join(FrontendConfiguration.getTargetPath(),
                                               FrontendConfiguration.getModuleName()) + '.h'
        self.module_implementation_path = os.path.join(FrontendConfiguration.getTargetPath(),
                                                       FrontendConfiguration.getModuleName()) + '.cpp'
        self.c_make_lists_path = os.path.join(FrontendConfiguration.getTargetPath(), 'CMakeLists') + '.txt'
        self.sli_init_path = os.path.join(FrontendConfiguration.getTargetPath(), 'sli',
                                          FrontendConfiguration.getModuleName() + "-init") + '.sli'
        self.neuron_header_path = os.path.join(FrontendConfiguration.getTargetPath(), '%s.h')
        self.neuron_implementation_path = os.path.join(FrontendConfiguration.getTargetPath(), '%s.cpp')
