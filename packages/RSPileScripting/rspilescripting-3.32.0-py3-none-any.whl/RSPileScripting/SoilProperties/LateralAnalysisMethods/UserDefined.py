from RSPileScripting._client import Client
from typing import List, Tuple
import RSPileScripting.generated_python_files.soil_services.LateralUserDefinedService_pb2 as LateralUserDefinedService_pb2
import RSPileScripting.generated_python_files.soil_services.LateralUserDefinedService_pb2_grpc as LateralUserDefinedService_pb2_grpc

class UserDefined:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = LateralUserDefinedService_pb2_grpc.LateralUserDefinedServiceStub(self._client.channel)

	def _getUserDefinedProperties(self) -> LateralUserDefinedService_pb2.UserDefinedProperties:
		request = LateralUserDefinedService_pb2.GetUserDefinedRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetUserDefinedProperties, request)
		return response.user_defined_props

	def _setUserDefinedProperties(self, userDefinedProps: LateralUserDefinedService_pb2.UserDefinedProperties):
		request = LateralUserDefinedService_pb2.SetUserDefinedRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, user_defined_props=userDefinedProps)
		self._client.callFunction(self._stub.SetUserDefinedProperties, request)

	def getVaryPYCurveByDepth(self) -> bool:
		properties = self._getUserDefinedProperties()
		return properties.uses_py_curve_bottom

	def setVaryPYCurveByDepth(self, varyPYCurveByDepth: bool):
		properties = self._getUserDefinedProperties()
		properties.uses_py_curve_bottom = varyPYCurveByDepth
		self._setUserDefinedProperties(properties)

	def getPYCurve(self) -> List[Tuple[float, float]]:
		properties = self._getUserDefinedProperties()
		return [(point.x_value, point.y_value) for point in properties.py_curve]

	def setPYCurve(self, pyCurve: List[Tuple[float, float]]):
		properties = self._getUserDefinedProperties()
		properties.ClearField("py_curve")
		for x, y in pyCurve:
			xyPair = properties.py_curve.add()
			xyPair.x_value = x
			xyPair.y_value = y
		self._setUserDefinedProperties(properties)
	
	def getPYCurveBottom(self) -> List[Tuple[float, float]]:
		properties = self._getUserDefinedProperties()
		return [(point.x_value, point.y_value) for point in properties.py_curve_bottom]

	def setPYCurveBottom(self, pyCurveBottom: List[Tuple[float, float]]):
		properties = self._getUserDefinedProperties()
		properties.ClearField("py_curve_bottom")
		for x, y in pyCurveBottom:
			xyPair = properties.py_curve_bottom.add()
			xyPair.x_value = x
			xyPair.y_value = y
		self._setUserDefinedProperties(properties)