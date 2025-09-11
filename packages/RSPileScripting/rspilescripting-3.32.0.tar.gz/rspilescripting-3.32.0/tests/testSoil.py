import unittest
from RSPileScripting.RSPileModeler import RSPileModeler
from RSPileScripting.enums import *
from RSPileScripting.Utilities.ColorPicker import ColorPicker
from dotenv import load_dotenv
import shutil
import os
from enum import Enum
from RSPileScripting.SoilProperties.Datum import Datum
import random as rand
import grpc

class TestSoilProperties(unittest.TestCase):
	load_dotenv()
	port = 60044
	exe_path = os.getenv("PATH_TO_RSPILE_CPP_REPO") + "\\Build\\Debug_x64\\RSPile.exe"
	test_file = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\TestProject.rspile2"

	@classmethod
	def setUpClass(cls):
		RSPileModeler.startApplication(overridePathToExecutable=cls.exe_path, port=cls.port)
		cls.modeler = RSPileModeler(cls.port)
		cls.copy_file = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\copyTestProject.rspile2"
		shutil.copy(cls.test_file, cls.copy_file)
		cls.model = cls.modeler.openFile(cls.copy_file)
		cls.soilProp = cls.model.getSoilProperties()[0]

	@classmethod
	def tearDownClass(cls):
		cls.model.close()
		if os.path.exists(cls.copy_file):
			os.remove(cls.copy_file)
		copy_file_dir = os.path.dirname(cls.copy_file) + "\\copyTestProject"
		if os.path.exists(copy_file_dir):
			try:
				shutil.rmtree(copy_file_dir)
			except Exception:
				print(f"Failed to remove directory: {copy_file_dir}")

		cls.modeler.closeApplication()

	def datumTestHelper(self, datumObject : Datum, datumEnum : Enum):
		for datum in datumEnum:
			random_datum_val = rand.random()
			datumObject.setDatum(datum, random_datum_val)
			self.assertAlmostEqual(datumObject.getDatum(datum), random_datum_val, 2)
			datumObject.removeDatum(datum)

			with self.assertRaises(grpc.RpcError):
				datumObject.getDatum(datum)

			with self.assertRaises(grpc.RpcError):
				datumObject.removeDatum(datum)

	#region Generic Soil Props
	def testGenericProps(self):
		self.soilProp.setName("Test Name 123!")
		self.assertEqual(self.soilProp.getName(), "Test Name 123!")

		self.soilProp.setColor(ColorPicker.Aqua)
		self.assertEqual(self.soilProp.getColor(), ColorPicker.Aqua)

		self.soilProp.setColor(ColorPicker.getColorFromRGB(50,50,50))
		self.assertEqual(self.soilProp.getColor(), ColorPicker.getColorFromRGB(50,50,50))

		for hatch in HatchStyle:
			self.soilProp.setHatch(hatch)
			self.assertEqual(self.soilProp.getHatch(), hatch)

		self.soilProp.setUnitWeight(19.5)
		self.assertEqual(self.soilProp.getUnitWeight(), 19.5)

		self.soilProp.setUseSaturatedUnitWeight(True)
		self.assertTrue(self.soilProp.getUseSaturatedUnitWeight())

		self.soilProp.setUseSaturatedUnitWeight(False)
		self.assertFalse(self.soilProp.getUseSaturatedUnitWeight())

		self.soilProp.setSaturatedUnitWeight(21.0)
		self.assertEqual(self.soilProp.getSaturatedUnitWeight(), 21.0)

		self.soilProp.getUseDatumDependency()
		self.soilProp.setUseDatumDependency(True)
		self.assertTrue(self.soilProp.getUseDatumDependency())

		self.soilProp.setUseDatumDependency(False)
		self.assertFalse(self.soilProp.getUseDatumDependency())

		self.datumTestHelper(self.soilProp.Datum, GeneralDatumProperties)
	#endregion

	#region Axial Soil Props
	def testAxialProps(self):
		for axialType in AxialType:
			self.soilProp.AxialProperties.setAxialType(axialType)
			self.assertEqual(self.soilProp.AxialProperties.getAxialType(), axialType)
	#endregion

	#region Axial API Sand Props
	def testAxialAPISandProps(self):
		self.soilProp.AxialProperties.APISand.setCoefficientOfLateralEarthPressure(2)
		self.assertEqual(self.soilProp.AxialProperties.APISand.getCoefficientOfLateralEarthPressure(), 2)

		self.soilProp.AxialProperties.APISand.setBearingCapacityFactor(3)
		self.assertEqual(self.soilProp.AxialProperties.APISand.getBearingCapacityFactor(), 3)

		self.soilProp.AxialProperties.APISand.setFrictionAngle(30)
		self.assertEqual(self.soilProp.AxialProperties.APISand.getFrictionAngle(), 30)

		self.soilProp.AxialProperties.APISand.setMaximumUnitSkinFriction(4)
		self.assertEqual(self.soilProp.AxialProperties.APISand.getMaximumUnitSkinFriction(), 4)

		self.soilProp.AxialProperties.APISand.setMaximumUnitEndBearingResistance(5)
		self.assertEqual(self.soilProp.AxialProperties.APISand.getMaximumUnitEndBearingResistance(), 5)

		self.datumTestHelper(self.soilProp.AxialProperties.APISand.Datum, AxialAPISandDatumProperties)
	#endregion

 #region Axial API Clay Props
	def testAxialAPIClayProps(self):
		self.soilProp.AxialProperties.APIClay.setUndrainedShearStrength(51.8)
		self.assertEqual(self.soilProp.AxialProperties.APIClay.getUndrainedShearStrength(), 51.8)

		self.soilProp.AxialProperties.APIClay.setMaximumUnitEndBearingResistance(53.2)
		self.assertEqual(self.soilProp.AxialProperties.APIClay.getMaximumUnitEndBearingResistance(), 53.2)

		self.soilProp.AxialProperties.APIClay.setUndrainedShearStrength(30)
		self.assertEqual(self.soilProp.AxialProperties.APIClay.getUndrainedShearStrength(), 30)

		self.soilProp.AxialProperties.APIClay.setRemoldedShearStrength(28.2)
		self.assertEqual(self.soilProp.AxialProperties.APIClay.getRemoldedShearStrength(), 28.2)

		self.soilProp.AxialProperties.APIClay.setMaximumUnitSkinFriction(1000000)
		self.assertEqual(self.soilProp.AxialProperties.APIClay.getMaximumUnitSkinFriction(), 1000000)

		self.soilProp.AxialProperties.APISand.setMaximumUnitEndBearingResistance(5)
		self.assertEqual(self.soilProp.AxialProperties.APISand.getMaximumUnitEndBearingResistance(), 5)

		self.datumTestHelper(self.soilProp.AxialProperties.APIClay.Datum, AxialAPIClayDatumProperties)
	#endregion

	#region Axial Drilled Sand Props
	def testAxialDrilledSandProps(self):
		self.soilProp.AxialProperties.DrilledSand.setUltimateShearResistance(200)
		self.assertEqual(self.soilProp.AxialProperties.DrilledSand.getUltimateShearResistance(), 200)

		self.soilProp.AxialProperties.DrilledSand.setUltimateEndBearingResistance(130000)
		self.assertEqual(self.soilProp.AxialProperties.DrilledSand.getUltimateEndBearingResistance(), 130000)

		self.datumTestHelper(self.soilProp.AxialProperties.DrilledSand.Datum, AxialDrilledSandDatumProperties)
	#endregion

	#region Axial Drilled Clay Props
	def testAxialDrilledClayProps(self):
		self.soilProp.AxialProperties.DrilledClay.setUltimateShearResistance(200)
		self.assertEqual(self.soilProp.AxialProperties.DrilledClay.getUltimateShearResistance(), 200)

		self.soilProp.AxialProperties.DrilledClay.setUltimateEndBearingResistance(130000)
		self.assertEqual(self.soilProp.AxialProperties.DrilledClay.getUltimateEndBearingResistance(), 130000)

		self.datumTestHelper(self.soilProp.AxialProperties.DrilledClay.Datum, AxialDrilledClayDatumProperties)
	#endregion

	#region Axial Coyle and Reese Clay Props
	def testAxialCoyleAndReeseClayProps(self):
		self.soilProp.AxialProperties.CoyleAndReeseClay.setShearStrength(250)
		self.assertEqual(self.soilProp.AxialProperties.CoyleAndReeseClay.getShearStrength(), 250)

		self.soilProp.AxialProperties.CoyleAndReeseClay.setUltimateShearResistance(500)
		self.assertEqual(self.soilProp.AxialProperties.CoyleAndReeseClay.getUltimateShearResistance(), 500)

		self.soilProp.AxialProperties.CoyleAndReeseClay.setE50(10000)
		self.assertEqual(self.soilProp.AxialProperties.CoyleAndReeseClay.getE50(), 10000)

		self.soilProp.AxialProperties.CoyleAndReeseClay.setUltimateEndBearingResistance(150000)
		self.assertEqual(self.soilProp.AxialProperties.CoyleAndReeseClay.getUltimateEndBearingResistance(), 150000)

		self.datumTestHelper(self.soilProp.AxialProperties.CoyleAndReeseClay.Datum, AxialCoyleAndReeseClayDatumProperties)
	#endregion

	#region Axial Elastic Props
	def testAxialElasticProps(self):
		self.soilProp.AxialProperties.Elastic.setSkinFrictionStiffness(30000)
		self.assertEqual(self.soilProp.AxialProperties.Elastic.getSkinFrictionStiffness(), 30000)

		self.soilProp.AxialProperties.Elastic.setEndBearingStiffness(45000)
		self.assertEqual(self.soilProp.AxialProperties.Elastic.getEndBearingStiffness(), 45000)

		self.datumTestHelper(self.soilProp.AxialProperties.Elastic.Datum, AxialElasticDatumProperties)
	#endregion

	#region Axial Mosher Sand Props
	def testAxialMosherSandProps(self):
		self.soilProp.AxialProperties.MosherSand.setFrictionAngle(30.0)
		self.assertEqual(self.soilProp.AxialProperties.MosherSand.getFrictionAngle(), 30.0)

		self.soilProp.AxialProperties.MosherSand.setUseUserDefinedEs(True)
		self.assertTrue(self.soilProp.AxialProperties.MosherSand.getUseUserDefinedEs())

		self.soilProp.AxialProperties.MosherSand.setUserDefinedEs(150)
		self.assertEqual(self.soilProp.AxialProperties.MosherSand.getUserDefinedEs(), 150)

		self.soilProp.AxialProperties.MosherSand.setUltimateShearResistance(25000)
		self.assertEqual(self.soilProp.AxialProperties.MosherSand.getUltimateShearResistance(), 25000)

		self.soilProp.AxialProperties.MosherSand.setUltimateEndBearingResistance(60000)
		self.assertEqual(self.soilProp.AxialProperties.MosherSand.getUltimateEndBearingResistance(), 60000)

		self.datumTestHelper(self.soilProp.AxialProperties.MosherSand.Datum, AxialMosherSandDatumProperties)
	#endregion

	#region Axial User Defined Props
	def testAxialUserDefinedProps(self):
		self.soilProp.AxialProperties.UserDefined.setUltimateUnitSkinFriction(50.0)
		self.assertEqual(self.soilProp.AxialProperties.UserDefined.getUltimateUnitSkinFriction(), 50.0)

		self.soilProp.AxialProperties.UserDefined.setUltimateUnitEndBearingResistance(1200)
		self.assertEqual(self.soilProp.AxialProperties.UserDefined.getUltimateUnitEndBearingResistance(), 1200)

		self.soilProp.AxialProperties.UserDefined.setTZCurve([(2,4), (5,7), (10,12)])
		self.assertEqual(self.soilProp.AxialProperties.UserDefined.getTZCurve(), [(2,4), (5,7), (10,12)])

		self.soilProp.AxialProperties.UserDefined.setQZCurve([(3,5), (6,5), (11,15)])
		self.assertEqual(self.soilProp.AxialProperties.UserDefined.getQZCurve(), [(3,5), (6,5), (11,15)])

		self.datumTestHelper(self.soilProp.AxialProperties.UserDefined.Datum, AxialUserDefinedDatumProperties)
	#endregion

	#region Lateral Soil Props
	def testLateralProps(self):
		for lateralType in LateralType:
			self.soilProp.LateralProperties.setLateralType(lateralType)
			self.assertEqual(self.soilProp.LateralProperties.getLateralType(), lateralType)
	#endregion

	#region Lateral Elastic Props
	def testLateralElasticProps(self):
		self.soilProp.LateralProperties.Elastic.setElasticSubgradeReaction(1500.0)
		self.assertEqual(self.soilProp.LateralProperties.Elastic.getElasticSubgradeReaction(), 1500.0)

		self.datumTestHelper(self.soilProp.LateralProperties.Elastic.Datum, LateralElasticDatumProperties)
	#endregion

	#region Lateral API Sand Props
	def testLateralAPISandProps(self):
		self.soilProp.LateralProperties.APISand.setFrictionAngle(30.0)
		self.assertEqual(self.soilProp.LateralProperties.APISand.getFrictionAngle(), 30.0)

		self.soilProp.LateralProperties.APISand.setInitialModulusOfSubgradeReaction(1000.0)
		self.assertEqual(self.soilProp.LateralProperties.APISand.getInitialModulusOfSubgradeReaction(), 1000.0)

		self.datumTestHelper(self.soilProp.LateralProperties.APISand.Datum, LateralAPISandDatumProperties)
	#endregion

	#region Lateral Dry Stiff Clay Props
	def testLateralDryStiffClayProps(self):
		self.soilProp.LateralProperties.DryStiffClay.setUndrainedShearStrength(150.0)
		self.assertEqual(self.soilProp.LateralProperties.DryStiffClay.getUndrainedShearStrength(), 150.0)

		self.soilProp.LateralProperties.DryStiffClay.setStrainFactor(0.8)
		self.assertEqual(self.soilProp.LateralProperties.DryStiffClay.getStrainFactor(), 0.8)

		self.datumTestHelper(self.soilProp.LateralProperties.DryStiffClay.Datum, LateralDryStiffClayDatumProperties)
	#endregion

	#region Lateral Hybrid Liquefied Sand Props
	def testLateralHybridLiquefiedSandProps(self):
		self.soilProp.LateralProperties.HybridLiquefiedSand.setUseSPT(True)
		self.assertEqual(self.soilProp.LateralProperties.HybridLiquefiedSand.getUseSPT(), True)

		self.soilProp.LateralProperties.HybridLiquefiedSand.setUndrainedShearStrength(250.0)
		self.assertEqual(self.soilProp.LateralProperties.HybridLiquefiedSand.getUndrainedShearStrength(), 250.0)

		self.soilProp.LateralProperties.HybridLiquefiedSand.setStrainFactor(1.2)
		self.assertEqual(self.soilProp.LateralProperties.HybridLiquefiedSand.getStrainFactor(), 1.2)

		self.soilProp.LateralProperties.HybridLiquefiedSand.setSPTValue(30.0)
		self.assertEqual(self.soilProp.LateralProperties.HybridLiquefiedSand.getSPTValue(), 30.0)

		self.datumTestHelper(self.soilProp.LateralProperties.HybridLiquefiedSand.Datum, LateralHybridLiquefiedSandDatumProperties)
	#endregion

	#region Lateral Loess Props
	def testLateralLoessProps(self):
		self.soilProp.LateralProperties.Loess.setConePenetrationTipResistance(120.0)
		self.assertEqual(self.soilProp.LateralProperties.Loess.getConePenetrationTipResistance(), 120.0)

		self.datumTestHelper(self.soilProp.LateralProperties.Loess.Datum, LateralLoessDatumProperties)
	#endregion

	#region Lateral Massive Rock Props
	def testLateralMassiveRockProps(self):
		self.soilProp.LateralProperties.MassiveRock.setModulusType(ModulusType.USE_INTACT_ROCK_MODULUS)
		self.assertEqual(self.soilProp.LateralProperties.MassiveRock.getModulusType(), ModulusType.USE_INTACT_ROCK_MODULUS)

		self.soilProp.LateralProperties.MassiveRock.setModulusType(ModulusType.USE_ROCK_MASS_MODULUS)
		self.assertEqual(self.soilProp.LateralProperties.MassiveRock.getModulusType(), ModulusType.USE_ROCK_MASS_MODULUS)

		#set invalid modulus type
		class InvalidModulusType(Enum):
			INVALID_MODULUS = 100
		with self.assertRaises(ValueError):
			self.soilProp.LateralProperties.MassiveRock.setModulusType(InvalidModulusType.INVALID_MODULUS)

		self.soilProp.LateralProperties.MassiveRock.setIntactRockConstant(0.5)
		self.assertEqual(self.soilProp.LateralProperties.MassiveRock.getIntactRockConstant(), 0.5)

		self.soilProp.LateralProperties.MassiveRock.setGeologicalStrengthIndex(30.0)
		self.assertEqual(self.soilProp.LateralProperties.MassiveRock.getGeologicalStrengthIndex(), 30.0)

		self.soilProp.LateralProperties.MassiveRock.setUniaxialCompressiveStrength(100.0)
		self.assertEqual(self.soilProp.LateralProperties.MassiveRock.getUniaxialCompressiveStrength(), 100.0)

		self.soilProp.LateralProperties.MassiveRock.setIntactRockModulus(2000.0)
		self.assertEqual(self.soilProp.LateralProperties.MassiveRock.getIntactRockModulus(), 2000.0)

		self.soilProp.LateralProperties.MassiveRock.setRockMassModulus(1500.0)
		self.assertEqual(self.soilProp.LateralProperties.MassiveRock.getRockMassModulus(), 1500.0)

		self.soilProp.LateralProperties.MassiveRock.setPoissonRatio(0.25)
		self.assertEqual(self.soilProp.LateralProperties.MassiveRock.getPoissonRatio(), 0.25)

		self.datumTestHelper(self.soilProp.LateralProperties.MassiveRock.Datum, LateralMassiveRockDatumProperties)
	#endregion

	#region Lateral Modified Stiff Clay Without Free Water Props
	def testLateralModifiedStiffClayWithoutFreeWaterProps(self):
		self.soilProp.LateralProperties.ModifiedStiffClayWithoutFreeWater.setStrainFactor(0.1)
		self.assertEqual(self.soilProp.LateralProperties.ModifiedStiffClayWithoutFreeWater.getStrainFactor(), 0.1)

		self.soilProp.LateralProperties.ModifiedStiffClayWithoutFreeWater.setUndrainedShearStrength(50.0)
		self.assertEqual(self.soilProp.LateralProperties.ModifiedStiffClayWithoutFreeWater.getUndrainedShearStrength(), 50.0)

		self.soilProp.LateralProperties.ModifiedStiffClayWithoutFreeWater.setInitialStiffness(2000.0)
		self.assertEqual(self.soilProp.LateralProperties.ModifiedStiffClayWithoutFreeWater.getInitialStiffness(), 2000.0)

		self.datumTestHelper(self.soilProp.LateralProperties.ModifiedStiffClayWithoutFreeWater.Datum, LateralModifiedStiffClayWithoutFreeWaterDatumProperties)
	#endregion

	#region Lateral Sand Properties
	def testLateralSandProperties(self):
		self.soilProp.LateralProperties.Sand.setFrictionAngle(30.0)
		self.assertEqual(self.soilProp.LateralProperties.Sand.getFrictionAngle(), 30.0)

		self.soilProp.LateralProperties.Sand.setKpy(1.2)
		self.assertEqual(self.soilProp.LateralProperties.Sand.getKpy(), 1.2)

		self.soilProp.LateralProperties.Sand.setSaturatedKpy(1.5)
		self.assertEqual(self.soilProp.LateralProperties.Sand.getSaturatedKpy(), 1.5)

		self.datumTestHelper(self.soilProp.LateralProperties.Sand.Datum, LateralSandDatumProperties)
	#endregion

	#region Lateral Silt Properties
	def testLateralSiltProperties(self):
		self.soilProp.LateralProperties.Silt.setCohesion(25.0)
		self.assertEqual(self.soilProp.LateralProperties.Silt.getCohesion(), 25.0)

		self.soilProp.LateralProperties.Silt.setFrictionAngle(28.0)
		self.assertEqual(self.soilProp.LateralProperties.Silt.getFrictionAngle(), 28.0)

		self.soilProp.LateralProperties.Silt.setInitialStiffness(1500.0)
		self.assertEqual(self.soilProp.LateralProperties.Silt.getInitialStiffness(), 1500.0)

		self.datumTestHelper(self.soilProp.LateralProperties.Silt.Datum, LateralSiltDatumProperties)
	#endregion

	#region Lateral Soft Clay Properties
	def testLateralSoftClayProperties(self):
		self.soilProp.LateralProperties.SoftClay.setStrainFactor(0.7)
		self.assertEqual(self.soilProp.LateralProperties.SoftClay.getStrainFactor(), 0.7)

		self.soilProp.LateralProperties.SoftClay.setUndrainedShearStrength(50.0)
		self.assertEqual(self.soilProp.LateralProperties.SoftClay.getUndrainedShearStrength(), 50.0)

		self.datumTestHelper(self.soilProp.LateralProperties.SoftClay.Datum, LateralSoftClayDatumProperties)
	#endregion

	#region Lateral Soft Clay with User Defined J Properties
	def testLateralSoftClayWithUserDefinedJProperties(self):
		self.soilProp.LateralProperties.SoftClayWithUserDefinedJ.setStrainFactor(0.9)
		self.assertEqual(self.soilProp.LateralProperties.SoftClayWithUserDefinedJ.getStrainFactor(), 0.9)

		self.soilProp.LateralProperties.SoftClayWithUserDefinedJ.setUndrainedShearStrength(60.0)
		self.assertEqual(self.soilProp.LateralProperties.SoftClayWithUserDefinedJ.getUndrainedShearStrength(), 60.0)

		self.soilProp.LateralProperties.SoftClayWithUserDefinedJ.setStiffnessFactor(1.2)
		self.assertEqual(self.soilProp.LateralProperties.SoftClayWithUserDefinedJ.getStiffnessFactor(), 1.2)

		self.datumTestHelper(self.soilProp.LateralProperties.SoftClayWithUserDefinedJ.Datum, LateralSoftClayWithUserDefinedJDatumProperties)
	#endregion

	#region Lateral Strong Rock Properties
	def testLateralStrongRockProperties(self):
		self.soilProp.LateralProperties.StrongRock.setUniaxialCompressiveStrength(150.0)
		self.assertEqual(self.soilProp.LateralProperties.StrongRock.getUniaxialCompressiveStrength(), 150.0)

		self.datumTestHelper(self.soilProp.LateralProperties.StrongRock.Datum, LateralStrongRockDatumProperties)
	#endregion

	#region Lateral Submerged Stiff Clay Properties
	def testLateralSubmergedStiffClayProperties(self):
		self.soilProp.LateralProperties.SubmergedStiffClay.setUndrainedShearStrength(80.0)
		self.assertEqual(self.soilProp.LateralProperties.SubmergedStiffClay.getUndrainedShearStrength(), 80.0)

		self.soilProp.LateralProperties.SubmergedStiffClay.setStrainFactor(0.6)
		self.assertEqual(self.soilProp.LateralProperties.SubmergedStiffClay.getStrainFactor(), 0.6)

		self.soilProp.LateralProperties.SubmergedStiffClay.setKs(1.5)
		self.assertEqual(self.soilProp.LateralProperties.SubmergedStiffClay.getKs(), 1.5)

		self.datumTestHelper(self.soilProp.LateralProperties.SubmergedStiffClay.Datum, LateralSubmergedStiffClayDatumProperties)
	#endregion

	#region Lateral Weak Rock Properties
	def testLateralWeakRockProperties(self):
		self.soilProp.LateralProperties.WeakRock.setUniaxialCompressiveStrength(120.0)
		self.assertEqual(self.soilProp.LateralProperties.WeakRock.getUniaxialCompressiveStrength(), 120.0)

		self.soilProp.LateralProperties.WeakRock.setReactionModulusOfRock(2000.0)
		self.assertEqual(self.soilProp.LateralProperties.WeakRock.getReactionModulusOfRock(), 2000.0)

		self.soilProp.LateralProperties.WeakRock.setRockQualityDesignation(50.0)
		self.assertEqual(self.soilProp.LateralProperties.WeakRock.getRockQualityDesignation(), 50.0)

		self.soilProp.LateralProperties.WeakRock.setConstantKrm(0.8)
		self.assertEqual(self.soilProp.LateralProperties.WeakRock.getConstantKrm(), 0.8)

		self.datumTestHelper(self.soilProp.LateralProperties.WeakRock.Datum, LateralWeakRockDatumProperties)
	#endregion

	#region Lateral User Defined Props
	def testLateralUserDefinedProps(self):
		self.soilProp.LateralProperties.UserDefined.setVaryPYCurveByDepth(False)
		self.assertEqual(self.soilProp.LateralProperties.UserDefined.getVaryPYCurveByDepth(), False)

		self.soilProp.LateralProperties.UserDefined.setVaryPYCurveByDepth(True)
		self.assertEqual(self.soilProp.LateralProperties.UserDefined.getVaryPYCurveByDepth(), True)

		self.soilProp.LateralProperties.UserDefined.setPYCurve([(2,4), (5,7), (10,12)])
		self.assertEqual(self.soilProp.LateralProperties.UserDefined.getPYCurve(), [(2,4), (5,7), (10,12)])

		self.soilProp.LateralProperties.UserDefined.setPYCurveBottom([(3,5), (6,5), (11,15)])
		self.assertEqual(self.soilProp.LateralProperties.UserDefined.getPYCurveBottom(), [(3,5), (6,5), (11,15)])
	#endregion

#region Lateral Piedmont Residual Soils Props
	def testLateralPiedmontResidualProps(self):

		for analysisType in PiedmontTestValueType:
			self.soilProp.LateralProperties.PiedmontResidual.setPiedmontAnalysisType(analysisType)
			self.assertEqual(self.soilProp.LateralProperties.PiedmontResidual.getPiedmontAnalysisType(), analysisType)

		self.soilProp.LateralProperties.PiedmontResidual.setDilatometerModulus(27.0)
		self.assertEqual(self.soilProp.LateralProperties.PiedmontResidual.getDilatometerModulus(),  27.0)
		
		self.soilProp.LateralProperties.PiedmontResidual.setConePenetrationTipResistance(13.0)
		self.assertEqual(self.soilProp.LateralProperties.PiedmontResidual.getConePenetrationTipResistance(), 13.0)
		
		self.soilProp.LateralProperties.PiedmontResidual.setMenardPressuremeterModulus(7.1)
		self.assertEqual(self.soilProp.LateralProperties.PiedmontResidual.getMenardPressuremeterModulus(), 7.1)

		self.soilProp.LateralProperties.PiedmontResidual.setStandardPenetrationBlowCount(150)
		self.assertEqual(self.soilProp.LateralProperties.PiedmontResidual.getStandardPenetrationBlowCount(), 150)

		self.datumTestHelper(self.soilProp.LateralProperties.PiedmontResidual.Datum, LateralPiedmontResidualDatumProperties)
 #endregion

 #region Bored Soil Properties
	def testBoredSoilProperties(self):
		# Test BoredSoilType set and get functionality
		for soilType in BoredType:
			self.soilProp.BoredProperties.setBoredSoilType(soilType)
			self.assertEqual(self.soilProp.BoredProperties.getBoredSoilType(), soilType)

		# Test enabling and disabling reduction factors
		self.soilProp.BoredProperties.setUseReductionFactors(True)
		self.assertTrue(self.soilProp.BoredProperties.getUseReductionFactors())

		self.soilProp.BoredProperties.setUseReductionFactors(False)
		self.assertFalse(self.soilProp.BoredProperties.getUseReductionFactors())

		# Test setting and getting skin resistance loss
		self.soilProp.BoredProperties.setSkinResistanceLoss(10.5)
		self.assertEqual(self.soilProp.BoredProperties.getSkinResistanceLoss(), 10.5)

		# Test setting and getting end bearing loss
		self.soilProp.BoredProperties.setEndBearingLoss(5.0)
		self.assertEqual(self.soilProp.BoredProperties.getEndBearingLoss(), 5.0)
#endregion

#region Bored Cohesive Properties
	def testCohesiveProperties(self):
		# Test CohesiveType set and get functionality
		for cohesiveMethod in CohesiveMethod:
			self.soilProp.BoredProperties.Cohesive.setCohesiveMethod(cohesiveMethod)
			self.assertEqual(self.soilProp.BoredProperties.Cohesive.getCohesiveMethod(), cohesiveMethod)
#endregion

#region Bored Cohesive Effective Stress Properties
	def testBoredCohesiveEffectiveStressProperties(self):
		self.soilProp.BoredProperties.Cohesive.EffectiveStress.setBeta(5.0)
		self.assertEqual(self.soilProp.BoredProperties.Cohesive.EffectiveStress.getBeta(), 5.0)

		self.soilProp.BoredProperties.Cohesive.EffectiveStress.setSkinFrictionLimit(3.5)
		self.assertEqual(self.soilProp.BoredProperties.Cohesive.EffectiveStress.getSkinFrictionLimit(), 3.5)

		self.soilProp.BoredProperties.Cohesive.EffectiveStress.setEndBearingLimit(2.8)
		self.assertEqual(self.soilProp.BoredProperties.Cohesive.EffectiveStress.getEndBearingLimit(), 2.8)

		self.soilProp.BoredProperties.Cohesive.EffectiveStress.setEffectiveCohesion(1.5)
		self.assertEqual(self.soilProp.BoredProperties.Cohesive.EffectiveStress.getEffectiveCohesion(), 1.5)

		self.soilProp.BoredProperties.Cohesive.EffectiveStress.setBearingCapacityFactorNc(4.2)
		self.assertEqual(self.soilProp.BoredProperties.Cohesive.EffectiveStress.getBearingCapacityFactorNc(), 4.2)

		self.soilProp.BoredProperties.Cohesive.EffectiveStress.setBearingCapacityFactorNq(6.1)
		self.assertEqual(self.soilProp.BoredProperties.Cohesive.EffectiveStress.getBearingCapacityFactorNq(), 6.1)
#endregion

	#region Bored Cohesive Total Stress Properties
	def testBoredCohesiveTotalStressProperties(self):
		self.soilProp.BoredProperties.Cohesive.TotalStress.setUndrainedShearStrength(5.1)
		self.assertEqual(self.soilProp.BoredProperties.Cohesive.TotalStress.getUndrainedShearStrength(), 5.1)

		self.soilProp.BoredProperties.Cohesive.TotalStress.setAlpha(3.6)
		self.assertEqual(self.soilProp.BoredProperties.Cohesive.TotalStress.getAlpha(), 3.6)

		self.soilProp.BoredProperties.Cohesive.TotalStress.setSkinFrictionLimit(2.7)
		self.assertEqual(self.soilProp.BoredProperties.Cohesive.TotalStress.getSkinFrictionLimit(), 2.7)

		self.soilProp.BoredProperties.Cohesive.TotalStress.setEndBearingLimit(1.9)
		self.assertEqual(self.soilProp.BoredProperties.Cohesive.TotalStress.getEndBearingLimit(), 1.9)

		self.soilProp.BoredProperties.Cohesive.TotalStress.setBearingCapacityFactorNc(4.5)
		self.assertEqual(self.soilProp.BoredProperties.Cohesive.TotalStress.getBearingCapacityFactorNc(), 4.5)
	#endregion

#region Bored Cohesionless Properties
	def testBoredCohesionlessProperties(self):
		for cohesionless_type in CohesionlessType:
			self.soilProp.BoredProperties.Cohesionless.setCohesionlessType(cohesionless_type)
			self.assertEqual(self.soilProp.BoredProperties.Cohesionless.getCohesionlessType(), cohesionless_type)

		for setInternalFrictionAngleMethod in InternalFrictionAngleMethod:
			self.soilProp.BoredProperties.Cohesionless.setInternalFrictionAngleMethod(setInternalFrictionAngleMethod)
			self.assertEqual(self.soilProp.BoredProperties.Cohesionless.getInternalFrictionAngleMethod(), setInternalFrictionAngleMethod)

		class InvalidInternalFrictionAngleMethod(Enum):
			INVALID_METHOD = 100
		# test invalid internal friction angle method
		with self.assertRaises(ValueError):
			self.soilProp.BoredProperties.Cohesionless.setInternalFrictionAngleMethod(InvalidInternalFrictionAngleMethod.INVALID_METHOD)

		self.soilProp.BoredProperties.Cohesionless.setSkinFrictionAngle(10.5)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.getSkinFrictionAngle(), 10.5)

		self.soilProp.BoredProperties.Cohesionless.setEndBearingAngle(15.0)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.getEndBearingAngle(), 15.0)
#endregion

#region SPT Table Properties
	def testBoredCohesionlessBoredSPTTableProperties(self):
		test_spt_table = [(5.0, 15.0), (10.0, 30.0), (15.0, 45.0)]
		self.soilProp.BoredProperties.Cohesionless.SPTTable.setSPTTable(test_spt_table)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.SPTTable.getSPTTable(), test_spt_table)
	#endregion

#region Bored Cohesionless BetaNQ Properties
	def testBoredCohesionlessBetaNQProperties(self):
		self.soilProp.BoredProperties.Cohesionless.BetaNQ.setBeta(1.2)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.BetaNQ.getBeta(), 1.2)

		self.soilProp.BoredProperties.Cohesionless.BetaNQ.setBearingCapacityFactorNq(5.6)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.BetaNQ.getBearingCapacityFactorNq(), 5.6)

		self.soilProp.BoredProperties.Cohesionless.BetaNQ.setUseAutoBearingCapacityFactorNq(True)
		self.assertTrue(self.soilProp.BoredProperties.Cohesionless.BetaNQ.getUseAutoBearingCapacityFactorNq())

		self.soilProp.BoredProperties.Cohesionless.BetaNQ.setSkinFrictionLimit(3.5)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.BetaNQ.getSkinFrictionLimit(), 3.5)

		self.soilProp.BoredProperties.Cohesionless.BetaNQ.setEndBearingLimit(10.2)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.BetaNQ.getEndBearingLimit(), 10.2)
#endregion

#region Bored Cohesionless KsDelta Properties
	def testBoredCohesionlessKsDeltaProperties(self):
		self.soilProp.BoredProperties.Cohesionless.KsDelta.setOCR(1.5)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.KsDelta.getOCR(), 1.5)

		self.soilProp.BoredProperties.Cohesionless.KsDelta.setKsKoRatio(0.8)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.KsDelta.getKsKoRatio(), 0.8)

		self.soilProp.BoredProperties.Cohesionless.KsDelta.setDeltaPhiRatio(20.0)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.KsDelta.getDeltaPhiRatio(), 20.0)

		self.soilProp.BoredProperties.Cohesionless.KsDelta.setUseAutoBearingCapacityFactorNq(True)
		self.assertTrue(self.soilProp.BoredProperties.Cohesionless.KsDelta.getUseAutoBearingCapacityFactorNq())

		self.soilProp.BoredProperties.Cohesionless.KsDelta.setBearingCapacityFactorNq(10.5)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.KsDelta.getBearingCapacityFactorNq(), 10.5)

		self.soilProp.BoredProperties.Cohesionless.KsDelta.setSkinFrictionLimit(3.7)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.KsDelta.getSkinFrictionLimit(), 3.7)

		self.soilProp.BoredProperties.Cohesionless.KsDelta.setEndBearingLimit(12.3)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.KsDelta.getEndBearingLimit(), 12.3)
#endregion

#region Bored Cohesionless SPTAASHTO Properties
	def testBoredCohesionlessSPTAASHTOProperties(self):
		self.soilProp.BoredProperties.Cohesionless.SPTAASHTO.setSkinFrictionLimit(4.5)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.SPTAASHTO.getSkinFrictionLimit(), 4.5)

		self.soilProp.BoredProperties.Cohesionless.SPTAASHTO.setEndBearingLimit(15.2)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.SPTAASHTO.getEndBearingLimit(), 15.2)
#endregion

#region Bored Cohesionless SPTUserFactors Properties
	def testBoredCohesionlessSPTUserFactorsProperties(self):
		self.soilProp.BoredProperties.Cohesionless.SPTUserFactors.setA(2.5)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.SPTUserFactors.getA(), 2.5)

		self.soilProp.BoredProperties.Cohesionless.SPTUserFactors.setB(3.5)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.SPTUserFactors.getB(), 3.5)

		self.soilProp.BoredProperties.Cohesionless.SPTUserFactors.setC(4.5)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.SPTUserFactors.getC(), 4.5)

		self.soilProp.BoredProperties.Cohesionless.SPTUserFactors.setD(5.5)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.SPTUserFactors.getD(), 5.5)

		self.soilProp.BoredProperties.Cohesionless.SPTUserFactors.setSkinFrictionLimit(6.5)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.SPTUserFactors.getSkinFrictionLimit(), 6.5)

		self.soilProp.BoredProperties.Cohesionless.SPTUserFactors.setEndBearingLimit(7.5)
		self.assertEqual(self.soilProp.BoredProperties.Cohesionless.SPTUserFactors.getEndBearingLimit(), 7.5)
#endregion

#region Bored WeakRock Properties
	def testWeakRockProperties(self):
		self.soilProp.BoredProperties.WeakRock.setUnconfinedCompressiveStrength(10.0)
		self.assertEqual(self.soilProp.BoredProperties.WeakRock.getUnconfinedCompressiveStrength(), 10.0)

		self.soilProp.BoredProperties.WeakRock.setSkinFrictionLimit(15.0)
		self.assertEqual(self.soilProp.BoredProperties.WeakRock.getSkinFrictionLimit(), 15.0)

		self.soilProp.BoredProperties.WeakRock.setEndBearingLimit(20.0)
		self.assertEqual(self.soilProp.BoredProperties.WeakRock.getEndBearingLimit(), 20.0)
#endregion

#region Bored Weak Rock Skin Resistance Properties
	def testBoredWeakRockSkinResistanceProperties(self):
		for resistanceMethod in SkinResistanceMethod:
			self.soilProp.BoredProperties.WeakRock.SkinResistance.setSkinResistanceMethod(resistanceMethod)
			self.assertEqual(self.soilProp.BoredProperties.WeakRock.SkinResistance.getSkinResistanceMethod(), resistanceMethod)
#endregion

#region Bored Weak Rock Skin Resistance Kulhawy And Phoon Properties
	def testBoredWeakRockulhawyAndPhoonProperties(self):
		self.soilProp.BoredProperties.WeakRock.SkinResistance.KulhawyAndPhoon.setChi(15.7)
		self.assertEqual(self.soilProp.BoredProperties.WeakRock.SkinResistance.KulhawyAndPhoon.getChi(), 15.7)
#endregion

#region Bored Weak Rock Skin Resistance William And Pells Properties
	def testBoredWeakRockWilliamAndPellsProperties(self):
		self.soilProp.BoredProperties.WeakRock.SkinResistance.WilliamAndPells.setAverageRQD(25.3)
		self.assertEqual(self.soilProp.BoredProperties.WeakRock.SkinResistance.WilliamAndPells.getAverageRQD(), 25.3)
#endregion

#region Bored Weak Rock Tip Resistance Properties
	def testBoredWeakRockTipResistanceProperties(self):
		for tipResistanceMethod in TipResistanceMethod:
			self.soilProp.BoredProperties.WeakRock.TipResistance.setTipResistanceMethod(tipResistanceMethod)
			self.assertEqual(self.soilProp.BoredProperties.WeakRock.TipResistance.getTipResistanceMethod(), tipResistanceMethod)
#endregion

#region Bored Weak Rock Tomlinson And Woodward Properties
	def testBoredWeakRockTomlinsonAndWoodwardProperties(self):
		self.soilProp.BoredProperties.WeakRock.TipResistance.TomlinsonAndWoodward.setInternalFrictionAngle(30)
		self.assertEqual(self.soilProp.BoredProperties.WeakRock.TipResistance.TomlinsonAndWoodward.getInternalFrictionAngle(), 30)
#endregion

#region Bored Weak Rock Tip Resistance User Defined B Properties
	def testBoredWeakRockUserDefinedBProperties(self):
		self.soilProp.BoredProperties.WeakRock.TipResistance.UserDefinedB.setB(20.5)
		self.assertEqual(self.soilProp.BoredProperties.WeakRock.TipResistance.UserDefinedB.getB(), 20.5)
#endregion

#region Driven Soil Properties
	def testDrivenSoilProperties(self):
		for driven_type in DrivenType:
			self.soilProp.DrivenProperties.setDrivenSoilType(driven_type)
			self.assertEqual(self.soilProp.DrivenProperties.getDrivenSoilType(), driven_type)

		self.soilProp.DrivenProperties.setDrivingStrengthLoss(5.0)
		self.assertEqual(self.soilProp.DrivenProperties.getDrivingStrengthLoss(), 5.0)
#endregion

#region Driven Cohesionless Properties
	def testDrivenCohesionlessProperties(self):
		for method in InternalFrictionAngleMethod:
			self.soilProp.DrivenProperties.Cohesionless.setInternalFrictionAngleSkinFrictionMethod(method)
			self.assertEqual(self.soilProp.DrivenProperties.Cohesionless.getInternalFrictionAngleSkinFrictionMethod(), method)

		class InvalidInternalFrictionAngleMethod(Enum):
			INVALID_METHOD = 100
		# test invalid internal friction angle method
		with self.assertRaises(ValueError):
			self.soilProp.DrivenProperties.Cohesionless.setInternalFrictionAngleSkinFrictionMethod(InvalidInternalFrictionAngleMethod.INVALID_METHOD)

		for method in InternalFrictionAngleMethod:
			self.soilProp.DrivenProperties.Cohesionless.setInternalFrictionAngleEndBearingMethod(method)
			self.assertEqual(self.soilProp.DrivenProperties.Cohesionless.getInternalFrictionAngleEndBearingMethod(), method)

		# test invalid internal friction angle method
		with self.assertRaises(ValueError):
			self.soilProp.DrivenProperties.Cohesionless.setInternalFrictionAngleEndBearingMethod(InvalidInternalFrictionAngleMethod.INVALID_METHOD)

		self.soilProp.DrivenProperties.Cohesionless.setSkinFrictionAngle(15.0)
		self.assertEqual(self.soilProp.DrivenProperties.Cohesionless.getSkinFrictionAngle(), 15.0)

		self.soilProp.DrivenProperties.Cohesionless.setEndBearingAngle(25.0)
		self.assertEqual(self.soilProp.DrivenProperties.Cohesionless.getEndBearingAngle(), 25.0)
#endregion

#region End Bearing SPT Table Properties
	def testDrivenEndBearingSPTTableProperties(self):
		test_spt_table = [(5.0, 15.0), (10.0, 30.0), (15.0, 45.0)]
		self.soilProp.DrivenProperties.Cohesionless.EndBearingSPTTable.setSPTTable(test_spt_table)
		self.assertEqual(self.soilProp.DrivenProperties.Cohesionless.EndBearingSPTTable.getSPTTable(), test_spt_table)

		self.soilProp.DrivenProperties.Cohesionless.EndBearingSPTTable.setUseSPTCorrectionForOverburdenPressure(True)
		self.assertTrue(self.soilProp.DrivenProperties.Cohesionless.EndBearingSPTTable.getUseSPTCorrectionForOverburdenPressure())

		self.soilProp.DrivenProperties.Cohesionless.SkinFrictionSPTTable.setUseSPTCorrectionForOverburdenPressure(False)
		self.assertFalse(self.soilProp.DrivenProperties.Cohesionless.SkinFrictionSPTTable.getUseSPTCorrectionForOverburdenPressure())
#endregion

#region Skin Friction SPT Table Properties
	def testDrivenSkinFrictionSPTTableProperties(self):
		test_spt_table = [(5.0, 15.0), (10.0, 30.0), (15.0, 45.0)]
		self.soilProp.DrivenProperties.Cohesionless.SkinFrictionSPTTable.setSPTTable(test_spt_table)
		self.assertEqual(self.soilProp.DrivenProperties.Cohesionless.SkinFrictionSPTTable.getSPTTable(), test_spt_table)

		self.soilProp.DrivenProperties.Cohesionless.SkinFrictionSPTTable.setUseSPTCorrectionForOverburdenPressure(True)
		self.assertTrue(self.soilProp.DrivenProperties.Cohesionless.SkinFrictionSPTTable.getUseSPTCorrectionForOverburdenPressure())

		self.soilProp.DrivenProperties.Cohesionless.SkinFrictionSPTTable.setUseSPTCorrectionForOverburdenPressure(False)
		self.assertFalse(self.soilProp.DrivenProperties.Cohesionless.SkinFrictionSPTTable.getUseSPTCorrectionForOverburdenPressure())
#endregion

#region Driven Cohesive Properties
	def testDrivenCohesiveType(self):
		for cohesive_type in AdhesionType:
			self.soilProp.DrivenProperties.Cohesive.setAdhesionType(cohesive_type)
			self.assertEqual(self.soilProp.DrivenProperties.Cohesive.getAdhesionType(), cohesive_type)
			
		self.soilProp.DrivenProperties.Cohesive.setUndrainedShearStrength(55.6)
		self.assertEqual(self.soilProp.DrivenProperties.Cohesive.getUndrainedShearStrength(), 55.6)
		
#endregion

#region Driven Cohesive User-Defined Adhesion Properties
	def testDrivenCohesiveUserDefinedAdhesionProperties(self):
		self.soilProp.DrivenProperties.Cohesive.UserDefinedAdhesion.setAdhesion(12.5)
		self.assertEqual(self.soilProp.DrivenProperties.Cohesive.UserDefinedAdhesion.getAdhesion(), 12.5)
#endregion

#region test Helical Properties
	def testHelicalProperties(self):
		for type in HelicalType:
			self.soilProp.HelicalProperties.setHelicalSoilType(type)
			self.assertEqual(self.soilProp.HelicalProperties.getHelicalSoilType(), type)
#endregion

#region test Helical Cohesive Properties
	def testHelicalCohesiveProperties(self):
		self.soilProp.HelicalProperties.Cohesive.setUndrainedShearStrength(43.7)
		self.assertEqual(self.soilProp.HelicalProperties.Cohesive.getUndrainedShearStrength(), 43.7)

		self.soilProp.HelicalProperties.Cohesive.setNcPrime(0.09)
		self.assertEqual(self.soilProp.HelicalProperties.Cohesive.getNcPrime(), 0.09)

		self.soilProp.HelicalProperties.Cohesive.setAdhesionFactorForShaft(1.8)
		self.assertEqual(self.soilProp.HelicalProperties.Cohesive.getAdhesionFactorForShaft(), 1.8)
#endregion

#region test Helical Cohesionless Properties
	def testHelicalCohesionlessProperties(self):
		self.soilProp.HelicalProperties.Cohesionless.setInternalFrictionAngle(38.8)
		self.assertEqual(self.soilProp.HelicalProperties.Cohesionless.getInternalFrictionAngle(), 38.8)

		self.soilProp.HelicalProperties.Cohesionless.setCoefficientOfLateralEarthPressureForShaft(1.2)
		self.assertEqual(self.soilProp.HelicalProperties.Cohesionless.getCoefficientOfLateralEarthPressureForShaft(), 1.2)

		self.soilProp.HelicalProperties.Cohesionless.setFrictionAngleBetweenShaftAndSoil(21.6)
		self.assertEqual(self.soilProp.HelicalProperties.Cohesionless.getFrictionAngleBetweenShaftAndSoil(), 21.6)

		self.soilProp.HelicalProperties.Cohesionless.setFrictionAngleBetweenShaftAndSoil(21.6)
#endregion

if __name__ == '__main__':
	unittest.main(verbosity=2)