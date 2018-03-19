#
# PyNestmlCoveredTest.py
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
import unittest
from nose.tools import nottest

from coverage import Coverage
from pathlib import Path, PurePath


class PyNestmlCoveredTest(unittest.TestCase):
    module_under_test = None

    @staticmethod
    def set_logging_level():
        # type: () -> None
        raise NotImplementedError("Test case must implement set_logging_level")

    @staticmethod
    @nottest
    def set_module_under_test():
        # type: () -> None
        raise NotImplementedError("Test case must implement set_module_under_test")


