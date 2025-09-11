import unittest
from RSPileScripting.RSPileModeler import RSPileModeler
from RSPileScripting.enums import *

from dotenv import load_dotenv
import shutil
import os

class BaseProjectSettingsTest(unittest.TestCase):
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
		self.projectSettings = self.model.ProjectSettings

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

class TestGeneralProjectSettings(BaseProjectSettingsTest):
	"""Test group for general project settings functionality"""
	
	def testGetUnitsDefault(self):
		"""Test that we can get the default units from project settings"""
		units = self.projectSettings.General.getUnits()
		self.assertIsInstance(units, Units)
		self.assertIn(units, [Units.SI_Metric, Units.USCS_Imperial])

	def testSetAndGetUnitsSI_Metric(self):
		"""Test setting and getting SI Metric units"""
		# Set units to SI Metric
		self.projectSettings.General.setUnits(Units.SI_Metric, True)
		
		# Verify the units were set correctly
		retrieved_units = self.projectSettings.General.getUnits()
		self.assertEqual(retrieved_units, Units.SI_Metric)
		
		# Save and reload to verify persistence
		self.model.save()
		self.model.close()
		
		self.model = self.modeler.openFile(self.copy_file)
		self.projectSettings = self.model.ProjectSettings
		
		persisted_units = self.projectSettings.General.getUnits()
		self.assertEqual(persisted_units, Units.SI_Metric)

	def testSetAndGetUnitsUSCS_Imperial(self):
		"""Test setting and getting USCS Imperial units"""
		# Set units to USCS Imperial
		self.projectSettings.General.setUnits(Units.USCS_Imperial, True)
		
		# Verify the units were set correctly
		retrieved_units = self.projectSettings.General.getUnits()
		self.assertEqual(retrieved_units, Units.USCS_Imperial)
		
		# Save and reload to verify persistence
		self.model.save()
		self.model.close()
		
		self.model = self.modeler.openFile(self.copy_file)
		self.projectSettings = self.model.ProjectSettings
		
		persisted_units = self.projectSettings.General.getUnits()
		self.assertEqual(persisted_units, Units.USCS_Imperial)

	def testSetUnitsWithResetValuesTrue(self):
		"""Test setting units with resetValues=True (default)"""
  
		soilProp = self.model.getSoilProperties()[0]
  
		originalSaturatedUnitWeight = soilProp.getSaturatedUnitWeight()

		soilProp.setSaturatedUnitWeight(originalSaturatedUnitWeight + 1)
		self.assertEqual(soilProp.getSaturatedUnitWeight(), originalSaturatedUnitWeight + 1) #verify that the soil property was set correctly

		# Set units with default resetValues=True
		self.projectSettings.General.setUnits(Units.USCS_Imperial, True)
		
		# Verify the units were set correctly
		retrieved_units = self.projectSettings.General.getUnits()
		self.assertEqual(retrieved_units, Units.USCS_Imperial)
		self.assertNotEqual(soilProp.getSaturatedUnitWeight(), originalSaturatedUnitWeight) #should be set to the default value of imperial now

	def testSetUnitsWithResetValuesFalse(self):
		"""Test setting units with resetValues=False"""
		# Set units with resetValues=False
  
		soilProp = self.model.getSoilProperties()[0]
  
		originalSaturatedUnitWeight = soilProp.getSaturatedUnitWeight()

		soilProp.setSaturatedUnitWeight(originalSaturatedUnitWeight + 1)
		self.assertEqual(soilProp.getSaturatedUnitWeight(), originalSaturatedUnitWeight + 1) #verify that the soil property was set correctly

		# Set units with default resetValues=True
		self.projectSettings.General.setUnits(Units.USCS_Imperial, False)
		
		# Verify the units were set correctly
		retrieved_units = self.projectSettings.General.getUnits()
		self.assertEqual(retrieved_units, Units.USCS_Imperial)
		self.assertEqual(soilProp.getSaturatedUnitWeight(), originalSaturatedUnitWeight + 1)

	def testGetProgramModeDefault(self):
		"""Test that we can get the default program mode from project settings"""
		program_mode = self.projectSettings.General.getProgramMode()
		self.assertIsInstance(program_mode, ProgramModeSelection)
		self.assertIn(program_mode, [ProgramModeSelection.PileAnalysis, ProgramModeSelection.CapacityCalcuations])

	def testSetAndGetProgramModePileAnalysis(self):
		"""Test setting and getting Pile Analysis program mode"""
		# Set program mode to Pile Analysis
		# First, get the current program mode
		initial_program_mode = self.projectSettings.General.getProgramMode()
		self.assertIn(initial_program_mode, [ProgramModeSelection.PileAnalysis, ProgramModeSelection.CapacityCalcuations])

		# Pick the other option that is not the initial_program_mode
		if initial_program_mode == ProgramModeSelection.PileAnalysis:
			first_option = ProgramModeSelection.CapacityCalcuations
		else:
			first_option = ProgramModeSelection.PileAnalysis
		second_option = initial_program_mode

		# Set to the first option (not already set)
		self.projectSettings.General.setProgramMode(first_option)
		retrieved_program_mode = self.projectSettings.General.getProgramMode()
		self.assertEqual(retrieved_program_mode, first_option)

		# Save and reload to verify persistence
		self.model.save()
		self.model.close()
		self.model = self.modeler.openFile(self.copy_file)
		self.projectSettings = self.model.ProjectSettings
		persisted_program_mode = self.projectSettings.General.getProgramMode()
		self.assertEqual(persisted_program_mode, first_option)

		# Now set to the second option (the original one)
		self.projectSettings.General.setProgramMode(second_option)
		retrieved_program_mode_2 = self.projectSettings.General.getProgramMode()
		self.assertEqual(retrieved_program_mode_2, second_option)

		# Save and reload to verify persistence again
		self.model.save()
		self.model.close()
		self.model = self.modeler.openFile(self.copy_file)
		self.projectSettings = self.model.ProjectSettings
		persisted_program_mode_2 = self.projectSettings.General.getProgramMode()
		self.assertEqual(persisted_program_mode_2, second_option)

class TestCapacityCalculations(BaseProjectSettingsTest):
	"""Test group for capacity calculations functionality"""
	
	def setUp(self):
		"""Set up capacity calculations tests with program mode set to capacity calculations"""
		super().setUp()
		# Set program mode to capacity calculations for all capacity calculation tests
		self.projectSettings.General.setProgramMode(ProgramModeSelection.CapacityCalcuations)
	
	def testGetCapacityCalculationTypeDefault(self):
		"""Test that we can get the default capacity calculation type from project settings"""
		capacity_calc_type = self.projectSettings.CapacityCalculations.getCapacityCalculationType()
		self.assertIsInstance(capacity_calc_type, CapacityCalculationType)
		self.assertIn(capacity_calc_type, [CapacityCalculationType.Driven, CapacityCalculationType.Bored, 
										  CapacityCalculationType.Helical, CapacityCalculationType.CapacityTableGenerator])

	def testSetAndGetCapacityCalculationType(self):
		"""Test setting and getting capacity calculation type"""
		# Get the current capacity calculation type
		initial_calc_type = self.projectSettings.CapacityCalculations.getCapacityCalculationType()
		self.assertIn(initial_calc_type, [CapacityCalculationType.Driven, CapacityCalculationType.Bored, 
										 CapacityCalculationType.Helical, CapacityCalculationType.CapacityTableGenerator])

		# Pick a different option that is not the initial_calc_type
		available_types = [CapacityCalculationType.Driven, CapacityCalculationType.Bored, 
						  CapacityCalculationType.Helical, CapacityCalculationType.CapacityTableGenerator]
		other_types = [t for t in available_types if t != initial_calc_type]
		first_option = other_types[0]
		second_option = initial_calc_type

		# Set to the first option (not already set)
		self.projectSettings.CapacityCalculations.setCapacityCalculationType(first_option)
		retrieved_calc_type = self.projectSettings.CapacityCalculations.getCapacityCalculationType()
		self.assertEqual(retrieved_calc_type, first_option)

		# Save and reload to verify persistence
		self.model.save()
		self.model.close()
		self.model = self.modeler.openFile(self.copy_file)
		self.projectSettings = self.model.ProjectSettings
		persisted_calc_type = self.projectSettings.CapacityCalculations.getCapacityCalculationType()
		self.assertEqual(persisted_calc_type, first_option)

		# Now set to the second option (the original one)
		self.projectSettings.CapacityCalculations.setCapacityCalculationType(second_option)
		retrieved_calc_type_2 = self.projectSettings.CapacityCalculations.getCapacityCalculationType()
		self.assertEqual(retrieved_calc_type_2, second_option)

		# Save and reload to verify persistence again
		self.model.save()
		self.model.close()
		self.model = self.modeler.openFile(self.copy_file)
		self.projectSettings = self.model.ProjectSettings
		persisted_calc_type_2 = self.projectSettings.CapacityCalculations.getCapacityCalculationType()
		self.assertEqual(persisted_calc_type_2, second_option)

	def testHelicalPileOptionsGetAndSetProperties(self):
		"""Test getting and setting helical pile options properties"""
		# First set capacity calculation type to Helical to enable helical options
		self.projectSettings.CapacityCalculations.setCapacityCalculationType(CapacityCalculationType.Helical)
		
		helical_options = self.projectSettings.CapacityCalculations.HelicalPileOptions
		
		# Test IsIncludeShaftAdhesionFriction
		initial_shaft_adhesion = helical_options.getIsIncludeShaftAdhesionFriction()
		helical_options.setIsIncludeShaftAdhesionFriction(not initial_shaft_adhesion)
		retrieved_shaft_adhesion = helical_options.getIsIncludeShaftAdhesionFriction()
		self.assertEqual(retrieved_shaft_adhesion, not initial_shaft_adhesion)
		
		# Test IsApplyLocalShearFailureForHelices
		initial_local_shear = helical_options.getIsApplyLocalShearFailureForHelices()
		helical_options.setIsApplyLocalShearFailureForHelices(not initial_local_shear)
		retrieved_local_shear = helical_options.getIsApplyLocalShearFailureForHelices()
		self.assertEqual(retrieved_local_shear, not initial_local_shear)
		
		# Test IsUseReducedHelixAreaForEndBearing
		initial_reduced_helix = helical_options.getIsUseReducedHelixAreaForEndBearing()
		helical_options.setIsUseReducedHelixAreaForEndBearing(not initial_reduced_helix)
		retrieved_reduced_helix = helical_options.getIsUseReducedHelixAreaForEndBearing()
		self.assertEqual(retrieved_reduced_helix, not initial_reduced_helix)
		
		# Test IsIncludeShapeAndDepthFactors
		initial_shape_depth = helical_options.getIsIncludeShapeAndDepthFactors()
		helical_options.setIsIncludeShapeAndDepthFactors(not initial_shape_depth)
		retrieved_shape_depth = helical_options.getIsIncludeShapeAndDepthFactors()
		self.assertEqual(retrieved_shape_depth, not initial_shape_depth)
		
		# Save and reload to verify persistence
		self.model.save()
		self.model.close()
		self.model = self.modeler.openFile(self.copy_file)
		self.projectSettings = self.model.ProjectSettings
		
		# Verify all properties persisted correctly
		helical_options = self.projectSettings.CapacityCalculations.HelicalPileOptions
		self.assertEqual(helical_options.getIsIncludeShaftAdhesionFriction(), not initial_shaft_adhesion)
		self.assertEqual(helical_options.getIsApplyLocalShearFailureForHelices(), not initial_local_shear)
		self.assertEqual(helical_options.getIsUseReducedHelixAreaForEndBearing(), not initial_reduced_helix)
		self.assertEqual(helical_options.getIsIncludeShapeAndDepthFactors(), not initial_shape_depth)

	def testCapacityTableGeneratorOptionsGetAndSetProperties(self):
		"""Test getting and setting capacity table generator options properties"""
		# First set capacity calculation type to CapacityTableGenerator to enable these options
		self.projectSettings.CapacityCalculations.setCapacityCalculationType(CapacityCalculationType.CapacityTableGenerator)
		
		capacity_table_options = self.projectSettings.CapacityCalculations.CapacityTableGeneratorOptions
		
		# Test IsTotalCapacity
		initial_total_capacity = capacity_table_options.getIsTotalCapacity()
		capacity_table_options.setIsTotalCapacity(not initial_total_capacity)
		retrieved_total_capacity = capacity_table_options.getIsTotalCapacity()
		self.assertEqual(retrieved_total_capacity, not initial_total_capacity)
		
		# Test IsSkinFriction
		initial_skin_friction = capacity_table_options.getIsSkinFriction()
		capacity_table_options.setIsSkinFriction(not initial_skin_friction)
		retrieved_skin_friction = capacity_table_options.getIsSkinFriction()
		self.assertEqual(retrieved_skin_friction, not initial_skin_friction)
		
		# Test IsSkinFrictionEndBearing
		initial_skin_friction_end_bearing = capacity_table_options.getIsSkinFrictionEndBearing()
		capacity_table_options.setIsSkinFrictionEndBearing(not initial_skin_friction_end_bearing)
		retrieved_skin_friction_end_bearing = capacity_table_options.getIsSkinFrictionEndBearing()
		self.assertEqual(retrieved_skin_friction_end_bearing, not initial_skin_friction_end_bearing)
		
		# Test FS1 (requires total capacity to be true)
		capacity_table_options.setIsTotalCapacity(True)
		initial_fs1 = capacity_table_options.getFS1()
		new_fs1 = initial_fs1 + 0.5
		capacity_table_options.setFS1(new_fs1)
		retrieved_fs1 = capacity_table_options.getFS1()
		self.assertEqual(retrieved_fs1, new_fs1)
		
		# Test FS2 (requires skin friction to be true)
		capacity_table_options.setIsSkinFriction(True)
		initial_fs2 = capacity_table_options.getFS2()
		new_fs2 = initial_fs2 + 0.6
		capacity_table_options.setFS2(new_fs2)
		retrieved_fs2 = capacity_table_options.getFS2()
		self.assertEqual(retrieved_fs2, new_fs2)
		
		# Test FS3 (requires skin friction end bearing to be true)
		capacity_table_options.setIsSkinFrictionEndBearing(True)
		initial_fs3 = capacity_table_options.getFS3()
		new_fs3 = initial_fs3 + 0.7
		capacity_table_options.setFS3(new_fs3)
		retrieved_fs3 = capacity_table_options.getFS3()
		self.assertEqual(retrieved_fs3, new_fs3)
		
		# Test FS4 (requires skin friction end bearing to be true)
		initial_fs4 = capacity_table_options.getFS4()
		new_fs4 = initial_fs4 + 0.8
		capacity_table_options.setFS4(new_fs4)
		retrieved_fs4 = capacity_table_options.getFS4()
		self.assertEqual(retrieved_fs4, new_fs4)
		
		# Test LimitAverageStress
		initial_limit_average_stress = capacity_table_options.getLimitAverageStress()
		capacity_table_options.setLimitAverageStress(not initial_limit_average_stress)
		retrieved_limit_average_stress = capacity_table_options.getLimitAverageStress()
		self.assertEqual(retrieved_limit_average_stress, not initial_limit_average_stress)
		
		# Save and reload to verify persistence
		self.model.save()
		self.model.close()
		self.model = self.modeler.openFile(self.copy_file)
		self.projectSettings = self.model.ProjectSettings
		
		# Verify all properties persisted correctly
		capacity_table_options = self.projectSettings.CapacityCalculations.CapacityTableGeneratorOptions
		self.assertEqual(capacity_table_options.getIsTotalCapacity(), not initial_total_capacity)
		self.assertEqual(capacity_table_options.getIsSkinFriction(), not initial_skin_friction)
		self.assertEqual(capacity_table_options.getIsSkinFrictionEndBearing(), not initial_skin_friction_end_bearing)
		self.assertEqual(capacity_table_options.getFS1(), new_fs1)
		self.assertEqual(capacity_table_options.getFS2(), new_fs2)
		self.assertEqual(capacity_table_options.getFS3(), new_fs3)
		self.assertEqual(capacity_table_options.getFS4(), new_fs4)
		self.assertEqual(capacity_table_options.getLimitAverageStress(), not initial_limit_average_stress)


class TestPileAnalysisTypeSettings(BaseProjectSettingsTest):
	"""Test group for pile analysis type settings functionality"""
	
	def setUp(self):
		"""Set up pile analysis type settings tests with program mode set to pile analysis"""
		super().setUp()
		# Set program mode to pile analysis for all pile analysis type settings tests
		self.projectSettings.General.setProgramMode(ProgramModeSelection.PileAnalysis)
  
	def testSetAndGetPileAnalysisType(self):
		"""Test setting and getting pile analysis type"""
		# Get the current analysis type
		initial_type = self.projectSettings.PileAnalysisTypeSettings.getPileAnalysisType()
		self.assertIn(initial_type, [PileAnalysisType.INDIVIDUAL_PILE_ANALYSIS, PileAnalysisType.GROUPED_PILE_ANALYSIS])
		
		# Toggle to the other option
		other_type = PileAnalysisType.GROUPED_PILE_ANALYSIS if initial_type == PileAnalysisType.INDIVIDUAL_PILE_ANALYSIS else PileAnalysisType.INDIVIDUAL_PILE_ANALYSIS
		
		# Set to the other option
		self.projectSettings.PileAnalysisTypeSettings.setPileAnalysisType(other_type)
		retrieved_type = self.projectSettings.PileAnalysisTypeSettings.getPileAnalysisType()
		self.assertEqual(retrieved_type, other_type)
		
		# Set back to the original
		self.projectSettings.PileAnalysisTypeSettings.setPileAnalysisType(initial_type)
		retrieved_type_2 = self.projectSettings.PileAnalysisTypeSettings.getPileAnalysisType()
		self.assertEqual(retrieved_type_2, initial_type)
	
	def testSetAndGetIndividualPileAnalysisType(self):
		"""Test setting and getting all individual pile analysis type options"""
		available_types = [
			IndividualPileAnalysisType.AXIALLY_LOADED,
			IndividualPileAnalysisType.LATERALLY_LOADED,
			IndividualPileAnalysisType.AXIALLY_LATERALLY_LOADED
		]
		self.projectSettings.PileAnalysisTypeSettings.setPileAnalysisType(PileAnalysisType.INDIVIDUAL_PILE_ANALYSIS)
		# For each type, set and get, and verify
		for t in available_types:
			self.projectSettings.PileAnalysisTypeSettings.setIndividualPileAnalysisType(t)
			retrieved_type = self.projectSettings.PileAnalysisTypeSettings.getIndividualPileAnalysisType()
			self.assertEqual(retrieved_type, t)

		# verify the case where the program was already set to the first type
		final_type = available_types[0]
		self.projectSettings.PileAnalysisTypeSettings.setIndividualPileAnalysisType(final_type)
		retrieved_type_final = self.projectSettings.PileAnalysisTypeSettings.getIndividualPileAnalysisType()
		self.assertEqual(retrieved_type_final, final_type)
	
	def testSetAndGetIsMultipleLoadCasesAndPDeltaEffects(self):
		"""Test setting and getting multiple load cases and P-Delta effects settings (only available for AXIALLY_LATERALLY_LOADED)"""
		# Set individual pile analysis type to AXIALLY_LATERALLY_LOADED to enable these options
		self.projectSettings.PileAnalysisTypeSettings.setPileAnalysisType(PileAnalysisType.INDIVIDUAL_PILE_ANALYSIS)
		self.projectSettings.PileAnalysisTypeSettings.setIndividualPileAnalysisType(IndividualPileAnalysisType.AXIALLY_LATERALLY_LOADED)
		
		# Test IsMultipleLoadCases
		initial_multiple_load_cases = self.projectSettings.PileAnalysisTypeSettings.getIsMultipleLoadCases()
		self.projectSettings.PileAnalysisTypeSettings.setIsMultipleLoadCases(not initial_multiple_load_cases)
		retrieved_multiple_load_cases = self.projectSettings.PileAnalysisTypeSettings.getIsMultipleLoadCases()
		self.assertEqual(retrieved_multiple_load_cases, not initial_multiple_load_cases)
		self.projectSettings.PileAnalysisTypeSettings.setIsMultipleLoadCases(initial_multiple_load_cases)
		retrieved_multiple_load_cases_2 = self.projectSettings.PileAnalysisTypeSettings.getIsMultipleLoadCases()
		self.assertEqual(retrieved_multiple_load_cases_2, initial_multiple_load_cases)

		# Test IsIncludePDeltaEffects
		initial_p_delta_effects = self.projectSettings.PileAnalysisTypeSettings.getIsIncludePDeltaEffects()
		self.projectSettings.PileAnalysisTypeSettings.setIsIncludePDeltaEffects(not initial_p_delta_effects)
		retrieved_p_delta_effects = self.projectSettings.PileAnalysisTypeSettings.getIsIncludePDeltaEffects()
		self.assertEqual(retrieved_p_delta_effects, not initial_p_delta_effects)
		self.projectSettings.PileAnalysisTypeSettings.setIsIncludePDeltaEffects(initial_p_delta_effects)
		retrieved_p_delta_effects_2 = self.projectSettings.PileAnalysisTypeSettings.getIsIncludePDeltaEffects()
		self.assertEqual(retrieved_p_delta_effects_2, initial_p_delta_effects)
	
	def testPileAnalysisTypeSettingsComprehensiveWithPersistence(self):
		"""Comprehensive test for all pile analysis type settings with save/restore persistence verification"""
		pile_analysis_settings = self.projectSettings.PileAnalysisTypeSettings
		
		# Test each individual pile analysis type with save/restore
		available_individual_types = [IndividualPileAnalysisType.AXIALLY_LOADED, 
									IndividualPileAnalysisType.LATERALLY_LOADED, 
									IndividualPileAnalysisType.AXIALLY_LATERALLY_LOADED]
		
		pile_analysis_settings.setPileAnalysisType(PileAnalysisType.INDIVIDUAL_PILE_ANALYSIS)
		for individual_type in available_individual_types:
			# Set the individual pile analysis type
			pile_analysis_settings.setIndividualPileAnalysisType(individual_type)
			self.assertEqual(pile_analysis_settings.getIndividualPileAnalysisType(), individual_type)
			
			# For AXIALLY_LATERALLY_LOADED, test the conditional properties
			if individual_type == IndividualPileAnalysisType.AXIALLY_LATERALLY_LOADED:
				# Test multiple load cases
				initial_multiple_load_cases = pile_analysis_settings.getIsMultipleLoadCases()
				pile_analysis_settings.setIsMultipleLoadCases(not initial_multiple_load_cases)
				self.assertEqual(pile_analysis_settings.getIsMultipleLoadCases(), not initial_multiple_load_cases)
				
				# Test P-Delta effects
				initial_p_delta_effects = pile_analysis_settings.getIsIncludePDeltaEffects()
				pile_analysis_settings.setIsIncludePDeltaEffects(not initial_p_delta_effects)
				self.assertEqual(pile_analysis_settings.getIsIncludePDeltaEffects(), not initial_p_delta_effects)
			
			# Save and reload to verify persistence for this individual type
			self.model.save()
			self.model.close()
			
			self.model = self.modeler.openFile(self.copy_file)
			self.projectSettings = self.model.ProjectSettings
			
			# Verify the individual type persisted correctly
			pile_analysis_settings = self.projectSettings.PileAnalysisTypeSettings
			self.assertEqual(pile_analysis_settings.getIndividualPileAnalysisType(), individual_type)
			
			# For AXIALLY_LATERALLY_LOADED, verify conditional properties persisted
			if individual_type == IndividualPileAnalysisType.AXIALLY_LATERALLY_LOADED:
				self.assertEqual(pile_analysis_settings.getIsMultipleLoadCases(), not initial_multiple_load_cases)
				self.assertEqual(pile_analysis_settings.getIsIncludePDeltaEffects(), not initial_p_delta_effects)
			
		# Test setting pile analysis type to GROUPED_PILE_ANALYSIS and verify persistence
		pile_analysis_settings.setPileAnalysisType(PileAnalysisType.GROUPED_PILE_ANALYSIS)
		self.assertEqual(pile_analysis_settings.getPileAnalysisType(), PileAnalysisType.GROUPED_PILE_ANALYSIS)

		# Save and reload to verify persistence for grouped pile analysis type
		self.model.save()
		self.model.close()

		self.model = self.modeler.openFile(self.copy_file)
		self.projectSettings = self.model.ProjectSettings
		pile_analysis_settings = self.projectSettings.PileAnalysisTypeSettings

		self.assertEqual(pile_analysis_settings.getPileAnalysisType(), PileAnalysisType.GROUPED_PILE_ANALYSIS)


class TestGroundwater(BaseProjectSettingsTest):
	"""Test group for groundwater functionality"""
	
	def testGroundWaterAnalysis(self):
		"""Test groundwater analysis setting"""
		groundwater = self.projectSettings.Groundwater
		
		# Get the initial value
		initial_value = groundwater.getIsGroundwaterAnalysis()
		
		# Change it
		new_value = not initial_value
		groundwater.setIsGroundwaterAnalysis(new_value)
		
		# Check that it was changed
		retrieved_value = groundwater.getIsGroundwaterAnalysis()
		self.assertEqual(retrieved_value, new_value)
		
		# Change back
		groundwater.setIsGroundwaterAnalysis(initial_value)
		
		# Check that it was changed back
		final_value = groundwater.getIsGroundwaterAnalysis()
		self.assertEqual(final_value, initial_value)
	
	def testGroundwaterMethod(self):
		"""Test groundwater method setting"""
		groundwater = self.projectSettings.Groundwater
		
		# Set groundwater analysis to true
		groundwater.setIsGroundwaterAnalysis(True)
		
		# Get the initial value
		initial_value = groundwater.getGroundwaterMethod()
		
		# Change it
		other_method = GroundwaterMethod.GRID if initial_value == GroundwaterMethod.PIEZOMETRIC_LINE else GroundwaterMethod.PIEZOMETRIC_LINE
		groundwater.setGroundwaterMethod(other_method)
		
		# Check that it was changed
		retrieved_value = groundwater.getGroundwaterMethod()
		self.assertEqual(retrieved_value, other_method)
		
		# Change back
		groundwater.setGroundwaterMethod(initial_value)
		
		# Check that it was changed back
		final_value = groundwater.getGroundwaterMethod()
		self.assertEqual(final_value, initial_value)
	
	def testWaterUnitWeight(self):
		"""Test water unit weight setting"""
		groundwater = self.projectSettings.Groundwater
		
		# Set groundwater analysis to true
		groundwater.setIsGroundwaterAnalysis(True)
		
		# Set it to a new value
		new_weight = 10.5
		groundwater.setWaterUnitWeight(new_weight)
		
		# Check if it was changed
		retrieved_weight = groundwater.getWaterUnitWeight()
		self.assertEqual(retrieved_weight, new_weight)
	
	def testGroundwaterPersistence(self):
		"""Test that all groundwater settings persist after save and reload"""
		groundwater = self.projectSettings.Groundwater
		
		# Set groundwater analysis to true
		groundwater.setIsGroundwaterAnalysis(True)
		
		# Change all values
		groundwater.setGroundwaterMethod(GroundwaterMethod.GRID)
		groundwater.setWaterUnitWeight(15.7)
		
		# Verify the values were set
		self.assertEqual(groundwater.getIsGroundwaterAnalysis(), True)
		self.assertEqual(groundwater.getGroundwaterMethod(), GroundwaterMethod.GRID)
		self.assertEqual(groundwater.getWaterUnitWeight(), 15.7)
		
		# Save the file
		self.model.save()
		self.model.close()
		
		# Open the file again
		self.model = self.modeler.openFile(self.copy_file)
		self.projectSettings = self.model.ProjectSettings
		groundwater = self.projectSettings.Groundwater
		
		# Check that all values persisted
		self.assertEqual(groundwater.getIsGroundwaterAnalysis(), True)
		self.assertEqual(groundwater.getGroundwaterMethod(), GroundwaterMethod.GRID)
		self.assertEqual(groundwater.getWaterUnitWeight(), 15.7)



class TestInteractionDiagram(BaseProjectSettingsTest):
	"""Test group for interaction diagram functionality"""
	
	def testConcreteStressStrainCurveModelNonFactored(self):
		"""Test setting and getting concrete stress strain curve model for non-factored analysis"""
		interaction_diagram = self.projectSettings.InteractionDiagram
		
		# Set calculate factored interaction MP to false first
		interaction_diagram.setIsCalculateFactoredInteractionMP(False)
		
		# Get the initial value
		initial_model = interaction_diagram.getConcreteStressStrainCurveModel()
		self.assertIsInstance(initial_model, ConcreteStressStrainCurveModel)
		
		# Test setting to MODIFIED_HOGNESTAD (the only available option)
		interaction_diagram.setConcreteStressStrainCurveModel(ConcreteStressStrainCurveModel.MODIFIED_HOGNESTAD)
		
		# Verify it was set correctly
		retrieved_model = interaction_diagram.getConcreteStressStrainCurveModel()
		self.assertEqual(retrieved_model, ConcreteStressStrainCurveModel.MODIFIED_HOGNESTAD)
		
		# Test persistence
		self.model.save()
		self.model.close()
		
		self.model = self.modeler.openFile(self.copy_file)
		self.projectSettings = self.model.ProjectSettings
		interaction_diagram = self.projectSettings.InteractionDiagram
		
		persisted_model = interaction_diagram.getConcreteStressStrainCurveModel()
		self.assertEqual(persisted_model, ConcreteStressStrainCurveModel.MODIFIED_HOGNESTAD)
		
	
	def testCalculateFactoredInteractionMP(self):
		"""Test setting and getting the calculate factored interaction MP boolean"""
		interaction_diagram = self.projectSettings.InteractionDiagram
		
		# Get the initial value
		initial_value = interaction_diagram.getIsCalculateFactoredInteractionMP()
		
		# Set to the opposite value
		new_value = not initial_value
		interaction_diagram.setIsCalculateFactoredInteractionMP(new_value)
		
		# Verify it was set correctly
		retrieved_value = interaction_diagram.getIsCalculateFactoredInteractionMP()
		self.assertEqual(retrieved_value, new_value)
		
		# Test persistence
		self.model.save()
		self.model.close()
		
		self.model = self.modeler.openFile(self.copy_file)
		self.projectSettings = self.model.ProjectSettings
		interaction_diagram = self.projectSettings.InteractionDiagram
		
		persisted_value = interaction_diagram.getIsCalculateFactoredInteractionMP()
		self.assertEqual(persisted_value, new_value)
	
	def testConcreteStressStrainCurveModelFactoredSingleACI(self):
		"""Test setting and getting concrete stress strain curve model for factored single ACI analysis"""
		interaction_diagram = self.projectSettings.InteractionDiagram
		
		# Enable factored interaction MP
		interaction_diagram.setIsCalculateFactoredInteractionMP(True)
		
		# Get the initial value
		initial_model = interaction_diagram.getConcreteStressStrainCurveModel()
		self.assertIsInstance(initial_model, ConcreteStressStrainCurveModel)
		
		# Test all available options
		available_models = [ConcreteStressStrainCurveModel.MODIFIED_HOGNESTAD,
						   ConcreteStressStrainCurveModel.WHITNEY_BLOCK]
		
		for model in available_models:
			interaction_diagram.setConcreteStressStrainCurveModel(model)
			retrieved_model = interaction_diagram.getConcreteStressStrainCurveModel()
			self.assertEqual(retrieved_model, model)
		
		# Test design standards
		# Test SINGLE_FACTOR_FOR_M_AND_P
		interaction_diagram.setDesignStandard(DesignStandard.SINGLE_FACTOR_FOR_M_AND_P)
		retrieved_design_standard = interaction_diagram.getDesignStandard()
		self.assertEqual(retrieved_design_standard, DesignStandard.SINGLE_FACTOR_FOR_M_AND_P)
		
		# Test setting single factor value
		test_factor = 1.5
		interaction_diagram.setSingleFactorForMAndP(test_factor)
		retrieved_factor = interaction_diagram.getSingleFactorForMAndP()
		self.assertEqual(retrieved_factor, test_factor)
		
		# Test ACI_318_FACTORS_2022
		interaction_diagram.setDesignStandard(DesignStandard.ACI_318_FACTORS_2022)
		retrieved_design_standard = interaction_diagram.getDesignStandard()
		self.assertEqual(retrieved_design_standard, DesignStandard.ACI_318_FACTORS_2022)
		
		# Test persistence
		self.model.save()
		self.model.close()
		
		self.model = self.modeler.openFile(self.copy_file)
		self.projectSettings = self.model.ProjectSettings
		interaction_diagram = self.projectSettings.InteractionDiagram
		
		persisted_model = interaction_diagram.getConcreteStressStrainCurveModel()
		self.assertEqual(persisted_model, ConcreteStressStrainCurveModel.WHITNEY_BLOCK)
		
		persisted_design_standard = interaction_diagram.getDesignStandard()
		self.assertEqual(persisted_design_standard, DesignStandard.ACI_318_FACTORS_2022)
		
		interaction_diagram.setDesignStandard(DesignStandard.SINGLE_FACTOR_FOR_M_AND_P)
		persisted_factor = interaction_diagram.getSingleFactorForMAndP()
		self.assertEqual(persisted_factor, test_factor)
			
	def testConcreteStressStrainCurveModelFactoredEurocode(self):
		"""Test all eurocode class functions"""
		interaction_diagram = self.projectSettings.InteractionDiagram
		
		# Enable factored interaction MP
		interaction_diagram.setIsCalculateFactoredInteractionMP(True)
		
		# Set design standard to Eurocode
		interaction_diagram.setDesignStandard(DesignStandard.EUROCODE_FACTORS_EC2_2004)
		retrieved_design_standard = interaction_diagram.getDesignStandard()
		self.assertEqual(retrieved_design_standard, DesignStandard.EUROCODE_FACTORS_EC2_2004)
		
		# Test all available options
		available_models = [ConcreteStressStrainCurveModel.EC2_BILINEAR,
						   ConcreteStressStrainCurveModel.EC2_PARABOLA,
						   ConcreteStressStrainCurveModel.EC2_RECTANGULAR_BLOCK]
		
		for model in available_models:
			interaction_diagram.setConcreteStressStrainCurveModel(model)
			retrieved_model = interaction_diagram.getConcreteStressStrainCurveModel()
			self.assertEqual(retrieved_model, model)
		
		# Test EurocodeParameters class
		eurocode_params = interaction_diagram.EurocodeParameters
		
		# Test gamma_c
		test_gamma_c = 1.501
		eurocode_params.setGammaC(test_gamma_c)
		retrieved_gamma_c = eurocode_params.getGammaC()
		self.assertEqual(retrieved_gamma_c, test_gamma_c)
		
		# Test gamma_s
		test_gamma_s = 1.652
		eurocode_params.setGammaS(test_gamma_s)
		retrieved_gamma_s = eurocode_params.getGammaS()
		self.assertEqual(retrieved_gamma_s, test_gamma_s)
		
		# Test gamma_a
		test_gamma_a = 1.803
		eurocode_params.setGammaA(test_gamma_a)
		retrieved_gamma_a = eurocode_params.getGammaA()
		self.assertEqual(retrieved_gamma_a, test_gamma_a)
		
		# Test alpha_cc
		test_alpha_cc = 1.954
		eurocode_params.setAlphaCC(test_alpha_cc)
		retrieved_alpha_cc = eurocode_params.getAlphaCC()
		self.assertEqual(retrieved_alpha_cc, test_alpha_cc)
		
		# Test alpha_kt
		test_alpha_kt = 2.105
		eurocode_params.setAlphaKt(test_alpha_kt)
		retrieved_alpha_kt = eurocode_params.getAlphaKt()
		self.assertEqual(retrieved_alpha_kt, test_alpha_kt)
		
		# Test alpha_kf
		test_alpha_kf = 2.256
		eurocode_params.setAlphaKf(test_alpha_kf)
		retrieved_alpha_kf = eurocode_params.getAlphaKf()
		self.assertEqual(retrieved_alpha_kf, test_alpha_kf)
		
		# Test use_reduced_section
		initial_use_reduced = eurocode_params.getUseReducedSection()
		eurocode_params.setUseReducedSection(not initial_use_reduced)
		retrieved_use_reduced = eurocode_params.getUseReducedSection()
		self.assertEqual(retrieved_use_reduced, not initial_use_reduced)
		
		# Test persistence
		self.model.save()
		self.model.close()
		
		self.model = self.modeler.openFile(self.copy_file)
		self.projectSettings = self.model.ProjectSettings
		interaction_diagram = self.projectSettings.InteractionDiagram
		eurocode_params = interaction_diagram.EurocodeParameters
		
		persisted_gamma_c = eurocode_params.getGammaC()
		self.assertEqual(persisted_gamma_c, test_gamma_c)
		
		persisted_gamma_s = eurocode_params.getGammaS()
		self.assertEqual(persisted_gamma_s, test_gamma_s)
		
		persisted_gamma_a = eurocode_params.getGammaA()
		self.assertEqual(persisted_gamma_a, test_gamma_a)
		
		persisted_alpha_cc = eurocode_params.getAlphaCC()
		self.assertEqual(persisted_alpha_cc, test_alpha_cc)
		
		persisted_alpha_kt = eurocode_params.getAlphaKt()
		self.assertEqual(persisted_alpha_kt, test_alpha_kt)
		
		persisted_alpha_kf = eurocode_params.getAlphaKf()
		self.assertEqual(persisted_alpha_kf, test_alpha_kf)
		
		persisted_use_reduced = eurocode_params.getUseReducedSection()
		self.assertEqual(persisted_use_reduced, not initial_use_reduced)
			
	def testCalculateCapacityRatioAnd3DInteractionSurfaces(self):
		"""Test setting the boolean and the associated values"""
		interaction_diagram = self.projectSettings.InteractionDiagram
		
		# Enable factored interaction MP first
		interaction_diagram.setIsCalculateFactoredInteractionMP(True)
		
		# Get the initial value
		initial_value = interaction_diagram.getIsCalculateCapacityRatioAnd3DInteractionSurfaces()
		
		# Set to the opposite value
		new_value = not initial_value
		interaction_diagram.setIsCalculateCapacityRatioAnd3DInteractionSurfaces(new_value)
		
		# Verify it was set correctly
		retrieved_value = interaction_diagram.getIsCalculateCapacityRatioAnd3DInteractionSurfaces()
		self.assertEqual(retrieved_value, new_value)
		
  
		interaction_diagram.setIsCalculateCapacityRatioAnd3DInteractionSurfaces(True)
		# Test associated values when enabled

		# Test number of load divisions
		test_load_divisions = 20
		interaction_diagram.setNumberOfLoadDivisions(test_load_divisions)
		retrieved_load_divisions = interaction_diagram.getNumberOfLoadDivisions()
		self.assertEqual(retrieved_load_divisions, test_load_divisions)
		
		# Test number of angle divisions
		test_angle_divisions = 40
		interaction_diagram.setNumberOfAngleDivisions(test_angle_divisions)
		retrieved_angle_divisions = interaction_diagram.getNumberOfAngleDivisions()
		self.assertEqual(retrieved_angle_divisions, test_angle_divisions)
	
		# Test persistence
		self.model.save()
		self.model.close()
		
		self.model = self.modeler.openFile(self.copy_file)
		self.projectSettings = self.model.ProjectSettings
		interaction_diagram = self.projectSettings.InteractionDiagram
		
		persisted_value = interaction_diagram.getIsCalculateCapacityRatioAnd3DInteractionSurfaces()
		self.assertEqual(persisted_value, True)
		
		persisted_load_divisions = interaction_diagram.getNumberOfLoadDivisions()
		self.assertEqual(persisted_load_divisions, test_load_divisions)
			
		persisted_angle_divisions = interaction_diagram.getNumberOfAngleDivisions()
		self.assertEqual(persisted_angle_divisions, test_angle_divisions)
  
class TestAdvanced(BaseProjectSettingsTest):
    
    def testAll(self):
        """Test all Advanced settings with increasing values starting from 9"""
        advanced = self.projectSettings.Advanced
        
        # Test Pile Discretization - try both values
        initial_discretization = advanced.getPileDiscretization()
        
        # Set to the opposite value first
        if initial_discretization == PileDiscretizationOptions.AUTO:
            advanced.setPileDiscretization(PileDiscretizationOptions.CUSTOM)
            self.assertEqual(advanced.getPileDiscretization(), PileDiscretizationOptions.CUSTOM)
            
            # Now set to AUTO
            advanced.setPileDiscretization(PileDiscretizationOptions.AUTO)
            self.assertEqual(advanced.getPileDiscretization(), PileDiscretizationOptions.AUTO)
        else:
            advanced.setPileDiscretization(PileDiscretizationOptions.AUTO)
            self.assertEqual(advanced.getPileDiscretization(), PileDiscretizationOptions.AUTO)
            
            # Now set to CUSTOM
            advanced.setPileDiscretization(PileDiscretizationOptions.CUSTOM)
            self.assertEqual(advanced.getPileDiscretization(), PileDiscretizationOptions.CUSTOM)
        

        # Test Pile Depth Increment (float with 3 decimal places)
        test_pile_depth_increment = 9.123
        advanced.setPileDepthIncrement(test_pile_depth_increment)
        retrieved_pile_depth_increment = advanced.getPileDepthIncrement()
        self.assertEqual(retrieved_pile_depth_increment, test_pile_depth_increment)
        
        # Test Pile Segments (integer)
        test_pile_segments = 10
        advanced.setPileSegments(test_pile_segments)
        retrieved_pile_segments = advanced.getPileSegments()
        self.assertEqual(retrieved_pile_segments, test_pile_segments)

        # Test Convergence Tolerance (float with 3 decimal places)
        test_convergence_tolerance = 11.789
        advanced.setConvergenceTolerance(test_convergence_tolerance)
        retrieved_convergence_tolerance = advanced.getConvergenceTolerance()
        self.assertEqual(retrieved_convergence_tolerance, test_convergence_tolerance)
        
        # Test Number of Iterations (integer)
        test_number_of_iterations = 12
        advanced.setNumberOfIterations(test_number_of_iterations)
        retrieved_number_of_iterations = advanced.getNumberOfIterations()
        self.assertEqual(retrieved_number_of_iterations, test_number_of_iterations)
        
        # Test Reinforced Concrete Slices (integer)
        test_reinforced_concrete_slices = 13
        advanced.setReinforcedConcreteSlices(test_reinforced_concrete_slices)
        retrieved_reinforced_concrete_slices = advanced.getReinforcedConcreteSlices()
        self.assertEqual(retrieved_reinforced_concrete_slices, test_reinforced_concrete_slices)
        
        # Test Use Method of Gergiadis Layering Effect (boolean)
        initial_georgiadis = advanced.getUseMethodOfGergiadisLayeringEffect()
        
        # Set to the opposite value
        advanced.setUseMethodOfGergiadisLayeringEffect(not initial_georgiadis)
        retrieved_georgiadis = advanced.getUseMethodOfGergiadisLayeringEffect()
        self.assertEqual(retrieved_georgiadis, not initial_georgiadis)
        
        # Test persistence by saving and reopening the file
        self.model.save()
        self.model.close()
        
        # Reopen the file
        self.model = self.modeler.openFile(self.copy_file)
        self.projectSettings = self.model.ProjectSettings
        advanced = self.projectSettings.Advanced
        
        # Verify all values persisted correctly
        persisted_pile_depth_increment = advanced.getPileDepthIncrement()
        self.assertEqual(persisted_pile_depth_increment, test_pile_depth_increment)
        
        persisted_pile_segments = advanced.getPileSegments()
        self.assertEqual(persisted_pile_segments, test_pile_segments)
        
        persisted_convergence_tolerance = advanced.getConvergenceTolerance()
        self.assertEqual(persisted_convergence_tolerance, test_convergence_tolerance)
        
        persisted_number_of_iterations = advanced.getNumberOfIterations()
        self.assertEqual(persisted_number_of_iterations, test_number_of_iterations)
        
        persisted_reinforced_concrete_slices = advanced.getReinforcedConcreteSlices()
        self.assertEqual(persisted_reinforced_concrete_slices, test_reinforced_concrete_slices)
        
        persisted_georgiadis = advanced.getUseMethodOfGergiadisLayeringEffect()
        self.assertEqual(persisted_georgiadis, not initial_georgiadis)
        