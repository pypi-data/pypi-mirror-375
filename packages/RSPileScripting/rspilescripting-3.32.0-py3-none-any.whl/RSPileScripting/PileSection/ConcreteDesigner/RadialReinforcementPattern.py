from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.ConcreteDesignerRadialReinforcementPatternService_pb2 as ConcreteDesignerRadialReinforcementPatternService_pb2
import RSPileScripting.generated_python_files.pile_section_services.ConcreteDesignerRadialReinforcementPatternService_pb2_grpc as ConcreteDesignerRadialReinforcementPatternService_pb2_grpc
from enum import Enum

class RebarReferencePointMethod(Enum):
	COVER_DEPTH = 1
	DISTANCE_FROM_CENTER = 2

class RadialReinforcementPattern:
	def __init__(self, model_id: str, pattern_id: str, client: Client):
		self._pattern_id = pattern_id
		self._client = client
		self._model_id = model_id
		self._stub = ConcreteDesignerRadialReinforcementPatternService_pb2_grpc.ConcreteDesignerRadialReinforcementPatternServiceStub(self._client.channel)

	def _getRadialPatternProperties(self) -> ConcreteDesignerRadialReinforcementPatternService_pb2.RadialReinforcementPatternProperties:
		request = ConcreteDesignerRadialReinforcementPatternService_pb2.GetRadialReinforcementPatternPropertiesRequest(
			session_id=self._client.sessionID, pattern_id=self._pattern_id)
		response = self._client.callFunction(self._stub.GetRadialReinforcementPattern, request)
		return response.radial_pattern_props

	def _setRadialPatternProperties(self, properties: ConcreteDesignerRadialReinforcementPatternService_pb2.RadialReinforcementPatternProperties):
		request = ConcreteDesignerRadialReinforcementPatternService_pb2.SetRadialReinforcementPatternPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pattern_id=self._pattern_id, 
			radial_pattern_props=properties)
		self._client.callFunction(self._stub.SetRadialReinforcementPattern, request)

	def getNumberOfBars(self) -> int:
		properties = self._getRadialPatternProperties()
		return properties.num_bars_radial

	def setNumberOfBars(self, numberOfBars: int):
		properties = self._getRadialPatternProperties()
		properties.num_bars_radial = numberOfBars
		self._setRadialPatternProperties(properties)

	def getAngleFromXAxis(self) -> float:
		properties = self._getRadialPatternProperties()
		return properties.rotation_angle

	def setAngleFromXAxis(self, angleFromXAxis: float):
		properties = self._getRadialPatternProperties()
		properties.rotation_angle = angleFromXAxis
		self._setRadialPatternProperties(properties)

	def getRebarLocationRefPoint(self) -> RebarReferencePointMethod:
		properties = self._getRadialPatternProperties()
		if properties.use_cover_depth:
			return RebarReferencePointMethod.COVER_DEPTH
		else:
			return RebarReferencePointMethod.DISTANCE_FROM_CENTER

	def setRebarLocationRefPoint(self, useCoverDepth: RebarReferencePointMethod):
		properties = self._getRadialPatternProperties()
		if useCoverDepth == RebarReferencePointMethod.COVER_DEPTH:
			properties.use_cover_depth = True
		elif useCoverDepth == RebarReferencePointMethod.DISTANCE_FROM_CENTER:
			properties.use_cover_depth = False
		else:
			raise ValueError("Invalid Rebar Reference Point Method")
		self._setRadialPatternProperties(properties)

	def getCoverDepth(self) -> float:
		properties = self._getRadialPatternProperties()
		return properties.radial_cover_depth

	def setCoverDepth(self, coverDepth: float):
		properties = self._getRadialPatternProperties()
		properties.radial_cover_depth = coverDepth
		self._setRadialPatternProperties(properties)

	def getDistanceFromCenter(self) -> float:
		properties = self._getRadialPatternProperties()
		return properties.dist_from_center

	def setDistanceFromCenter(self, distanceFromCenter: float):
		properties = self._getRadialPatternProperties()
		properties.dist_from_center = distanceFromCenter
		self._setRadialPatternProperties(properties)