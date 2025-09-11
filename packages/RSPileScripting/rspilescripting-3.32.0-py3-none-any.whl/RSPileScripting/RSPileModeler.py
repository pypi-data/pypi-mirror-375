from RSPileScripting._client import Client
import os
import logging
from RSPileScripting.RSPileModel import RSPileModel
import RSPileScripting.generated_python_files.ApplicationService_pb2 as ApplicationService_pb2
import RSPileScripting.generated_python_files.ApplicationService_pb2_grpc as ApplicationService_pb2_grpc
from RSPileScripting.Utilities.ApplicationManager import ApplicationManager
import winreg
import grpc
import atexit
import time

class RSPileModeler:
	logger = logging.getLogger('Rocscience.RSPile.RSPileModeler')

	def __init__(self, port=60054):
		self.port = port
		self._client = Client(self.port)
		self._stub = ApplicationService_pb2_grpc.ApplicationServiceStub(self._client.channel)
		self._atexitRegistered = True
		atexit.register(self._closeSession)

	def openFile(self, fileName: str) -> RSPileModel:
		"""
		Examples:
		:ref:`Modeler Example`
		"""
		absPath = os.path.abspath(fileName)
		if os.path.isfile(absPath):
			openFileRequest = ApplicationService_pb2.OpenFileRequest(session_id=self._client.sessionID, file_name=absPath)
			response: ApplicationService_pb2.OpenFileResponse = self._client.callFunction(self._stub.OpenFile, openFileRequest)
			return RSPileModel(self._client, response.model_id, absPath)
		else:
			self.logger.error("Invalid File Path: %s", absPath)
			raise FileNotFoundError(f"The file path '{fileName}' is invalid or the file does not exist.")
	
	def _closeSession(self):
		try:
			self._client.endSession()
			self._client.closeConnection()
		except Exception as e:
			self.logger.error(f"Failed to close session: {e}")

	@classmethod
	def startApplication(cls, port: int, overridePathToExecutable: str = None, timeout: float = 30) -> None:
		"""
		Starts RSPile, with the option to override the default executable path.

		Args:
			port : int
				The port number to bind the server to. Must be a port number between 49152 and 65535.
			
			overridePathToExecutable : str, optional
				An optional path to override the default RSPile executable. If not provided, the latest installation of RSPile will be used.
			
			timeout : float, optional
				The maximum time to wait for the server to start and bind to the specified port, by default 30 seconds.

		Returns:
			None

		Note:
			The logger is configured under the `Rocscience.RSPile` namespace.

		Examples:
		:ref:`Modeler Example`
		"""
		appManager = ApplicationManager()
		executablePath = overridePathToExecutable if overridePathToExecutable else cls._getApplicationPath()
		appManager.startApplication(executablePath, port, cls._isServerRunning, cls.logger, timeout)

	@staticmethod
	def _getApplicationPath() -> str:
		registry = winreg.ConnectRegistry(None, winreg.HKEY_LOCAL_MACHINE)
		key = winreg.OpenKey(registry, r'SOFTWARE\Rocscience\RSPile 3.0')
		installationLocation, type = winreg.QueryValueEx(key, "Install")
		rsPileModelerInstallLocation = rf"{installationLocation}\RSPile"
		return rsPileModelerInstallLocation
	
	@staticmethod
	def _isServerRunning(port, timeout) -> bool:
		channel = grpc.insecure_channel(f"localhost:{port}")
		stub = ApplicationService_pb2_grpc.ApplicationServiceStub(channel)
		pingRequest = ApplicationService_pb2.PingRequest()
		try:
			stub.Ping(pingRequest, wait_for_ready=True, timeout=timeout)
			return True
		except grpc.RpcError as e:
			RSPileModeler.logger.error(f"Failed to ping server on port {port}: {e}")
			return False
		finally:
			channel.close()
	
	def closeApplication(self, timeout=30) -> None:
		"""
		Closes the application.

		Args:
			timeout: float, optional
				The maximum time to wait for the application to close and release the port, by default 30 seconds.

		Returns:
			None

		Raises:
			TimeoutError: The application did not close within the given timeout time.
		
		Examples:
		:ref:`Modeler Example`
		"""
		self._client.callFunction(self._stub.CloseApplication, 
								  ApplicationService_pb2.CloseApplicationRequest())
		appManager = ApplicationManager()
		portIsAvailable = False
		startTime = time.time()
		while not portIsAvailable:
			if (time.time() - startTime) > timeout:
				raise TimeoutError("The application did not close within the given timeout time.")
			portIsAvailable = appManager._isPortAvailable(self.port)
		if self._atexitRegistered:
			atexit.unregister(self._closeSession)
			self._atexitRegistered = False
		self._client.closeConnection()
		self._client.sessionID = None