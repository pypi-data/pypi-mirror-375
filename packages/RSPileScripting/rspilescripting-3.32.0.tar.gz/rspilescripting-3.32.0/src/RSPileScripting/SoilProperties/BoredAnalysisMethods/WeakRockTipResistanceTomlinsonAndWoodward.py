from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.BoredWeakRockTomlinsonAndWoodwardService_pb2 as BoredWeakRockTomlinsonAndWoodwardService_pb2
import RSPileScripting.generated_python_files.soil_services.BoredWeakRockTomlinsonAndWoodwardService_pb2_grpc as BoredWeakRockTomlinsonAndWoodwardService_pb2_grpc

class TomlinsonAndWoodward:
	"""
	Examples:
	:ref:`soil properties bored`
	"""
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = BoredWeakRockTomlinsonAndWoodwardService_pb2_grpc.BoredWeakRockTomlinsonAndWoodwardServiceStub(self._client.channel)

	def _getTomlinsonAndWoodwardProperties(self) -> BoredWeakRockTomlinsonAndWoodwardService_pb2.TomlinsonAndWoodwardProperties:
		request = BoredWeakRockTomlinsonAndWoodwardService_pb2.GetTomlinsonAndWoodwardRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetTomlinsonAndWoodwardProperties, request)
		return response.tomlinson_and_woodward_props

	def _setTomlinsonAndWoodwardProperties(self, tomlinsonAndWoodwardProperties: BoredWeakRockTomlinsonAndWoodwardService_pb2.TomlinsonAndWoodwardProperties):
		request = BoredWeakRockTomlinsonAndWoodwardService_pb2.SetTomlinsonAndWoodwardRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, tomlinson_and_woodward_props=tomlinsonAndWoodwardProperties)
		self._client.callFunction(self._stub.SetTomlinsonAndWoodwardProperties, request)

	def setInternalFrictionAngle(self, internalFrictionAngle: float):
		properties = self._getTomlinsonAndWoodwardProperties()
		properties.angle_of_friction = internalFrictionAngle
		self._setTomlinsonAndWoodwardProperties(properties)

	def getInternalFrictionAngle(self) -> float:
		properties = self._getTomlinsonAndWoodwardProperties()
		return properties.angle_of_friction