# **************************************************************************
# *
# * Authors: Martín Salinas (martin.salinas@cnb.csic.es)
# *
# * Biocomputing Unit, CNB-CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

# Scipion em imports
import os, subprocess
from subprocess import run
from scipion.install.funcs import InstallHelper

# Scipion chem imports
import pwchem

# Plugin imports
from .constants import PLUGIN_VERSION, AIZYNTHFINDER_DIC

_version_ = PLUGIN_VERSION
_logo = ""
_references = ['']

class Plugin(pwchem.Plugin):
	@classmethod
	def _defineVariables(cls):
		""" Return and write a variable in the config file. """
		cls._defineEmVar(AIZYNTHFINDER_DIC['home'], '{}-{}'.format(AIZYNTHFINDER_DIC['name'], AIZYNTHFINDER_DIC['version']))

	@classmethod
	def defineBinaries(cls, env):
		""" Install the necessary packages. """
		cls.addAizynthfinder(env)

	@classmethod
	def getHome(cls):
		return cls.getVar(AIZYNTHFINDER_DIC['home'])

	########################### PACKAGE FUNCTIONS ###########################
	@classmethod
	def addAizynthfinder(cls, env, default=True):
		""" This function installs Aizynthfinder's package. """
		# Instantiating install helper
		installer = InstallHelper(AIZYNTHFINDER_DIC['name'], packageHome=cls.getVar(AIZYNTHFINDER_DIC['home']), packageVersion=AIZYNTHFINDER_DIC['version'])

	
		# Installing package
		installer.getCondaEnvCommand(pythonVersion='3.9', binaryName=AIZYNTHFINDER_DIC['name'], binaryVersion=AIZYNTHFINDER_DIC['version']) \
		.addCommand(f'{cls.getEnvActivationCommand(AIZYNTHFINDER_DIC)} && python -m pip install aizynthfinder[all] && download_public_data .')\
		.addPackage(env, dependencies=['conda'], default=default)



	@classmethod
	def runAIZYNTH(cls, program, args, cwd=None):
		""" Run AIZYNTH command from a given protocol. """
		full_program = '%s && %s ' % (cls.getEnvActivationCommand(AIZYNTHFINDER_DIC), program)
		run(full_program + args, env=cls.getEnviron(), cwd=cwd, shell=True)

	@classmethod
	def getPluginH(cls, path=""):
		import retrosynthesis
		fnDir = os.path.split(retrosynthesis.__file__)[0]
		return os.path.join(fnDir, path)
	
	@classmethod
	def getScriptsPath(cls):
		return cls.getPluginH('scripts/')



	
