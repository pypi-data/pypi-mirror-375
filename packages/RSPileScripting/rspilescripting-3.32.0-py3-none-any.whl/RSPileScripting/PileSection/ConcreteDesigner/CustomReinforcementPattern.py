from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.ConcreteDesignerCustomReinforcementPatternService_pb2 as ConcreteDesignerCustomReinforcementPatternService_pb2
import RSPileScripting.generated_python_files.pile_section_services.ConcreteDesignerCustomReinforcementPatternService_pb2_grpc as ConcreteDesignerCustomReinforcementPatternService_pb2_grpc

class CustomReinforcementPattern:
	def __init__(self, model_id: str, pattern_id: str, client: Client):
		self._pattern_id = pattern_id
		self._client = client
		self._model_id = model_id
		self._stub = ConcreteDesignerCustomReinforcementPatternService_pb2_grpc.ConcreteDesignerCustomReinforcementPatternServiceStub(self._client.channel)

	def _getCustomPatternProperties(self) -> ConcreteDesignerCustomReinforcementPatternService_pb2.CustomReinforcementPatternProperties:
		request = ConcreteDesignerCustomReinforcementPatternService_pb2.GetCustomReinforcementPatternPropertiesRequest(
			session_id=self._client.sessionID, pattern_id=self._pattern_id)
		response = self._client.callFunction(self._stub.GetCustomReinforcementPattern, request)
		return response.custom_pattern_props

	def _setCustomPatternProperties(self, properties: ConcreteDesignerCustomReinforcementPatternService_pb2.CustomReinforcementPatternProperties):
		request = ConcreteDesignerCustomReinforcementPatternService_pb2.SetCustomReinforcementPatternPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pattern_id=self._pattern_id, 
			custom_pattern_props=properties)
		self._client.callFunction(self._stub.SetCustomReinforcementPattern, request)

	def getCustomLocations(self) -> list[tuple[float, float]]:
		properties = self._getCustomPatternProperties()
		return [(location.x_coordinate, location.y_coordinate) for location in properties.custom_locations]

	def setCustomLocations(self, customLocations: list[tuple[float, float]]):
		properties = self._getCustomPatternProperties()
		del properties.custom_locations[:]
		properties.custom_locations.extend(
			ConcreteDesignerCustomReinforcementPatternService_pb2.BarLocations(x_coordinate=x, y_coordinate=y)
			for x, y in customLocations
		)
		self._setCustomPatternProperties(properties)