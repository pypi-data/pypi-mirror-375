# **************************************************************************
# *
# * Authors:  Verónica Gamo
# *		        Daniel Del Hoyo (ddelhoyo@cnb.csic.es)
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 3 of the License, or
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

from pyworkflow.tests import BaseTest, DataSet, setupTestProject

from pwchem.utils import assertHandle
from pwchem.protocols import ProtChemImportSmallMolecules

from retrosynthesis.protocols import ProtChemAiZynthFinder

class TestImportBase(BaseTest):
	@classmethod
	def setUpClass(cls):
		cls.dsLig = DataSet.getDataSet("smallMolecules")
		setupTestProject(cls)

		cls._runImportSmallMols()
		cls._waitOutput(cls.protImportSmallMols, 'outputSmallMolecules', sleepTime=5)

	@classmethod
	def _runImportSmallMols(cls):
		cls.protImportSmallMols = cls.newProtocol(
			ProtChemImportSmallMolecules,
			filesPath=cls.dsLig.getFile('sdf'))
		cls.proj.launchProtocol(cls.protImportSmallMols, wait=False)

class TestRetrosynthesis(TestImportBase):
	@classmethod
	def _runAizynthfinder(cls, inProt):
		protaizynth = cls.newProtocol(
			ProtChemAiZynthFinder,
			inputLigand='SmallMolecule (2000 molecule)'
		)
		protaizynth.inputSet.set(inProt)
		protaizynth.inputSet.setExtended('outputSmallMolecules')

		cls.proj.launchProtocol(protaizynth, wait=False)
		return protaizynth

	def test(self):
		p = self._runAizynthfinder(inProt=self.protImportSmallMols)
		self._waitOutput(p, 'outputSmallMolecules', sleepTime=10)
		assertHandle(self.assertIsNotNone, getattr(p, 'outputSmallMolecules', None), cwd=p.getWorkingDir())


