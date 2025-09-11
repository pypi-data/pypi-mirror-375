import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'generated_python_files')))
import grpc
import RSPileScripting.generated_python_files.ClientService_pb2 as ClientService_pb2
import RSPileScripting.generated_python_files.ClientService_pb2_grpc as ClientService_pb2_grpc
import logging

class Client():
	logger = logging.getLogger('Rocscience.RSPile._client')

	def __init__(self, port : int):
		self.compatibleProgramVersion = "3.032"
		self.establishConnection(port)
		self._stub = ClientService_pb2_grpc.ClientServiceStub(self.channel)
		checkVersionRequest = ClientService_pb2.CheckVersionRequest(library_version=self.compatibleProgramVersion)
		isVersionCompatibleResponse = self.callFunction(self._stub.CheckVersion, checkVersionRequest)
		if not isVersionCompatibleResponse.do_versions_match:
			self.closeConnection()
			raise RuntimeError(f"""
					  Library version is not compatible with the program version. 
					  Please ensure that the library version and program version are equal. 
					  Library version: {self.compatibleProgramVersion} Program version: {isVersionCompatibleResponse.modeler_version}.
					  """
					  )
		self.generateSessionID()

	def establishConnection(self, port):
		self.channel = grpc.insecure_channel(f"localhost:{port}")

	def generateSessionID(self, retry_attempts=3):
		request = ClientService_pb2.GenerateNewSessionRequest()
		try:
			response = self.callFunction(self._stub.GenerateNewSession, request)
			self.sessionID = response.session_id
			return
		except grpc._channel._InactiveRpcError as e:
			if e.code() == grpc.StatusCode.UNAVAILABLE:
				self.logger.warning("Failed to connect to RSPile. Retrying...")
				if retry_attempts > 0:
					time.sleep(1)
					self.generateSessionID(retry_attempts - 1)
				else:
					self.logger.error("Unable to connect to RSPile Application.")
					raise
			else:
				self.logger.error(f"An unexpected error occurred: {e.details()}")
				raise

	def endSession(self):
		if hasattr(self, 'sessionID') and self.sessionID is not None:
			request = ClientService_pb2.EndSessionRequest(session_id=self.sessionID)
			self.callFunction(self._stub.EndSession, request)

	def closeConnection(self):
		self.channel.close()

	def callFunction(self, function, request):
		try:
			response, call = function.with_call(request)
			self._logMessages(call)
			return response
		except grpc.RpcError as e:
			self.logger.warning("An exception was raised from the application.")
			raise

	def _logMessages(self, call: grpc.Call):
		if not call:
			return
		for key, value in call.trailing_metadata():
			if key == "warning":
				self.logger.warning(value)
