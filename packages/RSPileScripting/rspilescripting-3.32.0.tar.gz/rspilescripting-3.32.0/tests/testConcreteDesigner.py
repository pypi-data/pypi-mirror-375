import unittest
from RSPileScripting.RSPileModeler import RSPileModeler
from RSPileScripting.enums import *
from enum import Enum

from dotenv import load_dotenv
import shutil
import os

class TestPileProperties(unittest.TestCase):
	load_dotenv()
	port = 60044
	exe_path = os.getenv("PATH_TO_RSPILE_CPP_REPO") + "\\Build\\Debug_x64\\RSPile.exe"
	test_file = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\TestProject.rspile2"

	@classmethod
	def setUpClass(cls):
		RSPileModeler.startApplication(overridePathToExecutable=cls.exe_path, port=cls.port)
		cls.modeler = RSPileModeler(cls.port)

	@classmethod
	def tearDownClass(cls):
		cls.modeler.closeApplication()

	def setUp(self):
		self.copy_file = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\copyTestProject.rspile2"
		shutil.copy(self.test_file, self.copy_file)
	
		self.model = self.modeler.openFile(self.copy_file)
		self.pileSection = self.model.getPileSections()[0]
		self.prestressedConcreteDesigner = self.pileSection.PileAnalysis.PrestressedConcrete.CrossSection.ConcreteDesigner
		self.reinforcedConcreteDesigner = self.pileSection.PileAnalysis.ReinforcedConcrete.CrossSection.ConcreteDesigner

	def tearDown(self):
		self.model.close()

		if os.path.exists(self.copy_file):
			os.remove(self.copy_file)

		copy_file_dir = os.path.dirname(self.copy_file) + "\\copyTestProject"
		copy_file_dir
		if os.path.exists(copy_file_dir):
			try:
				shutil.rmtree(copy_file_dir)
			except Exception:
				print(f"Failed to remove directory: {copy_file_dir}")

	#region Core Props
	def testCoreProps(self):
		self.prestressedConcreteDesigner.Core.setUseCore(True)
		self.assertEqual(self.prestressedConcreteDesigner.Core.getUseCore(), True)

		self.prestressedConcreteDesigner.Core.setUseCore(False)
		self.assertEqual(self.prestressedConcreteDesigner.Core.getUseCore(), False)

		self.prestressedConcreteDesigner.Core.setCoreDiameter(1.1)
		self.assertEqual(self.prestressedConcreteDesigner.Core.getCoreDiameter(), 1.1)

		self.prestressedConcreteDesigner.Core.setWallThickness(1.2)
		self.assertEqual(self.prestressedConcreteDesigner.Core.getWallThickness(), 1.2)

		self.prestressedConcreteDesigner.Core.setIsFilledCore(True)
		self.assertEqual(self.prestressedConcreteDesigner.Core.getIsFilledCore(), True)

		self.prestressedConcreteDesigner.Core.setIsFilledCore(False)
		self.assertEqual(self.prestressedConcreteDesigner.Core.getIsFilledCore(), False)

		self.prestressedConcreteDesigner.Core.setYieldStress(310.2)
		self.assertEqual(self.prestressedConcreteDesigner.Core.getYieldStress(), 310.2)

		self.prestressedConcreteDesigner.Core.setElasticModulus(200000.3)
		self.assertEqual(self.prestressedConcreteDesigner.Core.getElasticModulus(), 200000.3)
	#endregion

	#region Casing Props
	def testCasingProps(self):
		self.prestressedConcreteDesigner.Casing.setUseCasing(True)
		self.assertEqual(self.prestressedConcreteDesigner.Casing.getUseCasing(), True)

		self.prestressedConcreteDesigner.Casing.setUseCasing(False)
		self.assertEqual(self.prestressedConcreteDesigner.Casing.getUseCasing(), False)

		self.prestressedConcreteDesigner.Casing.setYieldStress(301.4)
		self.assertEqual(self.prestressedConcreteDesigner.Casing.getYieldStress(), 301.4)

		self.prestressedConcreteDesigner.Casing.setElasticModulus(200000.6)
		self.assertEqual(self.prestressedConcreteDesigner.Casing.getElasticModulus(), 200000.6)

		self.prestressedConcreteDesigner.Casing.setCasingThickness(1.2)
		self.assertEqual(self.prestressedConcreteDesigner.Casing.getCasingThickness(), 1.2)
	#endregion

	#region IBeam Props
	def testIBeamProps(self):
		# test when no ibeam has been set 
		self.assertIsNone(self.reinforcedConcreteDesigner.IBeam.getIBeamType())

		# test setting an ibeam type that doesn't exist
		class TEST_ENUM(Enum):
			INVALID_IBEAM_TYPE = "InvalidIBeamType"

		with self.assertRaises(ValueError):
			self.reinforcedConcreteDesigner.IBeam.setIBeamType(TEST_ENUM.INVALID_IBEAM_TYPE)

		self.reinforcedConcreteDesigner.IBeam.setUseIBeam(True)
		self.assertEqual(self.reinforcedConcreteDesigner.IBeam.getUseIBeam(), True)

		self.reinforcedConcreteDesigner.IBeam.setUseIBeam(False)
		self.assertEqual(self.reinforcedConcreteDesigner.IBeam.getUseIBeam(), False)

		self.reinforcedConcreteDesigner.IBeam.setYieldStress(381.6)
		self.assertEqual(self.reinforcedConcreteDesigner.IBeam.getYieldStress(), 381.6)

		self.reinforcedConcreteDesigner.IBeam.setElasticModulus(200001.8)
		self.assertEqual(self.reinforcedConcreteDesigner.IBeam.getElasticModulus(), 200001.8)

		for iBeamType in AmericanIBeamTypes:
			self.reinforcedConcreteDesigner.IBeam.setIBeamType(iBeamType)
			self.assertEqual(self.reinforcedConcreteDesigner.IBeam.getIBeamType(), iBeamType)
		for iBeamType in CanadianIBeamTypes:
			self.reinforcedConcreteDesigner.IBeam.setIBeamType(iBeamType)
			self.assertEqual(self.reinforcedConcreteDesigner.IBeam.getIBeamType(), iBeamType)
	#endregion

	#region Reinforcement Props
	def testPrestressedReinforcementProps(self):

		self.prestressedConcreteDesigner.Reinforcement.setForceBeforeLosses(150.2)
		self.assertEqual(self.prestressedConcreteDesigner.Reinforcement.getForceBeforeLosses(), 150.2)

		self.prestressedConcreteDesigner.Reinforcement.setFractionOfLoss(0.5)
		self.assertEqual(self.prestressedConcreteDesigner.Reinforcement.getFractionOfLoss(), 0.5)

		self.prestressedConcreteDesigner.Reinforcement.addReinforcementPattern("TestPattern")
		pattern = self.prestressedConcreteDesigner.Reinforcement.getReinforcementPatterns()[0]
		pattern.getName()
		self.assertEqual(pattern.getName(), "TestPattern")

		pattern.setName("123Hello456!")
		self.assertEqual(pattern.getName(), "123Hello456!")

		for size in StrandSize:
			pattern.setStrandSize(size)
			self.assertEqual(pattern.getStrandSize(), size)

		for type in StrandType:
			pattern.setStrandType(type)
			self.assertEqual(pattern.getStrandType(), type)

		pattern.setUseBundledBars(False)
		self.assertEqual(pattern.getUseBundledBars(), False)

		pattern.setUseBundledBars(True)
		self.assertEqual(pattern.getUseBundledBars(), True)

		pattern.setNumberOfBundledBars(5)
		self.assertEqual(pattern.getNumberOfBundledBars(), 5)

		for type in ReinforcementPatternType:
			pattern.setReinforcementPatternType(type)
			self.assertEqual(pattern.getReinforcementPatternType(), type)

		#Radial Props
		pattern.Radial.setNumberOfBars(8)
		self.assertEqual(pattern.Radial.getNumberOfBars(), 8)

		pattern.Radial.setAngleFromXAxis(45.0)
		self.assertEqual(pattern.Radial.getAngleFromXAxis(), 45.0)

		for refpoint in RebarReferencePointMethod:
			pattern.Radial.setRebarLocationRefPoint(refpoint)
			self.assertEqual(pattern.Radial.getRebarLocationRefPoint(), refpoint)

		# set invalid rebar ref point
		with self.assertRaises(ValueError):
			pattern.Radial.setRebarLocationRefPoint("InvalidRefPoint")

		pattern.Radial.setCoverDepth(44)
		self.assertEqual(pattern.Radial.getCoverDepth(), 44)

		pattern.Radial.setDistanceFromCenter(55)
		self.assertEqual(pattern.Radial.getDistanceFromCenter(), 55)

		#Rectangle Props
		pattern.Rectangle.setIsPeripheralBars(True)
		self.assertEqual(pattern.Rectangle.getIsPeripheralBars(), True)

		pattern.Rectangle.setIsPeripheralBars(False)
		self.assertEqual(pattern.Rectangle.getIsPeripheralBars(), False)

		pattern.Rectangle.setNumberOfBarsX(9)
		self.assertEqual(pattern.Rectangle.getNumberOfBarsX(), 9)

		pattern.Rectangle.setNumberOfBarsY(10)
		self.assertEqual(pattern.Rectangle.getNumberOfBarsY(), 10)

		pattern.Rectangle.setMinCoverDepth(37)
		self.assertEqual(pattern.Rectangle.getMinCoverDepth(), 37)

		#Custom Props
		pattern.Custom.setCustomLocations([(1,2), (3,4)])
		self.assertEqual(pattern.Custom.getCustomLocations(), [(1,2), (3,4)])

		pattern.Custom.setCustomLocations([(5,6), (7,8)])
		self.assertEqual(pattern.Custom.getCustomLocations(), [(5,6), (7,8)])

		numberOfPatterns = len(self.prestressedConcreteDesigner.Reinforcement.getReinforcementPatterns())
		self.prestressedConcreteDesigner.Reinforcement.removeReinforcementPattern("123Hello456!")

		numberOfPatternsAfterRemoval = len(self.prestressedConcreteDesigner.Reinforcement.getReinforcementPatterns())
		self.assertEqual(numberOfPatternsAfterRemoval, numberOfPatterns - 1)

	def testReinforcedConcreteReinforcementProps(self):
		self.reinforcedConcreteDesigner.Reinforcement.addReinforcementPattern("TestPattern")
		pattern = self.reinforcedConcreteDesigner.Reinforcement.getReinforcementPatterns()[0]

		pattern.setName("Test Pattern 2")
		self.assertEqual(pattern.getName(), "Test Pattern 2")

		for size in RebarSize:
			pattern.setRebarSize(size)
			self.assertEqual(pattern.getRebarSize(), size)
		
		for patternType in ReinforcementPatternType:
			pattern.setReinforcementPatternType(patternType)
			self.assertEqual(pattern.getReinforcementPatternType(), patternType)

		pattern.setUseBundledBars(False)
		self.assertEqual(pattern.getUseBundledBars(), False)

		pattern.setUseBundledBars(True)
		self.assertEqual(pattern.getUseBundledBars(), True)

		pattern.setNumberOfBundledBars(4)
		self.assertEqual(pattern.getNumberOfBundledBars(), 4)

		pattern.setRebarYieldStress(350.2)
		self.assertEqual(pattern.getRebarYieldStress(), 350.2)

		pattern.setRebarElasticModulus(5000.1)
		self.assertEqual(pattern.getRebarElasticModulus(), 5000.1)

		#Radial Props
		pattern.Radial.setNumberOfBars(3)
		self.assertEqual(pattern.Radial.getNumberOfBars(), 3)

		pattern.Radial.setAngleFromXAxis(46.0)
		self.assertEqual(pattern.Radial.getAngleFromXAxis(), 46.0)

		for refpoint in RebarReferencePointMethod:
			pattern.Radial.setRebarLocationRefPoint(refpoint)
			self.assertEqual(pattern.Radial.getRebarLocationRefPoint(), refpoint)

		pattern.Radial.setCoverDepth(45)
		self.assertEqual(pattern.Radial.getCoverDepth(), 45)

		pattern.Radial.setDistanceFromCenter(56)
		self.assertEqual(pattern.Radial.getDistanceFromCenter(), 56)

		#Rectangle Props
		pattern.Rectangle.setIsPeripheralBars(True)
		self.assertEqual(pattern.Rectangle.getIsPeripheralBars(), True)

		pattern.Rectangle.setIsPeripheralBars(False)
		self.assertEqual(pattern.Rectangle.getIsPeripheralBars(), False)

		pattern.Rectangle.setNumberOfBarsX(3)
		self.assertEqual(pattern.Rectangle.getNumberOfBarsX(), 3)

		pattern.Rectangle.setNumberOfBarsY(4)
		self.assertEqual(pattern.Rectangle.getNumberOfBarsY(), 4)

		pattern.Rectangle.setMinCoverDepth(38)
		self.assertEqual(pattern.Rectangle.getMinCoverDepth(), 38)

		#Custom Props
		pattern.Custom.setCustomLocations([(2,3), (4,5)])
		self.assertEqual(pattern.Custom.getCustomLocations(), [(2,3), (4,5)])

		pattern.Custom.setCustomLocations([(6,7), (8,9)])
		self.assertEqual(pattern.Custom.getCustomLocations(), [(6,7), (8,9)])

		numberOfPatterns = len(self.reinforcedConcreteDesigner.Reinforcement.getReinforcementPatterns())
		self.reinforcedConcreteDesigner.Reinforcement.removeReinforcementPattern("Test Pattern 2")

		numberOfPatternsAfterRemoval = len(self.reinforcedConcreteDesigner.Reinforcement.getReinforcementPatterns())
		self.assertEqual(numberOfPatternsAfterRemoval, numberOfPatterns - 1)
		
if __name__ == '__main__':

	unittest.main(verbosity=2)