#!/usr/bin/env python
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

"""The setup script."""

from setuptools import setup
from importlib.util import find_spec
from importlib.metadata import version as _get_version
from warnings import warn

version = {}
with open("enpt_enmapboxapp/version.py", encoding='utf-8') as version_file:
    exec(version_file.read(), version)

setup(
    scripts=[
        'bin/enpt_run_cmd.bat',
        'bin/enpt_run_cmd.sh'
    ],  # include both OS scripts because the feedstock build running on Linux would only include the .sh otherwise
)


# check for missing dependencies #
##################################

installationlink = 'https://enmap-box.readthedocs.io/en/latest/usr_section/usr_installation.html'

# check for qgis
if not find_spec('qgis'):
    warn('You need to install QGIS to run the EnPT-EnMAPBox-App. See here for installation instructions: %s'
         % installationlink)

# check for enmapbox
if not find_spec('enmapbox'):
    warn('You need to install the EnMAP-Box to run the EnPT-EnMAPBox-App. See here for installation instructions: %s'
         % installationlink)

# check for enpt
if find_spec('enpt'):
    from packaging.version import parse as _parse_version  # packaging is only available AFTER running setup()
    enpt_version = _get_version('enpt')
    if _parse_version(enpt_version) < _parse_version(version['_minimal_enpt_version']):
        warn(f"The EnPT backend package is already installed, however, its version (v{enpt_version}) is too old "
             f"and not compatible anymore with enpt_enmapboxapp v{version['__version__']}. Please update the EnPT "
             f"backend code to at least version {version['_minimal_enpt_version']}! Refer to "
             f"https://enmap.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/EnPT/doc/installation.html for more details.")
else:
    print(f"NOTE: To run EnPT within the EnMAP-Box via the EnPT GUI, the EnPT backend code is required "
          f"(minimal version: v{version['_minimal_enpt_version']}). Right now, it could not be found. Refer to "
          f"https://enmap.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/EnPT/doc/installation.html for more details.")
