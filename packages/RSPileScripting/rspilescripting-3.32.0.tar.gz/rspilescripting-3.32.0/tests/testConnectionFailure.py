import unittest
import grpc
from RSPileScripting.RSPileModeler import RSPileModeler
from dotenv import load_dotenv
import os
import shutil
import RSPileScripting.generated_python_files.ClientService_pb2 as ClientService_pb2

class TestPingFailure(unittest.TestCase):
	load_dotenv()
	port = 60044
	expected_executable = "RSPile.exe"
	exe_path = os.getenv("PATH_TO_RSPILE_CPP_REPO") + "\\Build\\Debug_x64\\RSPile.exe"
	test_file = os.getenv("PATH_TO_RSPILE_PYTHON_REPO") + "\\tests\\resources\\TestProject.rspile2"
	
	@classmethod
	def setUpClass(cls):
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

	def testFailuretoPingModeler(self):
		with self.assertRaises(grpc.RpcError):
			modeler = RSPileModeler(self.port)

	def testPortOutOfRange(self):
		with self.assertRaises(ValueError):
			RSPileModeler.startApplication(
				overridePathToExecutable=self.exe_path, 
				port=100000000000000
				)
			
	def testPortOccupied(self):
		RSPileModeler.startApplication(
				overridePathToExecutable=self.exe_path, 
				port=self.port
				)
		modeler = RSPileModeler(self.port)
		with self.assertRaises(RuntimeError):
			RSPileModeler.startApplication(
				overridePathToExecutable=self.exe_path, 
				port=self.port, timeout=5
				)
		modeler.closeApplication()

	def testIncorrectVersion(self):
		RSPileModeler.startApplication(
			overridePathToExecutable=self.exe_path, 
			port=self.port
		)
		modeler = RSPileModeler(self.port)
		modeler._client.compatibleProgramVersion = "Incompatible Version"

		response = modeler._client.callFunction(modeler._client._stub.CheckVersion, 
									ClientService_pb2.CheckVersionRequest(
										library_version=modeler._client.compatibleProgramVersion
									))
		
		self.assertFalse(response.do_versions_match)
	
		modeler.closeApplication()

if __name__ == '__main__':
	unittest.main(verbosity=2)