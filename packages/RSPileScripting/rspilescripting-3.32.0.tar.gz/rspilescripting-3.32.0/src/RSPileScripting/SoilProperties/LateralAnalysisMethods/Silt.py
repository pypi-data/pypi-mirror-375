from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.LateralSiltService_pb2 as LateralSiltService_pb2
import RSPileScripting.generated_python_files.soil_services.LateralSiltService_pb2_grpc as LateralSiltService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class LateralSiltDatumProperties(Enum):
	COHESION = "LAT_SILT_COHESION"
	FRICTION_ANGLE = "LAT_SILT_PHI"
	INITIAL_STIFFNESS = "LAT_SILT_INITIAL_STIFFNESS"

class Silt:
	"""
	Examples:
	:ref:`soil properties lateral pile analysis`
	"""
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = LateralSiltService_pb2_grpc.LateralSiltServiceStub(self._client.channel)
		self.Datum: Datum[LateralSiltDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.LATERAL
		)

	def _getSiltProperties(self) -> LateralSiltService_pb2.SiltProperties:
		request = LateralSiltService_pb2.GetSiltRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetSiltProperties, request)
		return response.silt_props

	def _setSiltProperties(self, siltProps: LateralSiltService_pb2.SiltProperties):
		request = LateralSiltService_pb2.SetSiltRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, silt_props=siltProps)
		self._client.callFunction(self._stub.SetSiltProperties, request)

	def getCohesion(self) -> float:
		properties = self._getSiltProperties()
		return properties.cohesion_Silt

	def setCohesion(self, cohesion: float):
		properties = self._getSiltProperties()
		properties.cohesion_Silt = cohesion
		self._setSiltProperties(properties)

	def getFrictionAngle(self) -> float:
		properties = self._getSiltProperties()
		return properties.friction_angle_Silt

	def setFrictionAngle(self, frictionAngle: float):
		properties = self._getSiltProperties()
		properties.friction_angle_Silt = frictionAngle
		self._setSiltProperties(properties)

	def getInitialStiffness(self) -> float:
		properties = self._getSiltProperties()
		return properties.initial_stiffness_Silt

	def setInitialStiffness(self, initialStiffness: float):
		properties = self._getSiltProperties()
		properties.initial_stiffness_Silt = initialStiffness
		self._setSiltProperties(properties)