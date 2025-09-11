from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.LateralDryStiffClayService_pb2 as LateralDryStiffClayService_pb2
import RSPileScripting.generated_python_files.soil_services.LateralDryStiffClayService_pb2_grpc as LateralDryStiffClayService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class LateralDryStiffClayDatumProperties(Enum):
	STRAIN_FACTOR = "LAT_DRY_CLAY_STRAIN_FACTOR"
	UNDRAINED_SHEAR_STRENGTH = "LAT_DRY_CLAY_SHEAR_STRENGTH"

class DryStiffClay:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = LateralDryStiffClayService_pb2_grpc.LateralDryStiffClayServiceStub(self._client.channel)
		self.Datum: Datum[LateralDryStiffClayDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.LATERAL
		)

	def _getDryStiffClayProperties(self) -> LateralDryStiffClayService_pb2.DryStiffClayProperties:
		request = LateralDryStiffClayService_pb2.GetDryStiffClayRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetDryStiffClayProperties, request)
		return response.dry_stiff_clay_props

	def _setDryStiffClayProperties(self, dryStiffClayProps: LateralDryStiffClayService_pb2.DryStiffClayProperties):
		request = LateralDryStiffClayService_pb2.SetDryStiffClayRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, dry_stiff_clay_props=dryStiffClayProps)
		self._client.callFunction(self._stub.SetDryStiffClayProperties, request)

	def getUndrainedShearStrength(self) -> float:
		properties = self._getDryStiffClayProperties()
		return properties.shear_strength_DSC

	def setUndrainedShearStrength(self, undrainedShearStrength: float):
		properties = self._getDryStiffClayProperties()
		properties.shear_strength_DSC = undrainedShearStrength
		self._setDryStiffClayProperties(properties)

	def getStrainFactor(self) -> float:
		properties = self._getDryStiffClayProperties()
		return properties.strain_factor_DSC

	def setStrainFactor(self, strainFactor: float):
		properties = self._getDryStiffClayProperties()
		properties.strain_factor_DSC = strainFactor
		self._setDryStiffClayProperties(properties)