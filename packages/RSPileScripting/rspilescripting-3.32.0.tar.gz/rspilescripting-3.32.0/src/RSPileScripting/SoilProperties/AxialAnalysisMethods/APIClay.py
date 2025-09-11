from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.AxialAPIClayService_pb2 as AxialAPIClayService_pb2
import RSPileScripting.generated_python_files.soil_services.AxialAPIClayService_pb2_grpc as AxialAPIClayService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class AxialAPIClayDatumProperties(Enum):
	UNDRAINED_SHEAR_STRENGTH = "CLAY_UNDRAINED_SHEAR_STRENGTH"
	REMOLDED_SHEAR_STRENGTH = "CLAY_REMOLDED_UNDRAINED_SHEAR_STRENGTH"
	MAXIMUM_UNIT_SKIN_FRICTION = "TZ_API_CLAY_MAX_UNIT_SKIN_FRICTION"
	MAXIMUM_UNIT_END_BEARING_RESISTANCE = "TZ_API_CLAY_MAX_UNIT_END_BEARING_RESIST"

class APIClay:
	"""
	Examples:
	:ref:`soil properties axial pile analysis`
	"""
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = AxialAPIClayService_pb2_grpc.AxialAPIClayServiceStub(self._client.channel)
		self.Datum: Datum[AxialAPIClayDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.AXIAL
		)
	
	def _getAPIClayProperties(self) -> AxialAPIClayService_pb2.APIClayProperties:
		request = AxialAPIClayService_pb2.GetAPIClayRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetAPIClayProperties, request)
		return response.api_clay_props
	
	def _setAPIClayProperties(self, apiClayProps: AxialAPIClayService_pb2.APIClayProperties):
		request = AxialAPIClayService_pb2.SetAPIClayRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, api_clay_props=apiClayProps)
		self._client.callFunction(self._stub.SetAPIClayProperties, request)
	
	def getMaximumUnitSkinFriction(self) -> float:
		properties = self._getAPIClayProperties()
		return properties.maximum_unit_side_friction_c
	
	def setMaximumUnitSkinFriction(self, maximumUnitSkinFriction: float):
		properties = self._getAPIClayProperties()
		properties.maximum_unit_side_friction_c = maximumUnitSkinFriction
		self._setAPIClayProperties(properties)
	
	def getMaximumUnitEndBearingResistance(self) -> float:
		properties = self._getAPIClayProperties()
		return properties.maximum_tip_resistance_c
	
	def setMaximumUnitEndBearingResistance(self, maximumUnitEndBearingResistance: float):
		properties = self._getAPIClayProperties()
		properties.maximum_tip_resistance_c = maximumUnitEndBearingResistance
		self._setAPIClayProperties(properties)
	
	def getUndrainedShearStrength(self) -> float:
		properties = self._getAPIClayProperties()
		return properties.undrained_shear_strength_c
	
	def setUndrainedShearStrength(self, undrainedShearStrength: float):
		properties = self._getAPIClayProperties()
		properties.undrained_shear_strength_c = undrainedShearStrength
		self._setAPIClayProperties(properties)
	
	def getRemoldedShearStrength(self) -> float:
		properties = self._getAPIClayProperties()
		return properties.remolded_undrained_shear_strength_c
	
	def setRemoldedShearStrength(self, remoldedShearStrength: float):
		properties = self._getAPIClayProperties()
		properties.remolded_undrained_shear_strength_c = remoldedShearStrength
		self._setAPIClayProperties(properties)