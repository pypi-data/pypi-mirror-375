import unittest
from RSPileScripting.RSPileModeler import RSPileModeler
from RSPileScripting.enums import *
from RSPileScripting.Utilities.ColorPicker import ColorPicker
from math import sqrt
import grpc

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
		self.pileType = self.model.getPileTypes()[0]

	def tearDown(self):
		self.model.close()

		if os.path.exists(self.copy_file):
			os.remove(self.copy_file)

		copy_file_dir = os.path.dirname(self.copy_file) + "\\copyTestProject"

		if os.path.exists(copy_file_dir):
			try:
				shutil.rmtree(copy_file_dir)
			except Exception:
				print(f"Failed to remove directory: {copy_file_dir}")

	#region test Pile Type
	def testGenericPileType(self):
		self.pileType.setName("Test Name 1234")
		self.assertEqual(self.pileType.getName(), "Test Name 1234")

		self.pileType.setColor(ColorPicker.Bright_Green)
		self.assertEqual(self.pileType.getColor(), ColorPicker.Bright_Green)

		self.pileType.setColor(ColorPicker.getColorFromRGB(51,53,52))
		self.assertEqual(self.pileType.getColor(), ColorPicker.getColorFromRGB(51,53,52))

	#region test Pile Type Sections
	def testPileAnalysisPileTypeSections(self):
		for section in PileAnalysisPileTypeCrossSection:
			self.pileType.PileAnalysis.Sections.setCrossSectionType(section)
			self.assertEqual(self.pileType.PileAnalysis.Sections.getCrossSectionType(), section)

		self.pileType.PileAnalysis.Sections.setCrossSectionType(PileAnalysisPileTypeCrossSection.UNIFORM) #setting back to uniform as input below doesn't have a bell

		self.pileType.PileAnalysis.Sections.setPileSegmentsByLength(1.5, [["Pile Section 1", 20], ["Pile Section 2", 5], ["Pile Section 4", 3]])
		self.assertEqual(self.pileType.PileAnalysis.Sections.getPileSegmentsByLength(), (1.5, [["Pile Section 1", 20], ["Pile Section 2", 5], ["Pile Section 4", 3]]))

		#test negative pile segment lengths
		with self.assertRaises(grpc.RpcError):
			self.pileType.PileAnalysis.Sections.setPileSegmentsByLength(1.5, [["Pile Section 1", -20], ["Pile Section 2", -5], ["Pile Section 4", -3]])

		self.pileType.PileAnalysis.Sections.setPileSegmentsByBottomElevation(1.5, [["Pile Section 1", -5], ["Pile Section 2", -10], ["Pile Section 4", -20]])
		self.assertEqual(self.pileType.PileAnalysis.Sections.getPileSegmentsByBottomElevation(), (1.5, [["Pile Section 1", -5], ["Pile Section 2", -10], ["Pile Section 4", -20]]))

		#test pile segment elevations that have lower elevation higher than upper elevation
		with self.assertRaises(grpc.RpcError):
			self.pileType.PileAnalysis.Sections.setPileSegmentsByBottomElevation(1.5, [["Pile Section 1", -10], ["Pile Section 2", 10], ["Pile Section 4", 5]])

		#need to set pile type to known length and diameter to ensure setting a valid taper angle
		self.pileType.PileAnalysis.Sections.setCrossSectionType(PileAnalysisPileTypeCrossSection.TAPERED)

		self.pileSection.setName("Tapered Pile Property")
		self.pileSection.PileAnalysis.Elastic.CrossSection.Circular.setDiameter(5)
	
		self.pileType.PileAnalysis.Sections.setPileSegmentsByLength(1.5, [["Tapered Pile Property", 15]])

		self.pileType.PileAnalysis.Sections.setTaperAngle(9)
		self.assertEqual(self.pileType.PileAnalysis.Sections.getTaperAngle(), 9)

		#test incorrect taper angle
		with self.assertRaises(grpc.RpcError):
			self.pileType.PileAnalysis.Sections.setTaperAngle(10)

		#test incorrect taper angle
		with self.assertRaises(grpc.RpcError):
			self.pileType.PileAnalysis.Sections.setTaperAngle(-7)

		#test setting taper while the cross section type is not tapered
		with self.assertRaises(grpc.RpcError):
			self.pileType.PileAnalysis.Sections.setCrossSectionType(PileAnalysisPileTypeCrossSection.UNIFORM)
			self.pileType.PileAnalysis.Sections.setTaperAngle(80)
	#end region

	#region test Driven Pile Type Sections
	def testDrivenPileTypeSections(self):
		for section in DrivenPileTypeCrossSection:
			self.pileType.Driven.Sections.setCrossSectionType(section)
			self.assertEqual(self.pileType.Driven.Sections.getCrossSectionType(), section)

		self.pileType.Driven.Sections.setCrossSectionType(DrivenPileTypeCrossSection.UNIFORM) #setting back to uniform as input below doesn't have a bell

		self.pileType.Driven.Sections.setPileSegmentsByLength(1.5, [["Pile Section 1", 2], ["Pile Section 2", 9], ["Pile Section 4", 12]])
		self.assertEqual(self.pileType.Driven.Sections.getPileSegmentsByLength(), (1.5, [["Pile Section 1", 2], ["Pile Section 2", 9], ["Pile Section 4", 12]]))

		#test negative pile segment lengths
		with self.assertRaises(grpc.RpcError):
			self.pileType.Driven.Sections.setPileSegmentsByLength(3, [["Pile Section 1", -20], ["Pile Section 2", -5], ["Pile Section 4", -3]])

		self.pileType.Driven.Sections.setPileSegmentsByBottomElevation(4, [["Pile Section 1", -5], ["Pile Section 2", -10], ["Pile Section 4", -20]])
		self.assertEqual(self.pileType.Driven.Sections.getPileSegmentsByBottomElevation(), (4, [["Pile Section 1", -5], ["Pile Section 2", -10], ["Pile Section 4", -20]]))

		#test pile segment elevations that have lower elevation higher than upper elevation
		with self.assertRaises(grpc.RpcError):
			self.pileType.Driven.Sections.setPileSegmentsByBottomElevation(1.3, [["Pile Section 1", -10], ["Pile Section 2", 10], ["Pile Section 4", 5]])

		#need to set pile type to known length and diameter to ensure setting a valid taper angle
		self.pileType.Driven.Sections.setCrossSectionType(DrivenPileTypeCrossSection.TAPERED)

		self.pileSection.setName("Tapered Pile Property")
		self.pileSection.DrivenCapacity.Concrete.setSideOfSquareSection(5)
	
		self.pileType.Driven.Sections.setPileSegmentsByLength(1.5, [["Tapered Pile Property", 20]])

		self.pileType.Driven.Sections.setTaperAngle(0.8)
		self.assertEqual(self.pileType.Driven.Sections.getTaperAngle(), 0.8)

		#test incorrect taper angle
		with self.assertRaises(grpc.RpcError):
			self.pileType.Driven.Sections.setTaperAngle(8)

		#test incorrect taper angle
		with self.assertRaises(grpc.RpcError):
			self.pileType.Driven.Sections.setTaperAngle(-7)

		#test setting taper while the cross section type is not tapered
		with self.assertRaises(grpc.RpcError):
			self.pileType.Driven.Sections.setCrossSectionType(DrivenPileTypeCrossSection.UNIFORM)
			self.pileType.Driven.Sections.setTaperAngle(80)
	#end region


	#region test Bored Pile Type Sections
	def testBoredPileTypeSections(self):
		for section in BoredPileTypeCrossSection:
			self.pileType.Bored.Sections.setCrossSectionType(section)
			self.assertEqual(self.pileType.Bored.Sections.getCrossSectionType(), section)

		self.pileType.Bored.Sections.setCrossSectionType(BoredPileTypeCrossSection.UNIFORM) #setting back to uniform as input below doesn't have a bell

		self.pileType.Bored.Sections.setPileSegmentsByLength(3.2, [["Pile Section 1", 5], ["Pile Section 2", 3], ["Pile Section 4", 11]])
		self.assertEqual(self.pileType.Bored.Sections.getPileSegmentsByLength(), (3.2, [["Pile Section 1", 5], ["Pile Section 2", 3], ["Pile Section 4", 11]]))

		#test negative pile segment lengths
		with self.assertRaises(grpc.RpcError):
			self.pileType.Bored.Sections.setPileSegmentsByLength(6, [["Pile Section 1", -20], ["Pile Section 2", -5], ["Pile Section 4", -3]])

		self.pileType.Bored.Sections.setPileSegmentsByBottomElevation(2.5, [["Pile Section 1", -5], ["Pile Section 2", -10], ["Pile Section 4", -20]])
		self.assertEqual(self.pileType.Bored.Sections.getPileSegmentsByBottomElevation(), (2.5, [["Pile Section 1", -5], ["Pile Section 2", -10], ["Pile Section 4", -20]]))

		#test pile segment elevations that have lower elevation higher than upper elevation
		with self.assertRaises(grpc.RpcError):
			self.pileType.Bored.Sections.setPileSegmentsByBottomElevation(2.5, [["Pile Section 1", -10], ["Pile Section 2", 10], ["Pile Section 4", 5]])
	#end region

	#region test Pile Type Sections Bell
	def testPileTypeSectionsBell(self):
		self.pileType.PileAnalysis.Sections.setCrossSectionType(PileAnalysisPileTypeCrossSection.BELL)

		self.pileType.PileAnalysis.Sections.Bell.setLengthAboveBell(22)
		self.assertEqual(self.pileType.PileAnalysis.Sections.Bell.getLengthAboveBell(), 22)

		#test incorrect length above bell
		with self.assertRaises(grpc.RpcError):
			self.pileType.PileAnalysis.Sections.Bell.setLengthAboveBell(-22)

		self.pileType.PileAnalysis.Sections.Bell.setAngle(88)
		self.assertEqual(self.pileType.PileAnalysis.Sections.Bell.getAngle(), 88)

		#test incorrect bell angle
		with self.assertRaises(grpc.RpcError):
			self.pileType.PileAnalysis.Sections.Bell.setAngle(91)

		self.pileType.PileAnalysis.Sections.Bell.setBaseThickness(11)
		self.assertEqual(self.pileType.PileAnalysis.Sections.Bell.getBaseThickness(), 11)

		#test incorrect base thickness
		with self.assertRaises(grpc.RpcError):
			self.pileType.PileAnalysis.Sections.Bell.setBaseThickness(-1)

		for bell in BaseDiamaterDefinitionType:
			self.pileType.PileAnalysis.Sections.Bell.setBaseDiameterDefinitionType(bell)
			self.assertEqual(self.pileType.PileAnalysis.Sections.Bell.getBaseDiameterDefinitionType(), bell)

		self.pileType.PileAnalysis.Sections.Bell.setBaseFactor(1.8)
		self.assertEqual(self.pileType.PileAnalysis.Sections.Bell.getBaseFactor(), 1.8)

		#test incorrect base factor
		with self.assertRaises(grpc.RpcError):
			self.pileType.PileAnalysis.Sections.Bell.setBaseFactor(0)

		#bell base diamater depends on diameter of section above so need to set known values
		self.pileType.PileAnalysis.Sections.setCrossSectionType(PileAnalysisPileTypeCrossSection.UNIFORM)
		self.pileSection.PileAnalysis.Elastic.CrossSection.Circular.setDiameter(3.8)
		self.pileSection.setName("Pile Section for Bell Test")
		self.pileType.PileAnalysis.Sections.setPileSegmentsByLength(0, [("Pile Section for Bell Test", 20)])

		self.pileType.PileAnalysis.Sections.setCrossSectionType(PileAnalysisPileTypeCrossSection.BELL)
		self.pileType.PileAnalysis.Sections.Bell.setBaseDiameter(5)
		self.assertEqual(self.pileType.PileAnalysis.Sections.Bell.getBaseDiameter(), 5)

		#test incorrect base diameter
		with self.assertRaises(grpc.RpcError):
			self.pileType.PileAnalysis.Sections.Bell.setBaseDiameter(3.5)
	#endregion

	#region test Pile Type Orientation 
	def testPileTypeOrientation(self):
		for orientation in OrientationType:
			self.pileType.PileAnalysis.Orientation.setOrientationType(orientation)
			self.assertEqual(self.pileType.PileAnalysis.Orientation.getOrientationType(), orientation)

		self.pileType.PileAnalysis.Orientation.setRotationAngle(43.7)
		self.assertEqual(self.pileType.PileAnalysis.Orientation.getRotationAngle(), 43.7)
	#end region		

	#test Pile Type Orientation Alpha Beta 
	def testPileTypeAlphaBeta(self):
		self.pileType.PileAnalysis.Orientation.AlphaBeta.setAlphaAngle(45.7)
		self.assertEqual(self.pileType.PileAnalysis.Orientation.AlphaBeta.getAlphaAngle(), 45.7)

		self.pileType.PileAnalysis.Orientation.AlphaBeta.setBetaAngle(45.7)
		self.assertEqual(self.pileType.PileAnalysis.Orientation.AlphaBeta.getBetaAngle(), 45.7)
	#end region

	#region test Pile Type Orientation Vector 
	def testPileTypeVector(self):
		vector = [0.5, 0.5, -0.707]
		magnitude = sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
		unitVector = [vector[0]/magnitude, vector[1]/magnitude, vector[2]/magnitude]

		self.pileType.PileAnalysis.Orientation.Vector.setVector(vector)
		result = self.pileType.PileAnalysis.Orientation.Vector.getVector()

		magnitude = sqrt(vector[0]**2 + vector[1]**2 + vector[2]**2)
		self.assertEqual(len(result), 3)
		self.assertAlmostEqual(result[0], unitVector[0])
		self.assertAlmostEqual(result[1], unitVector[1])
		self.assertAlmostEqual(result[2], unitVector[2])

		#test invalid vector
		with self.assertRaises(grpc.RpcError):
			self.pileType.PileAnalysis.Orientation.Vector.setVector([5, 5, 10])
	#end region

	#region test Helical Piles
	def testHelicalPiles(self):
		#Helical Sections
		self.pileType.Helical.Sections.setPileSegmentsByLength(1.9, [["Pile Section 2", 11], ["Pile Section 1", 12], ["Pile Section 4", 13]])
		self.assertEqual(self.pileType.Helical.Sections.getPileSegmentsByLength(), (1.9, [["Pile Section 2", 11], ["Pile Section 1", 12], ["Pile Section 4", 13]]))

		self.pileType.Helical.Sections.setPileSegmentsByBottomElevation(2.1, [["Pile Section 1", -6], ["Pile Section 2", -8], ["Pile Section 4", -21]])
		self.assertEqual(self.pileType.Helical.Sections.getPileSegmentsByBottomElevation(), (2.1, [["Pile Section 1", -6], ["Pile Section 2", -8], ["Pile Section 4", -21]]))

		#test cross section types
		self.pileType.Helical.Sections.setCrossSectionType(HelicalPileTypeCrossSection.UNIFORM)
		self.assertEqual(self.pileType.Helical.Sections.getCrossSectionType(), HelicalPileTypeCrossSection.UNIFORM)
		
		#Helices
		self.pileType.Helical.Sections.Helices.setHeightReductionFactor(2.78)
		self.assertEqual(self.pileType.Helical.Sections.Helices.getHeightReductionFactor(), 2.78)

		self.pileType.Helical.Sections.Helices.setHelicesByDepth([[0.8, 0.07, 3], [1.0, 0.08, 4.1], [1.1, 0.1, 5]])
		self.assertEqual(self.pileType.Helical.Sections.Helices.getHelicesByDepth(), [[0.8, 0.07, 3], [1.0, 0.08, 4.1], [1.1, 0.1, 5]])

		self.pileType.Helical.Sections.Helices.setHelicesBySpacing(6, [0.8, 0.05], [[0.7, 0.06, 2], [0.9, 0.07, 2.1], [1.0, 0.09, 2.2]])
		self.assertEqual(self.pileType.Helical.Sections.Helices.getHelicesBySpacing(), (6, [[0.8, 0.05, 0], [0.7, 0.06, 2], [0.9, 0.07, 2.1], [1.0, 0.09, 2.2]]))

		#Add helix with depth less than previous helix
		with self.assertRaises(grpc.RpcError):
			self.pileType.Helical.Sections.Helices.setHelicesByDepth([[0.7, 0.01, 2], [0.9, 0.02, 1]])

		#Add helix deep than pile
		with self.assertRaises(grpc.RpcError):
			self.pileType.Helical.Sections.Helices.setHelicesByDepth([[0.7, 0.06, 2], [0.9, 0.07, 10000000]])
		with self.assertRaises(grpc.RpcError):
			self.pileType.Helical.Sections.Helices.setHelicesBySpacing(6, [0.7, 0.05], [[0.7, 0.06, 2], [0.9, 0.07, 10000000]])

		#add helix with negative pitch
		with self.assertRaises(grpc.RpcError):
			self.pileType.Helical.Sections.Helices.setHelicesByDepth([[0.8, 0.04, 2], [-0.9, 0.03, 3]])
		with self.assertRaises(grpc.RpcError):
			self.pileType.Helical.Sections.Helices.setHelicesBySpacing(6, [0.9, 0.6], [[-0.7, 0.04, 2], [0.9, 0.03, 3]])

		#add helix with negative diameter
		with self.assertRaises(grpc.RpcError):
			self.pileType.Helical.Sections.Helices.setHelicesByDepth([[0.7, -0.06, 2], [0.9, 0.07, 3]])
		with self.assertRaises(grpc.RpcError):
			self.pileType.Helical.Sections.Helices.setHelicesBySpacing(6, [0.7, 0.6], [[0.7, -0.06, 2], [0.9, 0.07, 3]])

		#add helix with negative spacing
		with self.assertRaises(grpc.RpcError):
			self.pileType.Helical.Sections.Helices.setHelicesBySpacing(6, [0.7, 0.6], [[0.9, 0.08, -3]])

		#add helix with spacing that causes overlapping
		with self.assertRaises(grpc.RpcError):
			self.pileType.Helical.Sections.Helices.setHelicesBySpacing(6, [0.7, 0.6], [[0.9, 0.08, 0.01]])

		with self.assertRaises(grpc.RpcError):
			self.pileType.Helical.Sections.Helices.setHelicesBySpacing(6, [0.7, 0.6], [[0.9, 0.08, 0.01]])		

		#add helix with negative depth
		with self.assertRaises(grpc.RpcError):
			self.pileType.Helical.Sections.Helices.setHelicesByDepth([[0.9, 0.06, -2], [0.3, 0.07, 3]])

		#add helix with diameter less than shaft diameter
		self.pileSection.setName("Small Diameter Pile Section")
		self.pileSection.HelicalCapacity.setCrossSectionType(HelicalCrossSectionType.CIRCULAR_SOLID)
		self.pileSection.HelicalCapacity.CircularSolid.setDiameter(0.1)
		self.pileType.Helical.Sections.setPileSegmentsByLength(0, [["Small Diameter Pile Section", 11]])
		with self.assertRaises(grpc.RpcError):
			self.pileType.Helical.Sections.Helices.setHelicesByDepth([[0.05, 0.06, 5]])

if __name__ == '__main__':
	unittest.main(verbosity=2)