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

"""This module provides the EnPTAlgorithm which is used in case EnPT is installed into QGIS Python environment."""

import os
from importlib.util import find_spec
from importlib.metadata import version as get_version

from qgis.core import \
    (QgsProcessingContext,
     QgsProcessingFeedback,
     NULL
     )

from ._enpt_alg_base import _EnPTBaseAlgorithm
from .version import check_minimal_enpt_version


class EnPTAlgorithm(_EnPTBaseAlgorithm):
    @staticmethod
    def _prepare_enpt_environment() -> dict:
        os.environ['PYTHONUNBUFFERED'] = '1'
        os.environ['IS_ENPT_GUI_CALL'] = '1'
        # os.environ['IS_ENPT_GUI_TEST'] = '1'

        enpt_env = os.environ.copy()
        enpt_env["PATH"] = ';'.join([i for i in enpt_env["PATH"].split(';') if 'OSGEO' not in i])  # actually not needed
        if "PYTHONHOME" in enpt_env.keys():
            del enpt_env["PYTHONHOME"]
        if "PYTHONPATH" in enpt_env.keys():
            del enpt_env["PYTHONPATH"]

        # FIXME is this needed?
        enpt_env['IPYTHONENABLE'] = 'True'
        enpt_env['PROMPT'] = '$P$G'
        enpt_env['PYTHONDONTWRITEBYTECODE'] = '1'
        enpt_env['PYTHONIOENCODING'] = 'UTF-8'
        enpt_env['TEAMCITY_VERSION'] = 'LOCAL'
        enpt_env['O4W_QT_DOC'] = 'C:/OSGEO4~3/apps/Qt5/doc'
        if 'SESSIONNAME' in enpt_env.keys():
            del enpt_env['SESSIONNAME']

        # import pprint
        # s = pprint.pformat(enpt_env)
        # with open('D:\\env.json', 'w') as fp:
        #     fp.write(s)

        return enpt_env

    def processAlgorithm(self, parameters: dict, context: QgsProcessingContext, feedback: QgsProcessingFeedback):
        if not find_spec('enpt'):
            raise ImportError("enpt", "EnPT must be installed into the QGIS Python environment "
                                      "when calling 'EnPTAlgorithm'.")

        # check if the minimal needed EnPT backend version is installed
        # (only works if EnPT is installed in the same environment)
        check_minimal_enpt_version(get_version('enpt'))

        parameters = self._get_preprocessed_parameters(parameters)

        # print parameters and console call to log
        # for key in sorted(parameters):
        #     feedback.pushInfo('{} = {}'.format(key, repr(parameters[key])))
        keyval_str = ' '.join(['--{} {}'.format(key, parameters[key])
                               for key in sorted(parameters)
                               if parameters[key] not in [None, NULL, 'NULL', '']])
        print(parameters)
        print(keyval_str + '\n\n')
        feedback.pushInfo("\nCalling EnPT with the following command:\n"
                          "enpt %s\n\n" % keyval_str)

        # prepare environment for subprocess
        enpt_env = self._prepare_enpt_environment()
        # path_enpt_runscript = self._locate_enpt_run_script()

        # run EnPT in subprocess that activates the EnPT Conda environment
        # feedback.pushDebugInfo('Using %s to start EnPT.' % path_enpt_runscript)
        feedback.pushInfo("The log messages of the EnMAP processing tool are written to the *.log file "
                          "in the specified output folder.")

        exitcode = self._run_cmd(f"enpt {keyval_str}",
                                 qgis_feedback=feedback,
                                 env=enpt_env)

        return self._handle_results(parameters, feedback, exitcode)
