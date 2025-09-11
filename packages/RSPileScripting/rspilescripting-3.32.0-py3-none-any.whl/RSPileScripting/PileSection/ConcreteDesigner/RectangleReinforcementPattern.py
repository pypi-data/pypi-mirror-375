from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.ConcreteDesignerRectangleReinforcementPatternService_pb2 as ConcreteDesignerRectangleReinforcementPatternService_pb2
import RSPileScripting.generated_python_files.pile_section_services.ConcreteDesignerRectangleReinforcementPatternService_pb2_grpc as ConcreteDesignerRectangleReinforcementPatternService_pb2_grpc

class RectangleReinforcementPattern:
	def __init__(self, model_id: str, pattern_id: str, client: Client):
		self._pattern_id = pattern_id
		self._client = client
		self._model_id = model_id
		self._stub = ConcreteDesignerRectangleReinforcementPatternService_pb2_grpc.ConcreteDesignerRectangleReinforcementPatternServiceStub(self._client.channel)

	def _getRectanglePatternProperties(self) -> ConcreteDesignerRectangleReinforcementPatternService_pb2.RectangleReinforcementPatternProperties:
		request = ConcreteDesignerRectangleReinforcementPatternService_pb2.GetRectangleReinforcementPatternPropertiesRequest(
			session_id=self._client.sessionID, pattern_id=self._pattern_id)
		response = self._client.callFunction(self._stub.GetRectangleReinforcementPattern, request)
		return response.rectangle_pattern_props

	def _setRectanglePatternProperties(self, properties: ConcreteDesignerRectangleReinforcementPatternService_pb2.RectangleReinforcementPatternProperties):
		request = ConcreteDesignerRectangleReinforcementPatternService_pb2.SetRectangleReinforcementPatternPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pattern_id=self._pattern_id, 
			rectangle_pattern_props=properties)
		self._client.callFunction(self._stub.SetRectangleReinforcementPattern, request)

	def getIsPeripheralBars(self) -> bool:
		properties = self._getRectanglePatternProperties()
		return properties.peripheral_bars

	def setIsPeripheralBars(self, isPeripheralBars: bool):
		properties = self._getRectanglePatternProperties()
		properties.peripheral_bars = isPeripheralBars
		self._setRectanglePatternProperties(properties)

	def getNumberOfBarsX(self) -> int:
		properties = self._getRectanglePatternProperties()
		return properties.num_bars_x

	def setNumberOfBarsX(self, numBarsX: int):
		properties = self._getRectanglePatternProperties()
		properties.num_bars_x = numBarsX
		self._setRectanglePatternProperties(properties)

	def getNumberOfBarsY(self) -> int:
		properties = self._getRectanglePatternProperties()
		return properties.num_bars_y

	def setNumberOfBarsY(self, numBarsY: int):
		properties = self._getRectanglePatternProperties()
		properties.num_bars_y = numBarsY
		self._setRectanglePatternProperties(properties)

	def getMinCoverDepth(self) -> int:
		properties = self._getRectanglePatternProperties()
		return properties.min_cover_depth

	def setMinCoverDepth(self, minCoverDepth: int):
		properties = self._getRectanglePatternProperties()
		properties.min_cover_depth = minCoverDepth
		self._setRectanglePatternProperties(properties)