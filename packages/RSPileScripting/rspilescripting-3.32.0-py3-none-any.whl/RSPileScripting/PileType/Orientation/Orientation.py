from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_type_services.PileTypeOrientationService_pb2 as PileTypeOrientationService_pb2
import RSPileScripting.generated_python_files.pile_type_services.PileTypeOrientationService_pb2_grpc as PileTypeOrientationService_pb2_grpc
from RSPileScripting.PileType.Orientation.Vector import Vector
from RSPileScripting.PileType.Orientation.AlphaBeta import AlphaBeta
from enum import Enum

class OrientationType(Enum):
	ALPHA_BETA = PileTypeOrientationService_pb2.OrientationType.OT_TREND_PLUNGE
	VECTOR = PileTypeOrientationService_pb2.OrientationType.OT_VECTOR

class Orientation:
	"""
		Examples:
		:ref:`pile types pile analysis`
	"""
	def __init__(self, model_id: str, pile_type_id: str, client: Client):
		self.pile_type_id = pile_type_id
		self._client = client
		self._model_id = model_id
		self._stub = PileTypeOrientationService_pb2_grpc.PileTypeOrientationServiceStub(self._client.channel)
		self.Vector = Vector(self._model_id, self.pile_type_id, self._client)
		self.AlphaBeta = AlphaBeta(self._model_id, self.pile_type_id, self._client)

	def _getPileTypeOrientationProperties(self) -> PileTypeOrientationService_pb2.OrientationProperties:
		request = PileTypeOrientationService_pb2.GetOrientationPropertiesRequest(
			session_id=self._client.sessionID, pile_type_id=self.pile_type_id)
		response = self._client.callFunction(self._stub.GetOrientationProperties, request)
		return response.orientation_props

	def _setPileTypeOrientationProperties(self, orientationProps: PileTypeOrientationService_pb2.OrientationProperties):
		request = PileTypeOrientationService_pb2.SetOrientationPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_type_id=self.pile_type_id, 
			orientation_props=orientationProps)
		self._client.callFunction(self._stub.SetOrientationProperties, request)

	def getOrientationType(self) -> OrientationType:
		properties = self._getPileTypeOrientationProperties()
		return OrientationType(properties.m_orientation_type)
	
	def setOrientationType(self, orientationType: OrientationType):
		properties = self._getPileTypeOrientationProperties()
		properties.m_orientation_type = orientationType.value
		self._setPileTypeOrientationProperties(properties)

	def getRotationAngle(self) -> float:
		properties = self._getPileTypeOrientationProperties()
		return properties.rotation_angle

	def setRotationAngle(self, rotationAngle: float):
		properties = self._getPileTypeOrientationProperties()
		properties.rotation_angle = rotationAngle
		self._setPileTypeOrientationProperties(properties)