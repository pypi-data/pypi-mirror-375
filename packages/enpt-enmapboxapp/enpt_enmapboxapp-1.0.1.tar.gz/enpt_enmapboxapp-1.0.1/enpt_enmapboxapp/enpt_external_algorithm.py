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

"""This module provides the ExternalEnPTAlgorithm which is used in case EnPT is installed into separate environment."""

import os
from subprocess import check_output, CalledProcessError
from glob import glob
from qgis.core import \
    (QgsProcessingContext,
     QgsProcessingFeedback,
     QgsProcessingParameterFile,
     NULL
     )

from ._enpt_alg_base import _EnPTBaseAlgorithm


class ExternalEnPTAlgorithm(_EnPTBaseAlgorithm):
    # Input parameters
    P_conda_root = 'conda_root'

    def initAlgorithm(self, configuration=None):
        self.addParameter(QgsProcessingParameterFile(
            name=self.P_conda_root,
            description='Conda root directory (which contains the EnPT Python environment in a subdirectory)',
            behavior=QgsProcessingParameterFile.Folder,
            defaultValue=self._get_default_conda_root(),
            optional=True))

        super().initAlgorithm(configuration=configuration)

    @staticmethod
    def _get_default_conda_root():
        if os.getenv('CONDA_ROOT') and os.path.exists(os.getenv('CONDA_ROOT')):
            return os.getenv('CONDA_ROOT')
        elif os.name == 'nt':
            return 'C:\\ProgramData\\Anaconda3'
        else:
            return ''  # FIXME is there a default location in Linux/OSX?

    @staticmethod
    def _locate_EnPT_Conda_environment(user_root):
        conda_rootdir = None

        if user_root and os.path.exists(user_root):
            conda_rootdir = user_root

        elif os.getenv('CONDA_ROOT') and os.path.exists(os.getenv('CONDA_ROOT')):
            conda_rootdir = os.getenv('CONDA_ROOT')

        elif os.getenv('CONDA_EXE') and os.path.exists(os.getenv('CONDA_EXE')):
            p = os.getenv('CONDA_EXE')
            conda_rootdir = os.path.abspath(os.path.join(p, '..', '..'))

        else:
            possPaths = [
                'C:\\ProgramData\\Anaconda3',
                'C:\\Users\\%s\\Anaconda3' % os.getenv('username')
                 ] if os.name == 'nt' else \
                []

            for rootDir in possPaths:
                if os.path.exists(rootDir):
                    conda_rootdir = rootDir

        if not conda_rootdir:
            raise NotADirectoryError("No valid Conda root directory given - "
                                     "neither via the GUI, nor via the 'CONDA_ROOT' environment variable.")

        # set ENPT_PYENV_ACTIVATION environment variable
        os.environ['ENPT_PYENV_ACTIVATION'] = \
            os.path.join(conda_rootdir, 'Scripts', 'activate.bat') if os.name == 'nt' else \
            os.path.join(conda_rootdir, 'bin', 'activate')

        if not os.path.exists(os.getenv('ENPT_PYENV_ACTIVATION')):
            raise FileNotFoundError(os.getenv('ENPT_PYENV_ACTIVATION'))

        return conda_rootdir

    @staticmethod
    def _is_enpt_environment_present(conda_rootdir):
        return os.path.exists(os.path.join(conda_rootdir, 'envs', 'enpt'))

    @staticmethod
    def _locate_enpt_run_script(conda_rootdir=None):
        if conda_rootdir:
            if os.name == 'nt':
                # Windows
                p_exp = os.path.join(conda_rootdir, 'envs', 'enpt', 'Scripts', 'enpt_run_cmd.bat')
            else:
                # Linux / OSX
                p_exp = os.path.join(conda_rootdir, 'envs', 'enpt', 'bin', 'enpt_run_cmd.sh')

            if os.path.isfile(p_exp):
                return p_exp

        try:
            if os.name == 'nt':
                # Windows
                return check_output('where enpt_run_cmd.bat', shell=True).decode('UTF-8').strip()
                # return "D:\\Daten\\Code\\python\\enpt_enmapboxapp\\bin\\enpt_run_cmd.bat"
            else:
                # Linux / OSX
                return check_output('which enpt_run_cmd.sh', shell=True).decode('UTF-8').strip()
                # return 'enpt_run_cmd.sh '

        except CalledProcessError:
            raise EnvironmentError('The EnPT run script could not be found. Please make sure, that enpt_enmapboxapp '
                                   'is correctly installed into your QGIS Python environment.')

    @staticmethod
    def _prepare_enpt_environment() -> dict:
        os.environ['PYTHONUNBUFFERED'] = '1'
        os.environ['IS_ENPT_GUI_CALL'] = '1'

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
        conda_root = self._locate_EnPT_Conda_environment(parameters[self.P_conda_root])
        feedback.pushInfo('Found Conda installation at %s.' % conda_root)

        if self._is_enpt_environment_present(conda_root):
            feedback.pushInfo("The Conda installation contains the 'enpt' environment as expected.")
        else:
            envs = list(sorted([i.split(os.sep)[-2] for i in glob(os.path.join(conda_root, 'envs', '*') + os.sep)]))
            feedback.reportError(
                "The Conda installation has no environment called 'enpt'. Existing environments are named %s. Please "
                "follow the EnPT installation instructions to install the EnMAP processing tool backend code "
                "(see https://enmap.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/EnPT/doc/installation.html). "
                "This is needed to run EnPT from this GUI." % ', '.join(envs)
            )
            return {
                'success': False,
                self.P_OUTPUT_RASTER: '',
                # self.P_OUTPUT_VECTOR: parameters[self.P_OUTPUT_RASTER],
                # self.P_OUTPUT_FILE: parameters[self.P_OUTPUT_RASTER],
                self.P_OUTPUT_FOLDER: ''
            }

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
        path_enpt_runscript = self._locate_enpt_run_script(conda_root)
        print('RUNSCRIPT: ' + path_enpt_runscript)

        # run EnPT in subprocess that activates the EnPT Conda environment
        feedback.pushDebugInfo('Using %s to start EnPT.' % path_enpt_runscript)
        feedback.pushInfo("The log messages of the EnMAP processing tool are written to the *.log file "
                          "in the specified output folder.")

        exitcode = self._run_cmd(f"{path_enpt_runscript} {keyval_str}",
                                 qgis_feedback=feedback,
                                 env=enpt_env)

        return self._handle_results(parameters, feedback, exitcode)
