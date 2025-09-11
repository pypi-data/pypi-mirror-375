from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.BoredCrossSectionRectangularService_pb2 as BoredCrossSectionRectangularService_pb2
import RSPileScripting.generated_python_files.pile_section_services.BoredCrossSectionRectangularService_pb2_grpc as BoredCrossSectionRectangularService_pb2_grpc

class Rectangular:
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = BoredCrossSectionRectangularService_pb2_grpc.BoredCrossSectionRectangularServiceStub(self._client.channel)

	def _getRectangularProperties(self) -> BoredCrossSectionRectangularService_pb2.RectangularProperties:
		request = BoredCrossSectionRectangularService_pb2.GetRectangularPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetRectangularProperties, request)
		return response.rectangular_props

	def _setRectangularProperties(self, rectangularProps: BoredCrossSectionRectangularService_pb2.RectangularProperties):
		request = BoredCrossSectionRectangularService_pb2.SetRectangularPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			rectangular_props=rectangularProps)
		self._client.callFunction(self._stub.SetRectangularProperties, request)

	def getWidth(self) -> float:
		properties = self._getRectangularProperties()
		return properties.width
	
	def setWidth(self, width: float):
		properties = self._getRectangularProperties()
		properties.width = width
		self._setRectangularProperties(properties)

	def getBreadth(self) -> float:
		properties = self._getRectangularProperties()
		return properties.breadth
	
	def setBreadth(self, breadth: float):
		properties = self._getRectangularProperties()
		properties.breadth = breadth
		self._setRectangularProperties(properties)