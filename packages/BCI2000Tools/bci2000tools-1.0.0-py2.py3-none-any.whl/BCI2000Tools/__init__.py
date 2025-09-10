# -*- coding: utf-8 -*-

# ///////////////////////////////////////////////////////////////////////////
# $Id: __init__.py 9041 2025-09-09 20:29:54Z jhill $
# Author: jeremy.hill@neurotechcenter.org
# Description: root namespace of the BCI2000Tools package
#
# $BEGIN_BCI2000_LICENSE$
#
# This file is part of BCI2000, a platform for real-time bio-signal research.
# [ Copyright (C) 2000-2022: BCI2000 team and many external contributors ]
#
# BCI2000 is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# BCI2000 is distributed in the hope that it will be useful, but
#                         WITHOUT ANY WARRANTY
# - without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#
# $END_BCI2000_LICENSE$
# ///////////////////////////////////////////////////////////////////////////

__version__ = '1.0.0'

USE_NUMPY_MATRIX = True # TODO: numpy.matrix is getting deprecated.
                        #       Switch it off here as soon as we are sure no client code
                        #       relies on the .A .H .I attributes or * / \ operator
                        #       behavior of signal arrays and state arrays (FileReader)
                        #       or ChannelSet objects and the spatial-filter matrices
                        #       their methods produce (Electrodes).

from . import Bootstrapping; from .Bootstrapping import *

# NB: do NOT import .Remote automatically (it has side effects and may fail, depending on bci2000root() setting)
