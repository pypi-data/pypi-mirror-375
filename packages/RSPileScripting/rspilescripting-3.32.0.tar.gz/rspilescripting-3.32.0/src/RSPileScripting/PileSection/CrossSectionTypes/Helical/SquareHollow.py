from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.HelicalCrossSectionSquareHollowService_pb2 as HelicalCrossSectionSquareHollowService_pb2
import RSPileScripting.generated_python_files.pile_section_services.HelicalCrossSectionSquareHollowService_pb2_grpc as HelicalCrossSectionSquareHollowService_pb2_grpc

class SquareHollow:
	"""
	Examples:
	:ref:`pile sections helical`
	"""
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = HelicalCrossSectionSquareHollowService_pb2_grpc.HelicalCrossSectionSquareHollowServiceStub(self._client.channel)

	def _getSquareHollowProperties(self) -> HelicalCrossSectionSquareHollowService_pb2.SquareHollowProperties:
		request = HelicalCrossSectionSquareHollowService_pb2.GetSquareHollowPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetSquareHollowProperties, request)
		return response.square_hollow_props

	def _setSquareHollowProperties(self, squareHollowProps: HelicalCrossSectionSquareHollowService_pb2.SquareHollowProperties):
		request = HelicalCrossSectionSquareHollowService_pb2.SetSquareHollowPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			square_hollow_props=squareHollowProps)
		self._client.callFunction(self._stub.SetSquareHollowProperties, request)

	def getOuterSideLength(self) -> float:
		properties = self._getSquareHollowProperties()
		return properties.outer_side_length
	
	def setOuterSideLength(self, outerSideLength: float):
		properties = self._getSquareHollowProperties()
		properties.outer_side_length = outerSideLength
		self._setSquareHollowProperties(properties)

	def getThickness(self) -> float:
		properties = self._getSquareHollowProperties()
		return properties.square_thickness
	
	def setThickness(self, thickness: float):
		properties = self._getSquareHollowProperties()
		properties.square_thickness = thickness
		self._setSquareHollowProperties(properties)