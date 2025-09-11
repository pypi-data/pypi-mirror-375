from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.AxialDrilledSandService_pb2 as AxialDrilledSandService_pb2
import RSPileScripting.generated_python_files.soil_services.AxialDrilledSandService_pb2_grpc as AxialDrilledSandService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class AxialDrilledSandDatumProperties(Enum):
	ULTIMATE_SHEAR_RESISTANCE ="TZ_DRILLED_SAND_ULT_SHEAR_RESISTANCE"
	ULTIMATE_END_BEARING_RESISTANCE ="TZ_DRILLED_SAND_ULT_END_BEARING_RESISTANCE"

class DrilledSand:
	"""
	Examples:
	:ref:`soil properties axial pile analysis`
	"""
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = AxialDrilledSandService_pb2_grpc.AxialDrilledSandServiceStub(self._client.channel)
		self.Datum: Datum[AxialDrilledSandDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.AXIAL
		)
	
	def _getDrilledSandProperties(self) -> AxialDrilledSandService_pb2.DrilledSandProperties:
		request = AxialDrilledSandService_pb2.GetDrilledSandRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetDrilledSandProperties, request)
		return response.drilled_sand_props
	
	def _setDrilledSandProperties(self, drilledSandProps: AxialDrilledSandService_pb2.DrilledSandProperties):
		request = AxialDrilledSandService_pb2.SetDrilledSandRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, drilled_sand_props=drilledSandProps)
		self._client.callFunction(self._stub.SetDrilledSandProperties, request)
	
	def getUltimateShearResistance(self) -> float:
		properties = self._getDrilledSandProperties()
		return properties.drilled_sand_ultimate_shear_resistance
	
	def setUltimateShearResistance(self, ultimateShearResistance: float):
		properties = self._getDrilledSandProperties()
		properties.drilled_sand_ultimate_shear_resistance = ultimateShearResistance
		self._setDrilledSandProperties(properties)
	
	def getUltimateEndBearingResistance(self) -> float:
		properties = self._getDrilledSandProperties()
		return properties.drilled_sand_ultimate_end_bearing_resistance
	
	def setUltimateEndBearingResistance(self, ultimateEndBearingResistance: float):
		properties = self._getDrilledSandProperties()
		properties.drilled_sand_ultimate_end_bearing_resistance = ultimateEndBearingResistance
		self._setDrilledSandProperties(properties)