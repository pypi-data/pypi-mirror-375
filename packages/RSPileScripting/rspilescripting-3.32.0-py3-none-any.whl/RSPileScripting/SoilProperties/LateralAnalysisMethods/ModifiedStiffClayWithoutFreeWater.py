from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.LateralModifiedStiffClayWithoutFreeWaterService_pb2 as LateralModifiedStiffClayWithoutFreeWaterService_pb2
import RSPileScripting.generated_python_files.soil_services.LateralModifiedStiffClayWithoutFreeWaterService_pb2_grpc as LateralModifiedStiffClayWithoutFreeWaterService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class LateralModifiedStiffClayWithoutFreeWaterDatumProperties(Enum):
	STRAIN_FACTOR = "LAT_MODDRYSTIFFCLAY_STRAIN_FACTOR"
	UNDRAINED_SHEAR_STRENGTH = "LAT_MODDRYSTIFFCLAY_UNDRAINED_SHEAR_STR"
	INITIAL_STIFFNESS = "LAT_MODDRYSTIFFCLAY_INITIAL_STIFFNESS"

class ModifiedStiffClayWithoutFreeWater:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = LateralModifiedStiffClayWithoutFreeWaterService_pb2_grpc.LateralModifiedStiffClayWithoutFreeWaterServiceStub(self._client.channel)
		self.Datum: Datum[LateralModifiedStiffClayWithoutFreeWaterDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.LATERAL
		)

	def _getModifiedStiffClayWithoutFreeWaterProperties(self) -> LateralModifiedStiffClayWithoutFreeWaterService_pb2.ModifiedStiffClayWithoutFreeWaterProperties:
		request = LateralModifiedStiffClayWithoutFreeWaterService_pb2.GetModifiedStiffClayWithoutFreeWaterRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetModifiedStiffClayWithoutFreeWaterProperties, request)
		return response.modified_stiff_clay_props

	def _setModifiedStiffClayWithoutFreeWaterProperties(self, modifiedStiffClayProps: LateralModifiedStiffClayWithoutFreeWaterService_pb2.ModifiedStiffClayWithoutFreeWaterProperties):
		request = LateralModifiedStiffClayWithoutFreeWaterService_pb2.SetModifiedStiffClayWithoutFreeWaterRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, modified_stiff_clay_props=modifiedStiffClayProps)
		self._client.callFunction(self._stub.SetModifiedStiffClayWithoutFreeWaterProperties, request)

	def getStrainFactor(self) -> float:
		properties = self._getModifiedStiffClayWithoutFreeWaterProperties()
		return properties.strain_factor_MSCwoutFW

	def setStrainFactor(self, strainFactor: float):
		properties = self._getModifiedStiffClayWithoutFreeWaterProperties()
		properties.strain_factor_MSCwoutFW = strainFactor
		self._setModifiedStiffClayWithoutFreeWaterProperties(properties)

	def getUndrainedShearStrength(self) -> float:
		properties = self._getModifiedStiffClayWithoutFreeWaterProperties()
		return properties.undrained_shear_strength_MSCwoutFW

	def setUndrainedShearStrength(self, shearStrength: float):
		properties = self._getModifiedStiffClayWithoutFreeWaterProperties()
		properties.undrained_shear_strength_MSCwoutFW = shearStrength
		self._setModifiedStiffClayWithoutFreeWaterProperties(properties)

	def getInitialStiffness(self) -> float:
		properties = self._getModifiedStiffClayWithoutFreeWaterProperties()
		return properties.initial_stiffness_MSCwoutFW

	def setInitialStiffness(self, initialStiffness: float):
		properties = self._getModifiedStiffClayWithoutFreeWaterProperties()
		properties.initial_stiffness_MSCwoutFW = initialStiffness
		self._setModifiedStiffClayWithoutFreeWaterProperties(properties)