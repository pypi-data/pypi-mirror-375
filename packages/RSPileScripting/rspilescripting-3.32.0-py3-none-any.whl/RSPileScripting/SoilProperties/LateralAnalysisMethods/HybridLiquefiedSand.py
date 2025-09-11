from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.LateralHybridLiquefiedSandService_pb2 as LateralHybridLiquefiedSandService_pb2
import RSPileScripting.generated_python_files.soil_services.LateralHybridLiquefiedSandService_pb2_grpc as LateralHybridLiquefiedSandService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class LateralHybridLiquefiedSandDatumProperties(Enum):
	STRAIN_FACTOR = "LAT_HYBRID_LSAND_STRAIN_FACTOR"
	UNDRAINED_SHEAR_STRENGTH = "LAT_HYBRID_LSAND_SHEAR_STRENGTH"
	SPT_VALUE = "LAT_HYBRID_LSAND_SPT"

class HybridLiquefiedSand:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = LateralHybridLiquefiedSandService_pb2_grpc.LateralHybridLiquefiedSandServiceStub(self._client.channel)
		self.Datum: Datum[LateralHybridLiquefiedSandDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.LATERAL
		)

	def _getHybridLiquefiedSandProperties(self) -> LateralHybridLiquefiedSandService_pb2.HybridLiquefiedSandProperties:
		request = LateralHybridLiquefiedSandService_pb2.GetHybridLiquefiedSandRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetHybridLiquefiedSandProperties, request)
		return response.hybrid_liquefied_sand_props

	def _setHybridLiquefiedSandProperties(self, hybridLiquefiedSandProps: LateralHybridLiquefiedSandService_pb2.HybridLiquefiedSandProperties):
		request = LateralHybridLiquefiedSandService_pb2.SetHybridLiquefiedSandRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, hybrid_liquefied_sand_props=hybridLiquefiedSandProps)
		self._client.callFunction(self._stub.SetHybridLiquefiedSandProperties, request)

	def getUseSPT(self) -> bool:
		properties = self._getHybridLiquefiedSandProperties()
		return properties.hybrid_lsand_use_spt

	def setUseSPT(self, useSPT: bool):
		properties = self._getHybridLiquefiedSandProperties()
		properties.hybrid_lsand_use_spt = useSPT
		self._setHybridLiquefiedSandProperties(properties)

	def getUndrainedShearStrength(self) -> float:
		properties = self._getHybridLiquefiedSandProperties()
		return properties.undrained_shear_strength_HLS

	def setUndrainedShearStrength(self, undrainedShearStrength: float):
		properties = self._getHybridLiquefiedSandProperties()
		properties.undrained_shear_strength_HLS = undrainedShearStrength
		self._setHybridLiquefiedSandProperties(properties)

	def getStrainFactor(self) -> float:
		properties = self._getHybridLiquefiedSandProperties()
		return properties.strain_factor_HLS

	def setStrainFactor(self, strainFactor: float):
		properties = self._getHybridLiquefiedSandProperties()
		properties.strain_factor_HLS = strainFactor
		self._setHybridLiquefiedSandProperties(properties)

	def getSPTValue(self) -> float:
		properties = self._getHybridLiquefiedSandProperties()
		return properties.spt_value_HLS

	def setSPTValue(self, sptValue: float):
		properties = self._getHybridLiquefiedSandProperties()
		properties.spt_value_HLS = sptValue
		self._setHybridLiquefiedSandProperties(properties)