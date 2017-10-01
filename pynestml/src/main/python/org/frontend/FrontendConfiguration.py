#
# FrontendConfiguration.py
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
import argparse  # used for parsing of input arguments
import os
from pynestml.src.main.python.org.nestml.parser.NESTMLParserExceptions import InvalidPathException
from pynestml.src.main.python.org.utils.Logger import Logger


class FrontendConfiguration(object):
    """
    This class encapsulates all settings as handed over to the frontend at start of the toolchain.
    """
    __argumentParser = None
    __pathsToCompilationUnits = None
    __providedPath = None
    __loggingLevel = None
    __dryRun = None
    __targetPath = None

    @classmethod
    def config(cls, _args=None):
        """
        Standard constructor.
        :param _args: a set of arguments as handed over to the frontend
        :type _args: list(str)
        """
        cls.__argumentParser = argparse.ArgumentParser(
            description='NESTML is a domain specific language that supports the specification of neuron models in a precise'
                        'and concise syntax, based on the syntax of Python. Model equations can either be given as a simple'
                        ' string of mathematical notation or as an algorithm written in the built-in procedural language.'
                        ' The equations are analyzed by NESTML to compute an exact solution'
                        ' if possible or use an appropriate numeric solver otherwise.')
        cls.__argumentParser.add_argument('-path', type=str, nargs='+',
                                          help='Path to a single file or a directory containing the source models.')
        cls.__argumentParser.add_argument('-target', metavar='Target', type=str, nargs='?',
                                          help='Path to a target directory where models should be generated to.')
        cls.__argumentParser.add_argument('-dry', action='store_true',
                                          help='Indicates that a dry run shall be performed, i.e.,'
                                               ' without generating a target model.')
        cls.__argumentParser.add_argument('-logging_level', type=str, nargs='?',
                                          help='Indicates which messages shall be logged and printed to the'
                                               'screen. Available ={ALL,WARNING/S,ERROR/S,NO}, Standard is ERRORS.')
        parsed_args = cls.__argumentParser.parse_args(_args)
        cls.__providedPath = parsed_args.path
        if cls.__providedPath is None:
            # check if the mandatory path arg has been handed over, just terminate
            raise InvalidPathException()
        cls.__pathsToCompilationUnits = list()
        if os.path.isfile(parsed_args.path[0]):
            cls.__pathsToCompilationUnits.append(parsed_args.path[0])
        elif os.path.isdir(parsed_args.path[0]):
            for filename in os.listdir(parsed_args.path[0]):
                if filename.endswith(".nestml"):
                    cls.__pathsToCompilationUnits.append(os.path.join(parsed_args.path[0],filename))
        else:
            raise InvalidPathException()
        # initialize the logger
        cls.__loggingLevel = parsed_args.logging_level
        Logger.initLogger(Logger.stringToLevel(parsed_args.logging_level))
        # check if a dry run shall be preformed, i.e. without generating a target model
        cls.__dryRun = parsed_args.dry
        cls.__targetPath = str(os.path.realpath(os.path.join( '..', '..', '..','..',parsed_args.target)))
        return

    @classmethod
    def getPath(cls):
        """
        Returns the path to the handed over directory or file.
        :return: a single path
        :rtype: str
        """
        return cls.__providedPath

    @classmethod
    def getFiles(cls):
        """
        Returns a list of all files to process.
        :return: a list of paths to files as str.
        :rtype: list(str)
        """
        return cls.__pathsToCompilationUnits

    @classmethod
    def isDryRun(cls):
        """
        Indicates whether it is a dry run, i.e., no modell shall be generated
        :return: True if dry run, otherwise false.
        :rtype: bool
        """
        return cls.__dryRun

    @classmethod
    def getLoggingLevel(cls):
        """
        Returns the set logging level.
        :return: the logging level
        :rtype: LOGGING_LEVEL
        """
        return cls.__loggingLevel

    @classmethod
    def getTargetPath(cls):
        """
        Returns the path to which models shall be generated to.
        :return: the target path.
        :rtype: str
        """
        return cls.__targetPath