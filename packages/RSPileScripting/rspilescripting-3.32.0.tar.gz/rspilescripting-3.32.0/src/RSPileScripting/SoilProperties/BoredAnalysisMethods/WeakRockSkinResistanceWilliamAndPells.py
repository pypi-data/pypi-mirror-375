from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.BoredWeakRockWilliamAndPellsService_pb2 as BoredWeakRockWilliamAndPellsService_pb2
import RSPileScripting.generated_python_files.soil_services.BoredWeakRockWilliamAndPellsService_pb2_grpc as BoredWeakRockWilliamAndPellsService_pb2_grpc

class WilliamAndPells:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = BoredWeakRockWilliamAndPellsService_pb2_grpc.BoredWeakRockWilliamAndPellsServiceStub(self._client.channel)

	def _getWilliamAndPellsProperties(self) -> BoredWeakRockWilliamAndPellsService_pb2.WilliamAndPellsProperties:
		request = BoredWeakRockWilliamAndPellsService_pb2.GetWilliamAndPellsRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetWilliamAndPellsProperties, request)
		return response.william_and_pells_props

	def _setWilliamAndPellsProperties(self, williamAndPellsProperties: BoredWeakRockWilliamAndPellsService_pb2.WilliamAndPellsProperties):
		request = BoredWeakRockWilliamAndPellsService_pb2.SetWilliamAndPellsRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, william_and_pells_props=williamAndPellsProperties)
		self._client.callFunction(self._stub.SetWilliamAndPellsProperties, request)

	def setAverageRQD(self, averageRQD: float):
		properties = self._getWilliamAndPellsProperties()
		properties.average_rqd = averageRQD
		self._setWilliamAndPellsProperties(properties)

	def getAverageRQD(self) -> float:
		properties = self._getWilliamAndPellsProperties()
		return properties.average_rqd
