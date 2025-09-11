from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.LateralSubmergedStiffClayService_pb2 as LateralSubmergedStiffClayService_pb2
import RSPileScripting.generated_python_files.soil_services.LateralSubmergedStiffClayService_pb2_grpc as LateralSubmergedStiffClayService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class LateralSubmergedStiffClayDatumProperties(Enum):
	STRAIN_FACTOR = "LAT_STIFF_CLAY_STRAIN_FACTOR"
	SHEAR_STRENGTH = "LAT_STIFF_CLAY_SHEAR_STRENGTH"
	K_S = "LAT_STIFF_CLAY_KS"

class SubmergedStiffClay:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = LateralSubmergedStiffClayService_pb2_grpc.LateralSubmergedStiffClayServiceStub(self._client.channel)
		self.Datum: Datum[LateralSubmergedStiffClayDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.LATERAL
		)

	def _getSubmergedStiffClayProperties(self) -> LateralSubmergedStiffClayService_pb2.SubmergedStiffClayProperties:
		request = LateralSubmergedStiffClayService_pb2.GetSubmergedStiffClayRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetSubmergedStiffClayProperties, request)
		return response.submerged_stiff_clay_props

	def _setSubmergedStiffClayProperties(self, submergedStiffClayProps: LateralSubmergedStiffClayService_pb2.SubmergedStiffClayProperties):
		request = LateralSubmergedStiffClayService_pb2.SetSubmergedStiffClayRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, submerged_stiff_clay_props=submergedStiffClayProps)
		self._client.callFunction(self._stub.SetSubmergedStiffClayProperties, request)

	def getUndrainedShearStrength(self) -> float:
		properties = self._getSubmergedStiffClayProperties()
		return properties.shear_strength_SSC

	def setUndrainedShearStrength(self, undrainedShearStrength: float):
		properties = self._getSubmergedStiffClayProperties()
		properties.shear_strength_SSC = undrainedShearStrength
		self._setSubmergedStiffClayProperties(properties)

	def getStrainFactor(self) -> float:
		properties = self._getSubmergedStiffClayProperties()
		return properties.strain_factor_SSC

	def setStrainFactor(self, strainFactor: float):
		properties = self._getSubmergedStiffClayProperties()
		properties.strain_factor_SSC = strainFactor
		self._setSubmergedStiffClayProperties(properties)

	def getKs(self) -> float:
		properties = self._getSubmergedStiffClayProperties()
		return properties.ks_SSC

	def setKs(self, ks: float):
		properties = self._getSubmergedStiffClayProperties()
		properties.ks_SSC = ks
		self._setSubmergedStiffClayProperties(properties)