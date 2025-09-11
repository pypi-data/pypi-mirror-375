from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.LateralSoftClayService_pb2 as LateralSoftClayService_pb2
import RSPileScripting.generated_python_files.soil_services.LateralSoftClayService_pb2_grpc as LateralSoftClayService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class LateralSoftClayDatumProperties(Enum):
	STRAIN_FACTOR = "LAT_SOFT_CLAY_STRAIN_FACTOR"
	UNDRAINED_SHEAR_STRENGTH = "LAT_SOFT_CLAY_SHEAR_STRENGTH"

class SoftClay:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = LateralSoftClayService_pb2_grpc.LateralSoftClayServiceStub(self._client.channel)
		self.Datum: Datum[LateralSoftClayDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.LATERAL
		)

	def _getSoftClayProperties(self) -> LateralSoftClayService_pb2.SoftClayProperties:
		request = LateralSoftClayService_pb2.GetSoftClayRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetSoftClayProperties, request)
		return response.soft_clay_props

	def _setSoftClayProperties(self, softClayProps: LateralSoftClayService_pb2.SoftClayProperties):
		request = LateralSoftClayService_pb2.SetSoftClayRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, soft_clay_props=softClayProps)
		self._client.callFunction(self._stub.SetSoftClayProperties, request)

	def getStrainFactor(self) -> float:
		properties = self._getSoftClayProperties()
		return properties.strain_factor_scs

	def setStrainFactor(self, strainFactor: float):
		properties = self._getSoftClayProperties()
		properties.strain_factor_scs = strainFactor
		self._setSoftClayProperties(properties)
		
	def getUndrainedShearStrength(self) -> float:
		properties = self._getSoftClayProperties()
		return properties.shear_strength_scs

	def setUndrainedShearStrength(self, undrainedShearStrength: float):
		properties = self._getSoftClayProperties()
		properties.shear_strength_scs = undrainedShearStrength
		self._setSoftClayProperties(properties)