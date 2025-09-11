import unittest
from RSPileScripting.RSPileModeler import RSPileModeler
from RSPileScripting.enums import *
from dotenv import load_dotenv
import shutil
import os

class TestDrivenRolledSections(unittest.TestCase):
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
		shutil.copy(TestDrivenRolledSections.test_file, self.copy_file)
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

	def testDrivenRolledHP360x174(self):
		RolledSection = self.pileSection.DrivenCapacity.RolledSection
		RolledSection.setDesignation(PileSectionDesignation.HP360_x_174)
		self.assertAlmostEqual(RolledSection.getSectionDepth(), 0.361, places=3)
		self.assertAlmostEqual(RolledSection.getSectionWidth(), 0.378, places=3)
		self.assertAlmostEqual(RolledSection.getSectionArea(), 0.0222, places=4)
		self.assertAlmostEqual(RolledSection.getSectionBoxArea(), 0.1365, places=4)
		self.assertAlmostEqual(RolledSection.getSectionPerimeter(), 2.1932, places=4)
		self.assertAlmostEqual(RolledSection.getSectionBoxPerimeter(), 1.4780, places=4)
		self.assertAlmostEqual(RolledSection.getWebThickness(), 0.0204, places=3)
		self.assertAlmostEqual(RolledSection.getFlangeThickness(), 0.0204, places=3)
		RolledSection.setAreaForEndBearing(RolledSectionArea.ROLLED_SECTION_AREA)
		self.assertEqual(RolledSection.getAreaForEndBearing(), RolledSectionArea.ROLLED_SECTION_AREA)
		RolledSection.setPerimeterForSkinFriction(RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)
		self.assertEqual(RolledSection.getPerimeterForSkinFriction(), RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)

	def testDrivenRolledW1100x499(self):
		RolledSection = self.pileSection.DrivenCapacity.RolledSection
		RolledSection.setDesignation(PileSectionDesignation.W1100_x_499)
		self.assertAlmostEqual(RolledSection.getSectionDepth(), 1.120, places=3)
		self.assertAlmostEqual(RolledSection.getSectionWidth(), 0.404, places=3)
		self.assertAlmostEqual(RolledSection.getSectionArea(), 0.06350, places=5)
		self.assertAlmostEqual(RolledSection.getWebThickness(), 0.0262, places=4)
		self.assertAlmostEqual(RolledSection.getFlangeThickness(), 0.045, places=3)
		RolledSection.setAreaForEndBearing(RolledSectionArea.ROLLED_SECTION_AREA)
		self.assertEqual(RolledSection.getAreaForEndBearing(), RolledSectionArea.ROLLED_SECTION_AREA)
		RolledSection.setPerimeterForSkinFriction(RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)
		self.assertEqual(RolledSection.getPerimeterForSkinFriction(), RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)

	def testDrivenRolledW1100x433(self):
		RolledSection = self.pileSection.DrivenCapacity.RolledSection
		RolledSection.setDesignation(PileSectionDesignation.W1100_x_433)
		self.assertAlmostEqual(RolledSection.getSectionDepth(), 1.110, places=3)
		self.assertAlmostEqual(RolledSection.getSectionWidth(), 0.401, places=3)
		self.assertAlmostEqual(RolledSection.getSectionArea(), 0.05510, places=5)
		self.assertAlmostEqual(RolledSection.getWebThickness(), 0.022, places=3)
		self.assertAlmostEqual(RolledSection.getFlangeThickness(), 0.0401, places=4)
		RolledSection.setAreaForEndBearing(RolledSectionArea.ROLLED_SECTION_AREA)
		self.assertEqual(RolledSection.getAreaForEndBearing(), RolledSectionArea.ROLLED_SECTION_AREA)
		RolledSection.setPerimeterForSkinFriction(RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)
		self.assertEqual(RolledSection.getPerimeterForSkinFriction(), RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)

	def testDrivenRolledW1100x390(self):
		RolledSection = self.pileSection.DrivenCapacity.RolledSection
		RolledSection.setDesignation(PileSectionDesignation.W1100_x_390)
		self.assertAlmostEqual(RolledSection.getSectionDepth(), 1.10, places=3)
		self.assertAlmostEqual(RolledSection.getSectionWidth(), 0.401, places=3)
		self.assertAlmostEqual(RolledSection.getSectionArea(), 0.0498, places=5)
		self.assertAlmostEqual(RolledSection.getWebThickness(), 0.0199, places=4)
		self.assertAlmostEqual(RolledSection.getFlangeThickness(), 0.0361, places=4)
		RolledSection.setAreaForEndBearing(RolledSectionArea.ROLLED_SECTION_AREA)
		self.assertEqual(RolledSection.getAreaForEndBearing(), RolledSectionArea.ROLLED_SECTION_AREA)
		RolledSection.setPerimeterForSkinFriction(RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)
		self.assertEqual(RolledSection.getPerimeterForSkinFriction(), RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)

	def testDrivenRolledW44x335(self):
		RolledSection = self.pileSection.DrivenCapacity.RolledSection
		RolledSection.setDesignation(PileSectionDesignation.W44_x_335)
		self.assertAlmostEqual(RolledSection.getSectionDepth(), 1.120, places=3)
		self.assertAlmostEqual(RolledSection.getSectionWidth(), 0.404, places=3)
		self.assertAlmostEqual(RolledSection.getSectionArea(), 0.06350, places=5)
		self.assertAlmostEqual(RolledSection.getWebThickness(), 0.0262, places=4)
		self.assertAlmostEqual(RolledSection.getFlangeThickness(), 0.045, places=4)
		RolledSection.setAreaForEndBearing(RolledSectionArea.ROLLED_SECTION_AREA)
		self.assertEqual(RolledSection.getAreaForEndBearing(), RolledSectionArea.ROLLED_SECTION_AREA)
		RolledSection.setPerimeterForSkinFriction(RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)
		self.assertEqual(RolledSection.getPerimeterForSkinFriction(), RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)

	def testDrivenRolledM8x6_5(self):
		RolledSection = self.pileSection.DrivenCapacity.RolledSection
		RolledSection.setDesignation(PileSectionDesignation.M8_x_6_5)
		self.assertAlmostEqual(RolledSection.getSectionDepth(), 0.203, places=3)
		self.assertAlmostEqual(RolledSection.getSectionWidth(), 0.0579, places=3)
		self.assertAlmostEqual(RolledSection.getSectionArea(), 0.001240, places=5)
		self.assertAlmostEqual(RolledSection.getWebThickness(), 0.00343, places=4)
		self.assertAlmostEqual(RolledSection.getFlangeThickness(), 0.0048, places=4)
		RolledSection.setAreaForEndBearing(RolledSectionArea.ROLLED_SECTION_AREA)
		self.assertEqual(RolledSection.getAreaForEndBearing(), RolledSectionArea.ROLLED_SECTION_AREA)
		RolledSection.setPerimeterForSkinFriction(RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)
		self.assertEqual(RolledSection.getPerimeterForSkinFriction(), RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)

	def testDrivenRolledHP460x304(self):
		RolledSection = self.pileSection.DrivenCapacity.RolledSection
		RolledSection.setDesignation(PileSectionDesignation.HP460_x_304)
		self.assertAlmostEqual(RolledSection.getSectionDepth(), 0.465, places=3)
		self.assertAlmostEqual(RolledSection.getSectionWidth(), 0.45974, places=5)
		self.assertAlmostEqual(RolledSection.getSectionArea(), 0.0388, places=5)
		self.assertAlmostEqual(RolledSection.getWebThickness(), 0.0287, places=4)
		self.assertAlmostEqual(RolledSection.getFlangeThickness(), 0.0287, places=4)
		RolledSection.setAreaForEndBearing(RolledSectionArea.ROLLED_SECTION_AREA)
		self.assertEqual(RolledSection.getAreaForEndBearing(), RolledSectionArea.ROLLED_SECTION_AREA)
		RolledSection.setPerimeterForSkinFriction(RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)
		self.assertEqual(RolledSection.getPerimeterForSkinFriction(), RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)

	def testDrivenRolledHP460x269(self):
		RolledSection = self.pileSection.DrivenCapacity.RolledSection
		RolledSection.setDesignation(PileSectionDesignation.HP460_x_269)
		self.assertAlmostEqual(RolledSection.getSectionDepth(), 0.4572, places=4)
		self.assertAlmostEqual(RolledSection.getSectionWidth(), 0.4572, places=4)
		self.assertAlmostEqual(RolledSection.getSectionArea(), 0.0343, places=5)
		self.assertAlmostEqual(RolledSection.getWebThickness(), 0.0254, places=4)
		self.assertAlmostEqual(RolledSection.getFlangeThickness(), 0.0254, places=4)
		RolledSection.setAreaForEndBearing(RolledSectionArea.ROLLED_SECTION_AREA)
		self.assertEqual(RolledSection.getAreaForEndBearing(), RolledSectionArea.ROLLED_SECTION_AREA)
		RolledSection.setPerimeterForSkinFriction(RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)
		self.assertEqual(RolledSection.getPerimeterForSkinFriction(), RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)

	def testDrivenRolledHP460x234(self):
		RolledSection = self.pileSection.DrivenCapacity.RolledSection
		RolledSection.setDesignation(PileSectionDesignation.HP460_x_234)
		self.assertAlmostEqual(RolledSection.getSectionDepth(), 0.450596, places=6)
		self.assertAlmostEqual(RolledSection.getSectionWidth(), 0.45466, places=5)
		self.assertAlmostEqual(RolledSection.getSectionArea(), 0.0298, places=5)
		self.assertAlmostEqual(RolledSection.getWebThickness(), 0.0221, places=4)
		self.assertAlmostEqual(RolledSection.getFlangeThickness(), 0.0221, places=4)
		RolledSection.setAreaForEndBearing(RolledSectionArea.ROLLED_SECTION_AREA)
		self.assertEqual(RolledSection.getAreaForEndBearing(), RolledSectionArea.ROLLED_SECTION_AREA)
		RolledSection.setPerimeterForSkinFriction(RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)
		self.assertEqual(RolledSection.getPerimeterForSkinFriction(), RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)

	def testDrivenRolledS75x11_2(self):
		RolledSection = self.pileSection.DrivenCapacity.RolledSection
		RolledSection.setDesignation(PileSectionDesignation.S75_x_11_2)
		self.assertAlmostEqual(RolledSection.getSectionDepth(), 0.0762, places=6)
		self.assertAlmostEqual(RolledSection.getSectionWidth(), 0.0638, places=5)
		self.assertAlmostEqual(RolledSection.getSectionArea(), 0.00142, places=5)
		self.assertAlmostEqual(RolledSection.getWebThickness(), 0.00886, places=4)
		self.assertAlmostEqual(RolledSection.getFlangeThickness(), 0.0066, places=4)
		RolledSection.setAreaForEndBearing(RolledSectionArea.ROLLED_SECTION_AREA)
		self.assertEqual(RolledSection.getAreaForEndBearing(), RolledSectionArea.ROLLED_SECTION_AREA)
		RolledSection.setPerimeterForSkinFriction(RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)
		self.assertEqual(RolledSection.getPerimeterForSkinFriction(), RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)

	def testDrivenRolledM250x11_9(self):
		RolledSection = self.pileSection.DrivenCapacity.RolledSection
		RolledSection.setDesignation(PileSectionDesignation.M250_x_11_9)
		self.assertAlmostEqual(RolledSection.getSectionDepth(), 0.253, places=6)
		self.assertAlmostEqual(RolledSection.getSectionWidth(), 0.0683, places=5)
		self.assertAlmostEqual(RolledSection.getSectionArea(), 0.00153, places=5)
		self.assertAlmostEqual(RolledSection.getWebThickness(), 0.00358, places=4)
		self.assertAlmostEqual(RolledSection.getFlangeThickness(), 0.00462, places=4)
		RolledSection.setAreaForEndBearing(RolledSectionArea.ROLLED_SECTION_AREA)
		self.assertEqual(RolledSection.getAreaForEndBearing(), RolledSectionArea.ROLLED_SECTION_AREA)
		RolledSection.setPerimeterForSkinFriction(RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)
		self.assertEqual(RolledSection.getPerimeterForSkinFriction(), RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)

	def testDrivenRolledHSS101_6x101_6x7_9(self):
		RolledSection = self.pileSection.DrivenCapacity.RolledSection
		RolledSection.setDesignation(PileSectionDesignation.HSS101_6_x_101_6_x_7_9)
		self.assertAlmostEqual(RolledSection.getSectionDepth(), 0.102, places=6)
		self.assertAlmostEqual(RolledSection.getSectionWidth(), 0.102, places=5)
		self.assertAlmostEqual(RolledSection.getSectionArea(), 0.002650, places=5)
		RolledSection.setAreaForEndBearing(RolledSectionArea.ROLLED_SECTION_AREA)
		self.assertEqual(RolledSection.getAreaForEndBearing(), RolledSectionArea.ROLLED_SECTION_AREA)
		RolledSection.setPerimeterForSkinFriction(RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)
		self.assertEqual(RolledSection.getPerimeterForSkinFriction(), RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)

	def testDrivenRolledHSS10x10x3_8(self):
		RolledSection = self.pileSection.DrivenCapacity.RolledSection
		RolledSection.setDesignation(PileSectionDesignation.HSS10_x_10_x_3_8)
		self.assertAlmostEqual(RolledSection.getSectionDepth(), 0.254, places=6)
		self.assertAlmostEqual(RolledSection.getSectionWidth(), 0.254, places=5)
		self.assertAlmostEqual(RolledSection.getSectionArea(), 0.008520, places=5)
		RolledSection.setAreaForEndBearing(RolledSectionArea.ROLLED_SECTION_AREA)
		self.assertEqual(RolledSection.getAreaForEndBearing(), RolledSectionArea.ROLLED_SECTION_AREA)
		RolledSection.setPerimeterForSkinFriction(RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)
		self.assertEqual(RolledSection.getPerimeterForSkinFriction(), RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)

	def testDrivenRolledHSS16x0_500(self):
		RolledSection = self.pileSection.DrivenCapacity.RolledSection
		RolledSection.setDesignation(PileSectionDesignation.HSS16_x_0_500)
		self.assertAlmostEqual(RolledSection.getSectionDepth(), 0.406, places=6)
		self.assertAlmostEqual(RolledSection.getSectionWidth(), 0.406, places=5)
		self.assertAlmostEqual(RolledSection.getSectionArea(), 0.014600, places=5)
		RolledSection.setAreaForEndBearing(RolledSectionArea.ROLLED_SECTION_AREA)
		self.assertEqual(RolledSection.getAreaForEndBearing(), RolledSectionArea.ROLLED_SECTION_AREA)
		RolledSection.setPerimeterForSkinFriction(RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)
		self.assertEqual(RolledSection.getPerimeterForSkinFriction(), RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)

	def testDrivenRolledPipe254XS(self):
		RolledSection = self.pileSection.DrivenCapacity.RolledSection
		RolledSection.setDesignation(PileSectionDesignation.Pipe254XS)
		self.assertAlmostEqual(RolledSection.getSectionDepth(), 0.274, places=6)
		self.assertAlmostEqual(RolledSection.getSectionWidth(), 0.274, places=5)
		self.assertAlmostEqual(RolledSection.getSectionArea(), 0.009740, places=5)
		RolledSection.setAreaForEndBearing(RolledSectionArea.ROLLED_SECTION_AREA)
		self.assertEqual(RolledSection.getAreaForEndBearing(), RolledSectionArea.ROLLED_SECTION_AREA)
		RolledSection.setPerimeterForSkinFriction(RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)
		self.assertEqual(RolledSection.getPerimeterForSkinFriction(), RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)

	def testDrivenRolledPipe1_1_2XS(self):
		RolledSection = self.pileSection.DrivenCapacity.RolledSection
		RolledSection.setDesignation(PileSectionDesignation.Pipe1_2XS)
		self.assertAlmostEqual(RolledSection.getSectionDepth(), 0.0213, places=6)
		self.assertAlmostEqual(RolledSection.getSectionWidth(), 0.0213, places=5)
		self.assertAlmostEqual(RolledSection.getSectionArea(), 0.000195, places=5)
		RolledSection.setAreaForEndBearing(RolledSectionArea.ROLLED_SECTION_AREA)
		self.assertEqual(RolledSection.getAreaForEndBearing(), RolledSectionArea.ROLLED_SECTION_AREA)
		RolledSection.setPerimeterForSkinFriction(RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)
		self.assertEqual(RolledSection.getPerimeterForSkinFriction(), RolledSectionPerimeter.ROLLED_SECTION_PERIMETER)

	

if __name__ == '__main__':
	unittest.main(verbosity=2) 