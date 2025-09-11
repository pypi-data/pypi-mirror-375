from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.HelicalCrossSectionSquareSolidService_pb2 as HelicalCrossSectionSquareSolidService_pb2
import RSPileScripting.generated_python_files.pile_section_services.HelicalCrossSectionSquareSolidService_pb2_grpc as HelicalCrossSectionSquareSolidService_pb2_grpc

class SquareSolid:
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = HelicalCrossSectionSquareSolidService_pb2_grpc.HelicalCrossSectionSquareSolidServiceStub(self._client.channel)

	def _getSquareSolidProperties(self) -> HelicalCrossSectionSquareSolidService_pb2.SquareSolidProperties:
		request = HelicalCrossSectionSquareSolidService_pb2.GetSquareSolidPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetSquareSolidProperties, request)
		return response.square_solid_props

	def _setSquareSolidProperties(self, squareSolidProps: HelicalCrossSectionSquareSolidService_pb2.SquareSolidProperties):
		request = HelicalCrossSectionSquareSolidService_pb2.SetSquareSolidPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			square_solid_props=squareSolidProps)
		self._client.callFunction(self._stub.SetSquareSolidProperties, request)

	def getSideLength(self) -> float:
		properties = self._getSquareSolidProperties()
		return properties.side_length
	
	def setSideLength(self, sideLength: float):
		properties = self._getSquareSolidProperties()
		properties.side_length = sideLength
		self._setSquareSolidProperties(properties)