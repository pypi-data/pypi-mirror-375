from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.AxialMosherSandService_pb2 as AxialMosherSandService_pb2
import RSPileScripting.generated_python_files.soil_services.AxialMosherSandService_pb2_grpc as AxialMosherSandService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class AxialMosherSandDatumProperties(Enum):
	PHI = "TZ_MOSHER_PHI"
	USER_DEFINED_E_S = "TZ_MOSHER_USER_DEF_ES"
	ULTIMATE_END_BEARING ="TZ_MOSHER_ULT_END_BEARING"
	ULTIMATE_SHEAR_RESISTANCE ="TZ_MOSHER_ULT_SHEAR_RESISTANCE"

class MosherSand:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = AxialMosherSandService_pb2_grpc.AxialMosherSandServiceStub(self._client.channel)
		self.Datum: Datum[AxialMosherSandDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.AXIAL
		)

	def _getMosherSandProperties(self) -> AxialMosherSandService_pb2.MosherSandProperties:
		request = AxialMosherSandService_pb2.GetMosherSandRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetMosherSandProperties, request)
		return response.mosher_sand_props

	def _setMosherSandProperties(self, mosherSandProps: AxialMosherSandService_pb2.MosherSandProperties):
		request = AxialMosherSandService_pb2.SetMosherSandRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, mosher_sand_props=mosherSandProps)
		self._client.callFunction(self._stub.SetMosherSandProperties, request)

	def getFrictionAngle(self) -> float:
		properties = self._getMosherSandProperties()
		return properties.mosher_phi

	def setFrictionAngle(self, frictionAngle: float):
		properties = self._getMosherSandProperties()
		properties.mosher_phi = frictionAngle
		self._setMosherSandProperties(properties)

	def getUseUserDefinedEs(self) -> bool:
		properties = self._getMosherSandProperties()
		return properties.mosher_use_user_def_es

	def setUseUserDefinedEs(self, useUserDefinedEs: bool):
		properties = self._getMosherSandProperties()
		properties.mosher_use_user_def_es = useUserDefinedEs
		self._setMosherSandProperties(properties)

	def getUserDefinedEs(self) -> float:
		properties = self._getMosherSandProperties()
		return properties.mosher_user_def_es

	def setUserDefinedEs(self, userDefinedEs: float):
		properties = self._getMosherSandProperties()
		properties.mosher_user_def_es = userDefinedEs
		self._setMosherSandProperties(properties)

	def getUltimateShearResistance(self) -> float:
		properties = self._getMosherSandProperties()
		return properties.mosher_ultimate_shear_resistance

	def setUltimateShearResistance(self, ultimateShearResistance: float):
		properties = self._getMosherSandProperties()
		properties.mosher_ultimate_shear_resistance = ultimateShearResistance
		self._setMosherSandProperties(properties)

	def getUltimateEndBearingResistance(self) -> float:
		properties = self._getMosherSandProperties()
		return properties.mosher_ultimate_end_bearing_resistance

	def setUltimateEndBearingResistance(self, ultimateEndBearingResistance: float):
		properties = self._getMosherSandProperties()
		properties.mosher_ultimate_end_bearing_resistance = ultimateEndBearingResistance
		self._setMosherSandProperties(properties)