import unittest
from RSPileScripting.RSPileModeler import RSPileModeler
from RSPileScripting.enums import *
from RSPileScripting.Utilities.ColorPicker import ColorPicker

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
		shutil.copy(TestPileProperties.test_file, self.copy_file)
	
		self.model = self.modeler.openFile(self.copy_file)
		self.pileSection = self.model.getPileSections()[0]

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

	#region Generic Pile Props
	def testGenericProps(self):
		self.pileSection.setName("Test Name 123!")
		self.assertEqual(self.pileSection.getName(), "Test Name 123!")

		self.pileSection.setColor(ColorPicker.Aqua)
		self.assertEqual(self.pileSection.getColor(), ColorPicker.Aqua)

		self.pileSection.setColor(ColorPicker.getColorFromRGB(50,50,50))
		self.assertEqual(self.pileSection.getColor(), ColorPicker.getColorFromRGB(50,50,50))
	#endregion

	#region Pile Analysis Props
	def testPileAnalysisSectionTypes(self):
		for section in SectionType:
			self.pileSection.PileAnalysis.setSectionType(section)
			self.assertEqual(self.pileSection.PileAnalysis.getSectionType(), section)
	#endregion

	#region Pile Analysis Elastic Material Props
	def testPileAnalysisElasticMaterialProperties(self):
		for section in ElasticCrossSectionType:
			self.pileSection.PileAnalysis.Elastic.setCrossSectionType(section)
			self.assertEqual(self.pileSection.PileAnalysis.Elastic.getCrossSectionType(), section)	

		self.pileSection.PileAnalysis.Elastic.setYoungsModulus(3000.23)
		self.assertEqual(self.pileSection.PileAnalysis.Elastic.getYoungsModulus(), 3000.23)
	#endregion	

	#region Pile Analysis Plastic Material Props
	def testPileAnalysisPlasticMaterialProperties(self):
		for section in PlasticCrossSectionType:
			self.pileSection.PileAnalysis.Plastic.setCrossSectionType(section)
			self.assertEqual(self.pileSection.PileAnalysis.Plastic.getCrossSectionType(), section)

		self.pileSection.PileAnalysis.Plastic.setYoungsModulus(3000.25)
		self.assertEqual(self.pileSection.PileAnalysis.Plastic.getYoungsModulus(), 3000.25)

		self.pileSection.PileAnalysis.Plastic.setMomentCapacityMyz(1500.45)
		self.assertEqual(self.pileSection.PileAnalysis.Plastic.getMomentCapacityMyz(), 1500.45)

		self.pileSection.PileAnalysis.Plastic.setMomentCapacityMxz(2500.67)
		self.assertEqual(self.pileSection.PileAnalysis.Plastic.getMomentCapacityMxz(), 2500.67)
	#endregion

	
	#region Pile Analysis Prestressed Concrete Material Props
	def testPileAnalysisPrestressedConcreteMaterialProperties(self):
		for section in PrestressedConcreteCrossSectionType:
			self.pileSection.PileAnalysis.PrestressedConcrete.setCrossSectionType(section)
			self.assertEqual(self.pileSection.PileAnalysis.PrestressedConcrete.getCrossSectionType(), section)

		self.pileSection.PileAnalysis.PrestressedConcrete.setCompressiveStrength(3000.23)
		self.assertEqual(self.pileSection.PileAnalysis.PrestressedConcrete.getCompressiveStrength(), 3000.23)
	#endregion


	#region Pile Analysis Reinforced Concrete Material Props
	def testPileAnalysisReinforcedConcreteMaterialProperties(self):
		for section in ReinforcedConcreteCrossSectionType:
			self.pileSection.PileAnalysis.ReinforcedConcrete.setCrossSectionType(section)
			self.assertEqual(self.pileSection.PileAnalysis.ReinforcedConcrete.getCrossSectionType(), section)

		self.pileSection.PileAnalysis.ReinforcedConcrete.setCompressiveStrength(3000.23)
		self.assertEqual(self.pileSection.PileAnalysis.ReinforcedConcrete.getCompressiveStrength(), 3000.23)
	#endregion

	#region Bored Capacity Props
	def testBoredCapacitySectionTypes(self):
		for section in BoredCrossSectionType:
			self.pileSection.BoredCapacity.setCrossSectionType(section)
			self.assertEqual(self.pileSection.BoredCapacity.getCrossSectionType(), section)

		self.pileSection.BoredCapacity.setConcreteCylinderStrength(125.1)
		self.assertEqual(self.pileSection.BoredCapacity.getConcreteCylinderStrength(), 125.1)
	#endregion	

	#region Driven Capacity Props
	def testDrivenCapacitySectionTypes(self):
		for section in DrivenCrossSectionType:
			self.pileSection.DrivenCapacity.setCrossSectionType(section)
			self.assertEqual(self.pileSection.DrivenCapacity.getCrossSectionType(), section)
	#endregion	

	#region test Bored Cross Sections
	def testBoredCircularCrossSection(self):
		self.pileSection.BoredCapacity.Circular.setDiameter(1.7)
		self.assertEqual(self.pileSection.BoredCapacity.Circular.getDiameter(), 1.7)

	def testBoredRectangularCrossSection(self):
		self.pileSection.BoredCapacity.Rectangular.setWidth(2.5)
		self.assertEqual(self.pileSection.BoredCapacity.Rectangular.getWidth(), 2.5)

		self.pileSection.BoredCapacity.Rectangular.setBreadth(1.6)
		self.assertEqual(self.pileSection.BoredCapacity.Rectangular.getBreadth(), 1.6)

	def testBoredSquareCrossSection(self):
		self.pileSection.BoredCapacity.Square.setSideLength(3.5)
		self.assertEqual(self.pileSection.BoredCapacity.Square.getSideLength(), 3.5)
	#endregion

	#region test Driven Cross Sections
	def testDrivenClosedEndPipeCrossSection(self):
		self.pileSection.DrivenCapacity.ClosedEndPipe.setDiameterOfPile(2.0)
		self.assertEqual(self.pileSection.DrivenCapacity.ClosedEndPipe.getDiameterOfPile(), 2.0)

	def testDrivenOpenEndPipeCrossSection(self):
		self.pileSection.DrivenCapacity.OpenEndPipe.setDiameterOfPile(2.5)
		self.assertEqual(self.pileSection.DrivenCapacity.OpenEndPipe.getDiameterOfPile(), 2.5)

		self.pileSection.DrivenCapacity.OpenEndPipe.setShellThickness(0.5)
		self.assertEqual(self.pileSection.DrivenCapacity.OpenEndPipe.getShellThickness(), 0.5)

	def testDrivenConcreteCrossSection(self):
		self.pileSection.DrivenCapacity.Concrete.setSideOfSquareSection(4.0)
		self.assertEqual(self.pileSection.DrivenCapacity.Concrete.getSideOfSquareSection(), 4.0)
	def testDrivenRaymondCrossSection(self):
		self.pileSection.DrivenCapacity.Raymond.setDiameterOfPile(3.0)
		self.assertEqual(self.pileSection.DrivenCapacity.Raymond.getDiameterOfPile(), 3.0)

	def testDrivenTimberCrossSection(self):
		self.pileSection.DrivenCapacity.Timber.setDiameterOfPile(2.9)
		self.assertEqual(self.pileSection.DrivenCapacity.Timber.getDiameterOfPile(), 2.9)

	def testDrivenRolledSectionUserSelectedAreaCrossSection(self):
		self.pileSection.DrivenCapacity.RolledSection.UserSelectedArea.setAreaOfTip(5.0)
		self.assertEqual(self.pileSection.DrivenCapacity.RolledSection.UserSelectedArea.getAreaOfTip(), 5.0)
	#endregion

	#region test Pile Analysis Cross Sections
	def testPileAnalysisCircularCrossSection(self):
		self.pileSection.PileAnalysis.Elastic.CrossSection.Circular.setDiameter(1.53)
		self.assertEqual(self.pileSection.PileAnalysis.Elastic.CrossSection.Circular.getDiameter(), 1.53)

	def testPileAnalysisPipeCrossSection(self):
		self.pileSection.PileAnalysis.Elastic.CrossSection.Pipe.setOutsideDiameter(2.07)
		self.assertEqual(self.pileSection.PileAnalysis.Elastic.CrossSection.Pipe.getOutsideDiameter(), 2.07)

		self.pileSection.PileAnalysis.Elastic.CrossSection.Pipe.setWallThickness(0.32)
		self.assertEqual(self.pileSection.PileAnalysis.Elastic.CrossSection.Pipe.getWallThickness(), 0.32)

	def testPileAnalysisRectangularCrossSection(self):
		self.pileSection.PileAnalysis.Elastic.CrossSection.Rectangular.setWidth(3.74)
		self.assertEqual(self.pileSection.PileAnalysis.Elastic.CrossSection.Rectangular.getWidth(), 3.74)

		self.pileSection.PileAnalysis.Elastic.CrossSection.Rectangular.setDepth(4.21)
		self.assertEqual(self.pileSection.PileAnalysis.Elastic.CrossSection.Rectangular.getDepth(), 4.21)

	def testPileAnalysisUserDefinedCrossSection(self):
		self.pileSection.PileAnalysis.Elastic.CrossSection.UserDefined.setDiameter(1.57)
		self.assertEqual(self.pileSection.PileAnalysis.Elastic.CrossSection.UserDefined.getDiameter(), 1.57)

		self.pileSection.PileAnalysis.Elastic.CrossSection.UserDefined.setPerimeter(5.03)
		self.assertEqual(self.pileSection.PileAnalysis.Elastic.CrossSection.UserDefined.getPerimeter(), 5.03)

		self.pileSection.PileAnalysis.Elastic.CrossSection.UserDefined.setArea(10.08)
		self.assertEqual(self.pileSection.PileAnalysis.Elastic.CrossSection.UserDefined.getArea(), 10.08)

		self.pileSection.PileAnalysis.Elastic.CrossSection.UserDefined.setIy(2.04)
		self.assertEqual(self.pileSection.PileAnalysis.Elastic.CrossSection.UserDefined.getIy(), 2.04)

		self.pileSection.PileAnalysis.Elastic.CrossSection.UserDefined.setIx(3.09)
		self.assertEqual(self.pileSection.PileAnalysis.Elastic.CrossSection.UserDefined.getIx(), 3.09)
	#endregion

	#region test Helical Piles
	def testHelicalPileCrossSection(self):
		for type in HelicalCrossSectionType:
			self.pileSection.HelicalCapacity.setCrossSectionType(type)
			self.assertEqual(self.pileSection.HelicalCapacity.getCrossSectionType(), type)

	#end region
		
	#region test Helical Pile Circular Solid Cross Section
	def testHelicalPileCircularSolidCrossSection(self):
		self.pileSection.HelicalCapacity.CircularSolid.setDiameter(1.3)
		self.assertEqual(self.pileSection.HelicalCapacity.CircularSolid.getDiameter(), 1.3)
	
	#end region

	#region test Helical Pile Circular Hollow Cross Section
	def testHelicalPileCircularHollowCrossSection(self):
		self.pileSection.HelicalCapacity.CircularHollow.setOuterDiameter(1.4)
		self.assertEqual(self.pileSection.HelicalCapacity.CircularHollow.getOuterDiameter(), 1.4)

		self.pileSection.HelicalCapacity.CircularHollow.setThickness(0.01)
		self.assertEqual(self.pileSection.HelicalCapacity.CircularHollow.getThickness(), 0.01)
	#end region

	#region test Helical Pile Square Solid Cross Section
	def testHelicalPileSquareSolidCrossSection(self):
		self.pileSection.HelicalCapacity.SquareSolid.setSideLength(1.5)
		self.assertEqual(self.pileSection.HelicalCapacity.SquareSolid.getSideLength(), 1.5)
	#end region

	#region test Helical Pile Square Hollow Cross Section
	def testHelicalPileSquareHollowCrossSection(self):
		self.pileSection.HelicalCapacity.SquareHollow.setOuterSideLength(1.6)
		self.assertEqual(self.pileSection.HelicalCapacity.SquareHollow.getOuterSideLength(), 1.6)

		self.pileSection.HelicalCapacity.SquareHollow.setThickness(0.02)
		self.assertEqual(self.pileSection.HelicalCapacity.SquareHollow.getThickness(), 0.02)
	#end region

if __name__ == '__main__':
	unittest.main(verbosity=2)