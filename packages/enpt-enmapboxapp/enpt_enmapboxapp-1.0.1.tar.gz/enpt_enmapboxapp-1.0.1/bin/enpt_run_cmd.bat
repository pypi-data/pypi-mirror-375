:: enpt_enmapboxapp, A QGIS EnMAPBox plugin providing a GUI for the EnMAP processing tools (EnPT)
::
:: Copyright (C) 2018–2025 Daniel Scheffler (GFZ Potsdam, daniel.scheffler@gfz.de)
::
:: This software was developed within the context of the EnMAP project supported
:: by the DLR Space Administration with funds of the German Federal Ministry of
:: Economic Affairs and Energy (on the basis of a decision by the German Bundestag:
:: 50 EE 1529) and contributions from DLR, GFZ and OHB System AG.
::
:: This program is free software: you can redistribute it and/or modify it under
:: the terms of the GNU Lesser General Public License as published by the Free
:: Software Foundation, either version 3 of the License, or (at your option) any
:: later version.
::
:: This program is distributed in the hope that it will be useful, but WITHOUT
:: ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
:: FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
:: details.
::
:: You should have received a copy of the GNU Lesser General Public License along
:: with this program. If not, see <https://www.gnu.org/licenses/>.

@echo off

:: activate the EnPT Conda environment located at %ENPT_PYENV_ACTIVATION%
:: echo %PATH%
call %ENPT_PYENV_ACTIVATION% enpt
:: echo %PATH%

:: check the path from where Python is loaded
:: where python

:: check if the enpt package is available
:: python -c "import enpt; print(enpt)"

:: print the user provided EnPT arguments
:: echo %*

:: Look for the enpt executable
FOR /F %%i IN ('where enpt') do (
    SET PATH_ENPT_CLI=%%i
)

:: Check if enpt executable was found
IF NOT DEFINED PATH_ENPT_CLI (
    echo ERROR: The enpt executable could not be found in the enpt conda environment. Please make sure the enpt package is properly installed, see https://enmap.git-pages.gfz-potsdam.de/GFZ_Tools_EnMAP_BOX/EnPT/doc/installation.html for details.
    exit /b 1
)

:: run enpt/cli.py with the provided arguments
echo.
echo _______________________________________
%PATH_ENPT_CLI% %*
echo _______________________________________
echo.
