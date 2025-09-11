from logging import Logger
from multiprocessing.connection import Listener
import grpc
import os
import time

class ApplicationManager:
	minimumPort = 49152
	maximumPort = 65535
	defaultTimeout = 30
	def startApplication(self, pathToExecutable: str, port: int, isServerRunning: callable, logger: Logger, timeout: float = defaultTimeout):
		if port < self.minimumPort or port > self.maximumPort:
			msg = f"Port must be in the range {self.minimumPort} to {self.maximumPort}"
			logger.error(msg)
			raise ValueError(msg)

		start_time = time.time()
		
		while time.time() - start_time < timeout:
			if self._isPortAvailable(port):
				logger.info(f"Port {port} is available. Attempting to start the application at {pathToExecutable} and binding server to port {port}...")
				os.spawnl(os.P_DETACH, pathToExecutable, pathToExecutable, "-startpythonserver", str(port))
				self._tryToConnectToServer(port, isServerRunning, timeout - (time.time() - start_time), logger)
				return
			else:
				logger.warning(f"Port {port} is occupied. Retrying in 3 seconds...")
				time.sleep(3)

		msg = f"Port {port} is still occupied after {timeout} seconds."
		logger.error(msg)
		raise RuntimeError(msg)
		
	def _tryToConnectToServer(self, port : int, isServerRunning : callable, timeout, logger : Logger):
		try:
			logger.debug("Trying to connect to the server...")
			isServerRunning(port, timeout)
			logger.debug("connected!")
		except grpc._channel._InactiveRpcError as e:
			msg = "The application did not start within the given timeout time."
			logger.error(msg)
			raise TimeoutError(msg)
		
	def _isPortAvailable(self, port):
		portAvailable = False
		listener = None
		try:
			listener = Listener(('localhost', port), 'AF_INET')
			portAvailable = True
		except Exception:
			portAvailable = False

		if listener:
			listener.close()
		return portAvailable