from RSPileScripting._client import Client
from typing import List, Tuple
import RSPileScripting.generated_python_files.soil_services.AxialUserDefinedService_pb2 as AxialUserDefinedService_pb2
import RSPileScripting.generated_python_files.soil_services.AxialUserDefinedService_pb2_grpc as AxialUserDefinedService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class AxialUserDefinedDatumProperties(Enum):
	ULTIMATE_UNIT_SKIN_FRICTION = "USER_ULT_UNIT_SIDE_FRICTION"
	ULTIMATE_END_BEARING_RESISTANCE = "USER_ULT_TIP_RESIST"

class UserDefined:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = AxialUserDefinedService_pb2_grpc.AxialUserDefinedServiceStub(self._client.channel)
		self.Datum: Datum[AxialUserDefinedDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.AXIAL
		)


	def _getUserDefinedProperties(self) -> AxialUserDefinedService_pb2.UserDefinedProperties:
		request = AxialUserDefinedService_pb2.GetUserDefinedRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetUserDefinedProperties, request)
		return response.user_defined_props

	def _setUserDefinedProperties(self, userDefinedProps: AxialUserDefinedService_pb2.UserDefinedProperties):
		request = AxialUserDefinedService_pb2.SetUserDefinedRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, user_defined_props=userDefinedProps)
		self._client.callFunction(self._stub.SetUserDefinedProperties, request)

	def getUltimateUnitSkinFriction(self) -> float:
		properties = self._getUserDefinedProperties()
		return properties.ultimate_unit_side_friction_top_u

	def setUltimateUnitSkinFriction(self, ultimateUnitSkinFriction: float):
		properties = self._getUserDefinedProperties()
		properties.ultimate_unit_side_friction_top_u = ultimateUnitSkinFriction
		self._setUserDefinedProperties(properties)

	def getUltimateUnitEndBearingResistance(self) -> float:
		properties = self._getUserDefinedProperties()
		return properties.ultimate_tip_resistance_top_u

	def setUltimateUnitEndBearingResistance(self, ultimateUnitEndBearingResistance: float):
		properties = self._getUserDefinedProperties()
		properties.ultimate_tip_resistance_top_u = ultimateUnitEndBearingResistance
		self._setUserDefinedProperties(properties)

	def getTZCurve(self) -> List[Tuple[float, float]]:
		properties = self._getUserDefinedProperties()
		return [(point.x_value, point.y_value) for point in properties.tz_curve]

	def setTZCurve(self, tzCurve: List[Tuple[float, float]]):
		"""
		Accepts an array of tuples, where each tuple contains (Displacement, Stress to Max Ratio).
		"""
		properties = self._getUserDefinedProperties()
		properties.ClearField("tz_curve")
		for x, y in tzCurve:
			xyPair = properties.tz_curve.add()
			xyPair.x_value = x
			xyPair.y_value = y
		self._setUserDefinedProperties(properties)
	
	def getQZCurve(self) -> List[Tuple[float, float]]:
		properties = self._getUserDefinedProperties()
		return [(point.x_value, point.y_value) for point in properties.qz_curve]

	def setQZCurve(self, qzCurve: List[Tuple[float, float]]):
		"""
		Accepts an array of tuples, where each tuple contains (Displacement, End Bearing to Max End Bearing Ratio).
		"""
		properties = self._getUserDefinedProperties()
		properties.ClearField("qz_curve")
		for x, y in qzCurve:
			xyPair = properties.qz_curve.add()
			xyPair.x_value = x
			xyPair.y_value = y
		self._setUserDefinedProperties(properties)