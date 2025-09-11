from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.LateralSoftClayWithUserDefinedJService_pb2 as LateralSoftClayWithUserDefinedJService_pb2
import RSPileScripting.generated_python_files.soil_services.LateralSoftClayWithUserDefinedJService_pb2_grpc as LateralSoftClayWithUserDefinedJService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class LateralSoftClayWithUserDefinedJDatumProperties(Enum):
	STRAIN_FACTOR = "LAT_SOFT_CLAY_WJ_UNDRAINED_SHEAR_STRENGTH"
	UNDRAINED_SHEAR_STRENGTH = "LAT_SOFT_CLAY_WJ_STRAIN_FACTOR"
	STIFFNESS_FACTOR = "LAT_SOFT_CLAY_WJ_STIFFNESS_FACTOR"

class SoftClayWithUserDefinedJ:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = LateralSoftClayWithUserDefinedJService_pb2_grpc.LateralSoftClayWithUserDefinedJServiceStub(self._client.channel)
		self.Datum: Datum[LateralSoftClayWithUserDefinedJDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.LATERAL
		)

	def _getSoftClayWithUserDefinedJProperties(self) -> LateralSoftClayWithUserDefinedJService_pb2.SoftClayWithUserDefinedJProperties:
		request = LateralSoftClayWithUserDefinedJService_pb2.GetSoftClayWithUserDefinedJRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetSoftClayWithUserDefinedJProperties, request)
		return response.soft_clay_props

	def _setSoftClayWithUserDefinedJProperties(self, softClayWithUserDefinedJProps: LateralSoftClayWithUserDefinedJService_pb2.SoftClayWithUserDefinedJProperties):
		request = LateralSoftClayWithUserDefinedJService_pb2.SetSoftClayWithUserDefinedJRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, soft_clay_props=softClayWithUserDefinedJProps)
		self._client.callFunction(self._stub.SetSoftClayWithUserDefinedJProperties, request)

	def getStrainFactor(self) -> float:
		properties = self._getSoftClayWithUserDefinedJProperties()
		return properties.strain_factor_SCwJ

	def setStrainFactor(self, strainFactor: float):
		properties = self._getSoftClayWithUserDefinedJProperties()
		properties.strain_factor_SCwJ = strainFactor
		self._setSoftClayWithUserDefinedJProperties(properties)

	def getUndrainedShearStrength(self) -> float:
		properties = self._getSoftClayWithUserDefinedJProperties()
		return properties.undrained_shear_strength_SCwJ

	def setUndrainedShearStrength(self, undrainedShearStrength: float):
		properties = self._getSoftClayWithUserDefinedJProperties()
		properties.undrained_shear_strength_SCwJ = undrainedShearStrength
		self._setSoftClayWithUserDefinedJProperties(properties)

	def getStiffnessFactor(self) -> float:
		properties = self._getSoftClayWithUserDefinedJProperties()
		return properties.stiffness_factor_J_SCwJ

	def setStiffnessFactor(self, stiffnessFactor: float):
		properties = self._getSoftClayWithUserDefinedJProperties()
		properties.stiffness_factor_J_SCwJ = stiffnessFactor
		self._setSoftClayWithUserDefinedJProperties(properties)