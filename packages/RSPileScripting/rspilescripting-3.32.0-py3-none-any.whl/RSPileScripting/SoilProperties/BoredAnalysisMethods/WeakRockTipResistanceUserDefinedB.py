from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.BoredWeakRockUserDefinedBService_pb2 as BoredWeakRockUserDefinedBService_pb2
import RSPileScripting.generated_python_files.soil_services.BoredWeakRockUserDefinedBService_pb2_grpc as BoredWeakRockUserDefinedBService_pb2_grpc

class UserDefinedB:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = BoredWeakRockUserDefinedBService_pb2_grpc.BoredWeakRockUserDefinedBServiceStub(self._client.channel)

	def _getUserDefinedBProperties(self) -> BoredWeakRockUserDefinedBService_pb2.UserDefinedBProperties:
		request = BoredWeakRockUserDefinedBService_pb2.GetUserDefinedBRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetUserDefinedBProperties, request)
		return response.user_defined_b_props

	def _setUserDefinedBProperties(self, userDefinedBProperties: BoredWeakRockUserDefinedBService_pb2.UserDefinedBProperties):
		request = BoredWeakRockUserDefinedBService_pb2.SetUserDefinedBRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, user_defined_b_props=userDefinedBProperties)
		self._client.callFunction(self._stub.SetUserDefinedBProperties, request)

	def setB(self, b: float):
		properties = self._getUserDefinedBProperties()
		properties.user_def_b = b
		self._setUserDefinedBProperties(properties)

	def getB(self) -> float:
		properties = self._getUserDefinedBProperties()
		return properties.user_def_b