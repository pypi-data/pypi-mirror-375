from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.BoredCrossSectionSquareService_pb2 as BoredCrossSectionSquareService_pb2
import RSPileScripting.generated_python_files.pile_section_services.BoredCrossSectionSquareService_pb2_grpc as BoredCrossSectionSquareService_pb2_grpc

class Square:
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = BoredCrossSectionSquareService_pb2_grpc.BoredCrossSectionSquareServiceStub(self._client.channel)

	def _getSquareProperties(self) -> BoredCrossSectionSquareService_pb2.SquareProperties:
		request = BoredCrossSectionSquareService_pb2.GetSquarePropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetSquareProperties, request)
		return response.square_props

	def _setSquareProperties(self, squareProps: BoredCrossSectionSquareService_pb2.SquareProperties):
		request = BoredCrossSectionSquareService_pb2.SetSquarePropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			square_props=squareProps)
		self._client.callFunction(self._stub.SetSquareProperties, request)

	def getSideLength(self) -> float:
		properties = self._getSquareProperties()
		return properties.side_length
	
	def setSideLength(self, sideLength: float):
		properties = self._getSquareProperties()
		properties.side_length = sideLength
		self._setSquareProperties(properties)