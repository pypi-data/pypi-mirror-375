from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.AxialCoyleAndReeseClayService_pb2 as AxialCoyleAndReeseClayService_pb2
import RSPileScripting.generated_python_files.soil_services.AxialCoyleAndReeseClayService_pb2_grpc as AxialCoyleAndReeseClayService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class AxialCoyleAndReeseClayDatumProperties(Enum):
	SHEAR_STRENGTH = "TZ_COYLE_REESE_SHEAR_STRENGTH"
	SHEAR_RESISTANCE = "TZ_COYLE_REESE_SHEAR_RESISTANCE"
	E_50 = "TZ_COYLE_REESE_E50"
	ULTIMATE_END_BEARING_RESISTANCE = "TZ_COYLE_REESE_ULT_END_BEARING_RESIST"

class CoyleAndReeseClay:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = AxialCoyleAndReeseClayService_pb2_grpc.AxialCoyleAndReeseClayServiceStub(self._client.channel)
		self.Datum: Datum[AxialCoyleAndReeseClayDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.AXIAL
		)

	def _getCoyleAndReeseClayProperties(self) -> AxialCoyleAndReeseClayService_pb2.CoyleAndReeseClayProperties:
		request = AxialCoyleAndReeseClayService_pb2.GetCoyleAndReeseClayRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetCoyleAndReeseClayProperties, request)
		return response.coyle_and_reese_props

	def _setCoyleAndReeseClayProperties(self, coyleAndReeseProps: AxialCoyleAndReeseClayService_pb2.CoyleAndReeseClayProperties):
		request = AxialCoyleAndReeseClayService_pb2.SetCoyleAndReeseClayRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, coyle_and_reese_props=coyleAndReeseProps)
		self._client.callFunction(self._stub.SetCoyleAndReeseClayProperties, request)

	def getShearStrength(self) -> float:
		properties = self._getCoyleAndReeseClayProperties()
		return properties.coyle_reese_shear_strength

	def setShearStrength(self, shearStrength: float):
		properties = self._getCoyleAndReeseClayProperties()
		properties.coyle_reese_shear_strength = shearStrength
		self._setCoyleAndReeseClayProperties(properties)

	def getUltimateShearResistance(self) -> float:
		properties = self._getCoyleAndReeseClayProperties()
		return properties.coyle_reese_ultimate_shear_resistance

	def setUltimateShearResistance(self, ultimateShearResistance: float):
		properties = self._getCoyleAndReeseClayProperties()
		properties.coyle_reese_ultimate_shear_resistance = ultimateShearResistance
		self._setCoyleAndReeseClayProperties(properties)

	def getE50(self) -> float:
		properties = self._getCoyleAndReeseClayProperties()
		return properties.coyle_reese_e50

	def setE50(self, e50: float):
		properties = self._getCoyleAndReeseClayProperties()
		properties.coyle_reese_e50 = e50
		self._setCoyleAndReeseClayProperties(properties)

	def getUltimateEndBearingResistance(self) -> float:
		properties = self._getCoyleAndReeseClayProperties()
		return properties.coyle_reese_ultimate_end_bearing_resistance

	def setUltimateEndBearingResistance(self, ultimateEndBearingResistance: float):
		properties = self._getCoyleAndReeseClayProperties()
		properties.coyle_reese_ultimate_end_bearing_resistance = ultimateEndBearingResistance
		self._setCoyleAndReeseClayProperties(properties)