import unittest
import psutil
import socket
import grpc
from RSPileScripting.RSPileModeler import RSPileModeler
import random
from dotenv import load_dotenv
import os
import shutil

class TestApplicationFunctions(unittest.TestCase):
	load_dotenv()
	port = 60044
	expected_executable = "RSPile.exe"
	exe_path = os.getenv("PATH_TO_RSPILE_CPP_REPO") + "\\Build\\Debug_x64\\RSPile.exe"
	test_file = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\TestProject.rspile2"
	non_rspile_file_path = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\testTextFile.txt"

	@classmethod
	def setUpClass(cls):
		RSPileModeler.startApplication(overridePathToExecutable=cls.exe_path, port=cls.port)
		cls.modeler = RSPileModeler(cls.port)
		cls.copy_file = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\copyTestProject.rspile2"
		shutil.copy(cls.test_file, cls.copy_file)

	@classmethod
	def tearDownClass(cls):
		if os.path.exists(cls.copy_file):
			os.remove(cls.copy_file)
		copy_file_dir = os.path.dirname(cls.copy_file) + "\\copyTestProject"
		if os.path.exists(copy_file_dir):
			try:
				shutil.rmtree(copy_file_dir)
			except Exception:
				print(f"Failed to remove directory: {copy_file_dir}")
		cls.modeler.closeApplication()

	def testModelerProcessIsRunning(self):
		is_running = False
		for process in psutil.process_iter(['pid', 'name']):
			if process.info['name'].lower() == self.expected_executable.lower():
				self.__class__.process = process
				is_running = True
				break
		self.assertTrue(is_running, f"{self.expected_executable} is not running.")

	def testPortIsOccupied(self):
		is_occupied_port = False
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			try:
				s.bind(("localhost", self.port))
				is_occupied_port = False
			except socket.error:
				is_occupied_port = True
		self.assertTrue(is_occupied_port, f"Port {self.port} is not occupied after starting the application.")

	def testConnectToModeler(self):
		try:
			self.assertIsNotNone(self.modeler._client)
		except Exception as e:
			self.fail(f"Failed to connect to RSPileModeler")

	def testFileOpenSaveClose(self):
		self.model = self.modeler.openFile(self.copy_file)
		random_value = random.randint(0, 100)
		self.model.getSoilProperties()[0].setUnitWeight(random_value)
		self.model.save()
		self.model.close()

		self.model = self.modeler.openFile(self.copy_file)
		self.assertEqual(self.model.getSoilProperties()[0].getUnitWeight(), random_value)
		self.model.close()

	def testOpenNonExistingFile(self):
		with self.assertRaises(FileNotFoundError):
			self.modeler.openFile("X:\\Invalid_File_Path")

	def testOpenNonRSPileFile(self):
		with self.assertRaises(grpc.RpcError):
			self.modeler.openFile(self.non_rspile_file_path)

	def testOpenEmptyFilePath(self):
		with self.assertRaises(FileNotFoundError): 
			self.modeler.openFile("")

	def testSaveAsToInvalidDirectory(self):
		with self.assertRaises(FileNotFoundError):
			self.model = self.modeler.openFile(self.copy_file)
			self.model.save("X:\\Invalid_Directory")
			
if __name__ == '__main__':
	unittest.main(verbosity=2)