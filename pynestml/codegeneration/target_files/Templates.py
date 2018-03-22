#
# Templates.py
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

from jinja2 import Environment, FileSystemLoader


class Templates(object):
    env = Environment(loader=FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templatesNEST')))
    c_make_lists = env.get_template('CMakeLists.jinja2')
    module_implementation = env.get_template('ModuleClass.jinja2')
    module_header = env.get_template('ModuleHeader.jinja2')
    sli_init = env.get_template('SLI_Init.jinja2')
    neuron_header = env.get_template('NeuronHeader.jinja2')
    neuron_implementation = env.get_template('NeuronClass.jinja2')
