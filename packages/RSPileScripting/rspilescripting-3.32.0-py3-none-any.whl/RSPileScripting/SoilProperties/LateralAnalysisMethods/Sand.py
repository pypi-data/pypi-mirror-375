from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.LateralSandService_pb2 as LateralSandService_pb2
import RSPileScripting.generated_python_files.soil_services.LateralSandService_pb2_grpc as LateralSandService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class LateralSandDatumProperties(Enum):
	K_PY = "LAT_SAND_KPY"
	K_PY_SAT = "LAT_SAND_KPY_SAT"
	FRICTION_ANGLE = "LAT_SAND_FRICTION_ANGLE"

class Sand:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = LateralSandService_pb2_grpc.LateralSandServiceStub(self._client.channel)
		self.Datum: Datum[LateralSandDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.LATERAL
		)

	def _getSandProperties(self) -> LateralSandService_pb2.SandProperties:
		request = LateralSandService_pb2.GetSandRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetSandProperties, request)
		return response.sand_props

	def _setSandProperties(self, sandProps: LateralSandService_pb2.SandProperties):
		request = LateralSandService_pb2.SetSandRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, sand_props=sandProps)
		self._client.callFunction(self._stub.SetSandProperties, request)

	def getFrictionAngle(self) -> float:
		properties = self._getSandProperties()
		return properties.friction_angle_S

	def setFrictionAngle(self, frictionAngle: float):
		properties = self._getSandProperties()
		properties.friction_angle_S = frictionAngle
		self._setSandProperties(properties)

	def getKpy(self) -> float:
		properties = self._getSandProperties()
		return properties.kpy_S

	def setKpy(self, kpy: float):
		properties = self._getSandProperties()
		properties.kpy_S = kpy
		self._setSandProperties(properties)

	def getSaturatedKpy(self) -> float:
		properties = self._getSandProperties()
		return properties.kpy_S_GW

	def setSaturatedKpy(self, saturatedKpy: float):
		properties = self._getSandProperties()
		properties.kpy_S_GW = saturatedKpy
		self._setSandProperties(properties)