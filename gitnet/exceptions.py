# *********************************************************************************************
# Copyright (C) 2016 Jillian Anderson, Joel Becker, Steve McColl and Dr. John McLevey
#
# This file is part of the gitnet package developed for Dr John McLevey's Networks Lab
# at the University of Waterloo. For more information, see http://networkslab.org/gitnet/.
#
# gitnet is free software: you can redistribute it and/or modify it under the terms of a
# GNU General Public License as published by the Free Software Foundation. gitnet is
# distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even
# the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with gitnet.
# If not, see <http://www.gnu.org/licenses/>.
# *********************************************************************************************

class gitnetException(Exception):
    pass


class RepositoryError(gitnetException):
    """
    Exception given when a problem is detected when interacting with a Git repository.
    """
    pass


class ParseError(gitnetException):
    """
    Exception given when an error occurs during parsing.
    """
    pass


class InputError(gitnetException):
    """
    Exception given when the user gives an invalid input.
    """
    pass


class NetworkError(gitnetException):
    """
    Exception given when there is a problem converting a Log Object to a MultiGraphPlus Object.
    """


class ExportError(gitnetException):
    """
    Exception given when gitnet is unable to export a given edgelist, node attribute list, or other object.
    """


class MergeError(gitnetException):
    """
    Exception given when the user provides nodes to node_merge() which do not meet the initial checks
    """
    pass

class GraphStatsError(gitnetException):
    """
    Exception given when the network graph statistics are not generated as expected.
    """
    pass
