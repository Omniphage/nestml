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


class PyNestmlCoveredTest(unittest.TestCase):
    module_under_test = None

    if os.environ['run_coverage'] == 'True':
        coverage = Coverage()
    else:
        coverage = None

    @staticmethod
    def set_logging_level():
        # type: () -> None
        raise NotImplementedError("Test case must implement set_logging_level")

    @staticmethod
    @nottest
    def set_module_under_test():
        # type: () -> None
        raise NotImplementedError("Test case must implement set_module_under_test")

    @classmethod
    def setUpClass(cls):
        # type: () -> None
        cls.set_logging_level()
        cls.set_module_under_test()
        assert cls.module_under_test is not None, "set_module_under_test must set the module_under_test class attribute"
        if os.environ['run_coverage'] == 'True':
            cls.start_coverage()

    @classmethod
    def start_coverage(cls):
        # type: () -> None
        cls.coverage.set_option('run:include', [cls.module_under_test])
        path_segments = cls.module_under_test.split('/')
        filename = path_segments[len(path_segments) - 1].split('.')[0]
        cls.coverage.set_option('run:data_file', filename)
        cls.coverage.start()

    @classmethod
    def tearDownClass(cls):
        # type: () -> None
        if os.environ['run_coverage'] == 'True':
            cls.stop_coverage()

    @classmethod
    def stop_coverage(cls):
        # type: () -> None
        cls.coverage.stop()
        cls.coverage.save()
        percentage = cls.coverage.report(cls.module_under_test)
        pretty_percentage = round(percentage, 2)
        threshold = 95.00
        #assert pretty_percentage > threshold, "Test coverage is %s%%. Target is %s%%" % (pretty_percentage, threshold)
