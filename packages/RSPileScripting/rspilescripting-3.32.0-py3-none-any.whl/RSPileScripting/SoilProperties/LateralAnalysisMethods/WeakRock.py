from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.LateralWeakRockService_pb2 as LateralWeakRockService_pb2
import RSPileScripting.generated_python_files.soil_services.LateralWeakRockService_pb2_grpc as LateralWeakRockService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class LateralWeakRockDatumProperties(Enum):
	UNIAXIAL_COMPRESSIVE_STRENGTH = "LAT_WEAK_ROCK_UNIAXIAL_COMP_STR"
	REACTION_MODULUS = "LAT_WEAK_ROCK_REACTION_MOD_ROCK"
	ROCK_QUALITY_DESIGNATION = "LAT_WEAK_ROCK_RQD"
	CONSTANT_K_RM ="LAT_WEAK_ROCK_KRM"

class WeakRock:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = LateralWeakRockService_pb2_grpc.LateralWeakRockServiceStub(self._client.channel)
		self.Datum: Datum[LateralWeakRockDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.LATERAL
		)

	def _getWeakRockProperties(self) -> LateralWeakRockService_pb2.WeakRockProperties:
		request = LateralWeakRockService_pb2.GetWeakRockRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetWeakRockProperties, request)
		return response.weak_rock_props

	def _setWeakRockProperties(self, weakRockProps: LateralWeakRockService_pb2.WeakRockProperties):
		request = LateralWeakRockService_pb2.SetWeakRockRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, weak_rock_props=weakRockProps)
		self._client.callFunction(self._stub.SetWeakRockProperties, request)

	def getUniaxialCompressiveStrength(self) -> float:
		properties = self._getWeakRockProperties()
		return properties.compressive_strength_WR

	def setUniaxialCompressiveStrength(self, uniaxialCompressiveStrength: float):
		properties = self._getWeakRockProperties()
		properties.compressive_strength_WR = uniaxialCompressiveStrength
		self._setWeakRockProperties(properties)

	def getReactionModulusOfRock(self) -> float:
		properties = self._getWeakRockProperties()
		return properties.reaction_modulus_WR

	def setReactionModulusOfRock(self, reactionModulusOfRock: float):
		properties = self._getWeakRockProperties()
		properties.reaction_modulus_WR = reactionModulusOfRock
		self._setWeakRockProperties(properties)

	def getRockQualityDesignation(self) -> float:
		properties = self._getWeakRockProperties()
		return properties.rock_quality_designation_WR

	def setRockQualityDesignation(self, rockQualityDesignation: float):
		properties = self._getWeakRockProperties()
		properties.rock_quality_designation_WR = rockQualityDesignation
		self._setWeakRockProperties(properties)

	def getConstantKrm(self) -> float:
		properties = self._getWeakRockProperties()
		return properties.krm_WR

	def setConstantKrm(self, constantKrm: float):
		properties = self._getWeakRockProperties()
		properties.krm_WR = constantKrm
		self._setWeakRockProperties(properties)