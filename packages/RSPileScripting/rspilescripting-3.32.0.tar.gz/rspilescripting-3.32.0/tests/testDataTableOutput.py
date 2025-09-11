import unittest
from RSPileScripting.RSPileModeler import RSPileModeler
from RSPileScripting.RSPileModel import *
from dotenv import load_dotenv
import shutil
import grpc
import os
import resources.DataOutputComparatorUtility as data_compare_util
import pandas as pd

class TestDataTableOutput(unittest.TestCase):
	load_dotenv()
	port = 60044
	exe_path = os.getenv("PATH_TO_RSPILE_CPP_REPO") + "\\Build\\Debug_x64\\RSPile.exe"
	pile_analysis_lat_ax_test_file = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\PileAnalysisAxLatModel.rspile2"
	pile_analysis_ax_test_file = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\PileAnalysisAxModel.rspile2"
	pile_analysis_lat_test_file = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\PileAnalysisLatModel.rspile2"
	driven_test_file = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\DrivenModel.rspile2"
	bored_test_file = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\BoredModel.rspile2"
	helical_test_file = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\HelicalModel.rspile2"

	#EXCEL OUTPUT FILES
	pile_analysis_lat_ax_excel_output = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\PILE_ANALYSIS_AX_LAT_OUTPUT.xlsx"
	pile_analysis_ax_excel_output = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\PILE_ANALYSIS_AX_OUTPUT.xlsx"
	pile_analysis_lat_excel_output = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\PILE_ANALYSIS_LAT_OUTPUT.xlsx"
	bored_excel_output = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\BORED_OUTPUT.xlsx"
	driven_excel_output = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\DRIVEN_OUTPUT.xlsx"
	helical_excel_output = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\HELICAL_OUTPUT.xlsx"
	helical_res_file_1 = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\helical_pile_capacity_results.csv"
	helical_res_file_2 = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\helical_pile_segment_record.csv"

	@classmethod
	def setUpClass(cls):
		RSPileModeler.startApplication(overridePathToExecutable=cls.exe_path, port=cls.port)
		cls.modeler = RSPileModeler(cls.port)

	@classmethod
	def tearDownClass(cls):
		cls.modeler.closeApplication()

	def customSetUp(self):
		if not hasattr(self, "test_file"):
			raise AttributeError("Test file not specified for this test case. Set `self.test_file` in your test method.")
		
		self.copy_file = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\copyTestProject.rspile2"
		shutil.copy(self.test_file, self.copy_file)

		self.model = self.modeler.openFile(self.copy_file)
		self.model.save()
		self.model.compute()

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

		if os.path.exists(self.helical_res_file_1):
			os.remove(self.helical_res_file_1)
		
		if os.path.exists(self.helical_res_file_2):
			os.remove(self.helical_res_file_2)

	def testPileAnalysisLatAx(self):
		self.test_file = self.pile_analysis_lat_ax_test_file
		self.customSetUp()
		output_tables = self.model.getPileResultsTables()
		
		#compares all headers and all data between the two datasets
		scripting_df_dict = self.model.getPileResultsTables()
		excel_df_dict = data_compare_util.convertPileAnalysisExcelResultsHelper(self.pile_analysis_lat_ax_excel_output)
		self.assertTrue(data_compare_util.compare_pile_data(excel_df_dict, scripting_df_dict))
		
		#Check that calling a specific output option works
		output_tables = self.model.getPileResultsTables(GraphingOptions.AX_LAT_END_BEARING)
		self.assertEqual(output_tables["Pile 1"].columns[0], "End Bearing")
		
		#test specifying only unavailable output options
		with self.assertRaises(grpc.RpcError):
			self.model.getPileResultsTables(GraphingOptions.BORED_END_BEARING_CAPACITY)

		#test specifying mix of available and unavailable output options
		output_tables = self.model.getPileResultsTables(GraphingOptions.DEPTH_FROM_PILE_HEAD, GraphingOptions.BORED_END_BEARING_CAPACITY, GraphingOptions.AX_LAT_SKIN_FRICTION)
		pile_1_data : ResultsTable = output_tables["Pile 1"]
		self.assertEqual(len(pile_1_data.columns), 2)

	def testPileAnalysisAx(self):
		self.test_file = self.pile_analysis_ax_test_file
		self.customSetUp()

		#compares all headers and all data between the two datasets
		scripting_df_dict = self.model.getPileResultsTables()
		excel_df_dict = data_compare_util.convertPileAnalysisExcelResultsHelper(self.pile_analysis_ax_excel_output)
		self.assertTrue(data_compare_util.compare_pile_data(excel_df_dict, scripting_df_dict))

		#Check that calling a specific output option works
		output_tables = self.model.getPileResultsTables(GraphingOptions.AX_LAT_SKIN_FRICTION)
		self.assertEqual(output_tables["Pile 1"].columns[0], "Skin Friction")
		
		#test specifying only unavailable output options
		with self.assertRaises(grpc.RpcError):
			self.model.getPileResultsTables(GraphingOptions.BORED_SKIN_FRICTION_CAPACITY)

		#test specifying mix of available and unavailable output options
		output_tables = self.model.getPileResultsTables(GraphingOptions.SOIL_STIFFNESS_Z, GraphingOptions.AX_LAT_SKIN_FRICTION, GraphingOptions.BORED_UNIT_ULTIMATE_END_BEARING)
		pile_1_data : ResultsTable = output_tables["Pile 1"]
		self.assertEqual(len(pile_1_data.columns), 2)

		
	def testPileAnalysisLat(self):
		self.test_file = self.pile_analysis_lat_test_file
		self.customSetUp()

		#compares all headers and all data between the two datasets
		scripting_df_dict = self.model.getPileResultsTables()
		excel_df_dict = data_compare_util.convertPileAnalysisExcelResultsHelper(self.pile_analysis_lat_excel_output)
		self.assertTrue(data_compare_util.compare_pile_data(excel_df_dict, scripting_df_dict))

		#Check that calling a specific output option works
		output_tables = self.model.getPileResultsTables(GraphingOptions.BEAM_SHEAR_FORCE_Y)
		self.assertEqual(output_tables["Pile 1"].columns[0], "Beam Shear Force Y'")
		
		#test specifying only unavailable output options
		with self.assertRaises(grpc.RpcError):
			self.model.getPileResultsTables(GraphingOptions.AX_LAT_END_BEARING)

		#test specifying mix of available and unavailable output options
		output_tables = self.model.getPileResultsTables(GraphingOptions.DEPTH_FROM_PILE_HEAD, GraphingOptions.BORED_END_BEARING_CAPACITY, GraphingOptions.AX_LAT_SKIN_FRICTION)
		pile_1_data : ResultsTable = output_tables["Pile 1"]
		self.assertEqual(len(pile_1_data.columns), 1)

	def testDrivenModel(self):
		self.test_file = self.driven_test_file
		self.customSetUp()
		
		#compares all headers and all data between the two datasets
		scripting_df_dict = self.model.getPileResultsTables()
		excel_df_dict = data_compare_util.convertPileCapacityExcelResultsHelper(self.driven_excel_output, "Pile 1")
		self.assertTrue(data_compare_util.compare_pile_data(excel_df_dict, scripting_df_dict))

		#Check that calling a specific output option works
		output_tables = self.model.getPileResultsTables(GraphingOptions.DRIVEN_ULTIMATE_END_BEARING)
		self.assertEqual(output_tables["Pile 1"].columns[0], "Ultimate (End Bearing)")
		
		#test specifying only unavailable output options
		with self.assertRaises(grpc.RpcError):
			self.model.getPileResultsTables(GraphingOptions.HELICAL_UNIT_CYLINDRICAL_SHEAR)

		#test specifying mix of available and unavailable output options
		output_tables = self.model.getPileResultsTables(GraphingOptions.DEPTH_FROM_PILE_HEAD, GraphingOptions.BORED_END_BEARING_CAPACITY, GraphingOptions.AX_LAT_SKIN_FRICTION)
		pile_1_data : ResultsTable = output_tables["Pile 1"]
		self.assertEqual(len(pile_1_data.columns), 1)

	def testBoredModel(self):
		self.test_file = self.bored_test_file
		self.customSetUp()  # Explicitly invoke setup

		#compares all headers and all data between the two datasets
		scripting_df_dict = self.model.getPileResultsTables()
		excel_df_dict = data_compare_util.convertPileCapacityExcelResultsHelper(self.bored_excel_output, "Pile 1")
		self.assertTrue(data_compare_util.compare_pile_data(excel_df_dict, scripting_df_dict))
		
		output_tables = self.model.getPileResultsTables(GraphingOptions.BORED_SKIN_FRICTION_CAPACITY)
		self.assertEqual(output_tables["Pile 1"].columns[0], "Skin Friction Capacity")
		
		#test specifying only unavailable output options
		with self.assertRaises(grpc.RpcError):
			self.model.getPileResultsTables(GraphingOptions.DRIVEN_DRIVING_TOTAL)

		#test specifying mix of available and unavailable output options
		output_tables = self.model.getPileResultsTables(GraphingOptions.DRIVEN_DRIVING_SKIN_FRICTION, GraphingOptions.DRIVEN_DRIVING_END_BEARING, GraphingOptions.AX_LAT_SKIN_FRICTION, GraphingOptions.BORED_SKIN_FRICTION_CAPACITY)
		pile_1_data : ResultsTable = output_tables["Pile 1"]
		self.assertEqual(len(pile_1_data.columns), 1)

	def testHelicalModel(self):
		self.test_file = self.helical_test_file
		self.customSetUp()  # Explicitly invoke setup

		#compares all headers and all data between the two datasets
		scripting_df_dict = self.model.getPileResultsTables()
		excel_df_dict = data_compare_util.convertPileCapacityExcelResultsHelper(self.helical_excel_output, "Pile 1")
		self.assertTrue(data_compare_util.compare_pile_data(excel_df_dict, scripting_df_dict))
		
		output_tables = self.model.getPileResultsTables(GraphingOptions.HELICAL_UNIT_SKIN_FRICTION)
		self.assertEqual(output_tables["Pile 1"].columns[0], "Unit Skin Friction (Shaft)")
		
		#test specifying only unavailable output options
		with self.assertRaises(grpc.RpcError):
			self.model.getPileResultsTables(GraphingOptions.BORED_UNIT_ULTIMATE_SKIN_FRICTION)

		#test specifying mix of available and unavailable output options
		output_tables = self.model.getPileResultsTables(GraphingOptions.DRIVEN_DRIVING_SKIN_FRICTION, GraphingOptions.DRIVEN_DRIVING_END_BEARING, GraphingOptions.AX_LAT_SKIN_FRICTION, GraphingOptions.HELICAL_END_BEARING_COMPRESSION)
		pile_1_data : ResultsTable = output_tables["Pile 1"]
		self.assertEqual(len(pile_1_data.columns), 1)

	def testObtainMultiPileResults(self):
		self.test_file = self.pile_analysis_lat_ax_test_file
		self.customSetUp()
		output_tables : PileResults = self.model.getPileResultsTables()
		pile_1_data : ResultsTable = output_tables["Pile 1"]

		#get result for specific pile data
		self.assertAlmostEqual(pile_1_data.getMinimumValue(GraphingOptions.AX_LAT_DISPLACEMENT_Z), -0.216, 2)
		
		#get results from all piles
		max_pile_name, max_value = output_tables.getMaximumValue(GraphingOptions.AX_LAT_DISPLACEMENT_Z)
		min_pile_name, min_value = output_tables.getMinimumValue(GraphingOptions.AX_LAT_DISPLACEMENT_Z)

		self.assertEqual(max_pile_name, "Pile 3")
		self.assertAlmostEqual(max_value, 0.5, 1)

		self.assertEqual(min_pile_name, "Pile 2")
		self.assertAlmostEqual(min_value, -2.2, 1)

	def testGetColumnName(self):
		self.test_file = self.pile_analysis_lat_ax_test_file
		self.customSetUp()
		output_tables : PileResults = self.model.getPileResultsTables(GraphingOptions.AX_LAT_DISPLACEMENT_Z)
		pile_1_data : ResultsTable = output_tables["Pile 1"]

		self.assertEqual(pile_1_data.getColumnName(GraphingOptions.AX_LAT_DISPLACEMENT_Z), pile_1_data.columns[0])

	def testSelectColumns(self):
		self.test_file = self.pile_analysis_lat_ax_test_file
		self.customSetUp()

		#get results for pile 1 and then filter a subset of those columns using selectColumns
		output_tables : PileResults = self.model.getPileResultsTables()
		pile_1_data : ResultsTable = output_tables["Pile 1"]
		pile_1_data_subselection = pile_1_data.selectColumns(GraphingOptions.AX_LAT_DISPLACEMENT_Z, GraphingOptions.DEPTH_FROM_PILE_HEAD)

		#get results for pile 1 but specify only the filtered columns form above
		baseline_results = self.model.getPileResultsTables(GraphingOptions.AX_LAT_DISPLACEMENT_Z, GraphingOptions.DEPTH_FROM_PILE_HEAD)
		pile1_data_baseline : ResultsTable = baseline_results["Pile 1"]

		#compare the two dataframes
		baseline_df_min = pile1_data_baseline.getMinimumValue(GraphingOptions.DEPTH_FROM_PILE_HEAD)
		df_subselection_min  = pile_1_data_subselection.getMinimumValue(GraphingOptions.DEPTH_FROM_PILE_HEAD)
		self.assertEqual(baseline_df_min, df_subselection_min)

		baseline_df_max = pile1_data_baseline.getMaximumValue(GraphingOptions.DEPTH_FROM_PILE_HEAD)
		df_subselection_max  = pile_1_data_subselection.getMaximumValue(GraphingOptions.DEPTH_FROM_PILE_HEAD)
		self.assertEqual(baseline_df_max, df_subselection_max)

		pd.testing.assert_frame_equal(pile_1_data_subselection, pile1_data_baseline, check_like=True)

if __name__ == '__main__':
	unittest.main(verbosity=2)