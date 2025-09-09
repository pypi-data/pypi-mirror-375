# -*- coding: utf-8 -*-

# enpt_enmapboxapp, A QGIS EnMAPBox plugin providing a GUI for the EnMAP processing tools (EnPT)
#
# Copyright (C) 2018–2025 Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz.de)
#
# This software was developed within the context of the EnMAP project supported
# by the DLR Space Administration with funds of the German Federal Ministry of
# Economic Affairs and Energy (on the basis of a decision by the German Bundestag:
# 50 EE 1529) and contributions from DLR, GFZ and OHB System AG.
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>.

"""Top-level package for enpt_enmapboxapp."""

import os as __os

from .version import __version__, __versionalias__   # noqa (E402 + F401)
# NOTE: importing the main classes here would break the conda-forge builds as they don't package qgis and enmapbox


__author__ = """Daniel Scheffler"""
__email__ = 'danschef@gfz.de'
__all__ = ['__version__',
           '__versionalias__',
           '__author__',
           '__email__'
           ]


# $PROJ_LIB was renamed to $PROJ_DATA in proj=9.1.1, which leads to issues with fiona>=1.8.20,<1.9
# https://github.com/conda-forge/pyproj-feedstock/issues/130
# -> fix it by setting PROJ_DATA
if 'GDAL_DATA' in __os.environ and 'PROJ_DATA' not in __os.environ and 'PROJ_LIB' not in __os.environ:
    __os.environ['PROJ_DATA'] = __os.path.join(__os.path.dirname(__os.environ['GDAL_DATA']), 'proj')
