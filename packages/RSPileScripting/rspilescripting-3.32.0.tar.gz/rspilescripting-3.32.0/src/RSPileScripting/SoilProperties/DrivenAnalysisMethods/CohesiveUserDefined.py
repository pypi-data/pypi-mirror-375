from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.DrivenCohesiveUserDefinedAdhesionService_pb2 as AdhesionService_pb2
import RSPileScripting.generated_python_files.soil_services.DrivenCohesiveUserDefinedAdhesionService_pb2_grpc as AdhesionService_pb2_grpc

class UserDefinedAdhesion:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = AdhesionService_pb2_grpc.DrivenCohesiveUserDefinedAdhesionServiceStub(self._client.channel)

	def _getUserDefinedAdhesionProperties(self) -> AdhesionService_pb2.UserDefinedAdhesionProperties:
		request = AdhesionService_pb2.GetUserDefinedAdhesionRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetUserDefinedAdhesionProperties, request)
		return response.user_defined_adhesion_props

	def _setUserDefinedAdhesionProperties(self, adhesionProps: AdhesionService_pb2.UserDefinedAdhesionProperties):
		request = AdhesionService_pb2.SetUserDefinedAdhesionRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id,
			user_defined_adhesion_props=adhesionProps)
		self._client.callFunction(self._stub.SetUserDefinedAdhesionProperties, request)

	def getAdhesion(self) -> float:
		properties = self._getUserDefinedAdhesionProperties()
		return properties.user_defined_adhesion

	def setAdhesion(self, adhesion: float):
		properties = self._getUserDefinedAdhesionProperties()
		properties.user_defined_adhesion = adhesion
		self._setUserDefinedAdhesionProperties(properties)