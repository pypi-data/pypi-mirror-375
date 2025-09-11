from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.AxialDrilledClayService_pb2 as AxialDrilledClayService_pb2
import RSPileScripting.generated_python_files.soil_services.AxialDrilledClayService_pb2_grpc as AxialDrilledClayService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class AxialDrilledClayDatumProperties(Enum):
	ULTIMATE_SHEAR_RESISTANCE ="TZ_DRILLED_CLAY_ULT_SHEAR_RESISTANCE"
	ULTIMATE_END_BEARING_RESISTANCE ="TZ_DRILLED_CLAY_ULT_END_BEARING_RESISTANCE"

class DrilledClay:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = AxialDrilledClayService_pb2_grpc.AxialDrilledClayServiceStub(self._client.channel)
		self.Datum: Datum[AxialDrilledClayDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.AXIAL
		)

	def _getDrilledClayProperties(self) -> AxialDrilledClayService_pb2.DrilledClayProperties:
		request = AxialDrilledClayService_pb2.GetDrilledClayRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetDrilledClayProperties, request)
		return response.drilled_clay_props

	def _setDrilledClayProperties(self, drilledClayProps: AxialDrilledClayService_pb2.DrilledClayProperties):
		request = AxialDrilledClayService_pb2.SetDrilledClayRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, drilled_clay_props=drilledClayProps)
		self._client.callFunction(self._stub.SetDrilledClayProperties, request)

	def getUltimateShearResistance(self) -> float:
		properties = self._getDrilledClayProperties()
		return properties.drilled_clay_ultimate_shear_resistance

	def setUltimateShearResistance(self, ultimateShearResistance: float):
		properties = self._getDrilledClayProperties()
		properties.drilled_clay_ultimate_shear_resistance = ultimateShearResistance
		self._setDrilledClayProperties(properties)

	def getUltimateEndBearingResistance(self) -> float:
		properties = self._getDrilledClayProperties()
		return properties.drilled_clay_ultimate_end_bearing_resistance

	def setUltimateEndBearingResistance(self, ultimateEndBearingResistance: float):
		properties = self._getDrilledClayProperties()
		properties.drilled_clay_ultimate_end_bearing_resistance = ultimateEndBearingResistance
		self._setDrilledClayProperties(properties)