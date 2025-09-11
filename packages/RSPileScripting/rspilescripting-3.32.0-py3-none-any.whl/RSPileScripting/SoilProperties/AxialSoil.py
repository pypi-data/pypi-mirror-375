from RSPileScripting._client import Client
from enum import Enum
import RSPileScripting.generated_python_files.soil_services.AxialSoilService_pb2 as AxialSoilService_pb2
import RSPileScripting.generated_python_files.soil_services.AxialSoilService_pb2_grpc as AxialSoilService_pb2_grpc
from RSPileScripting.SoilProperties.AxialAnalysisMethods.APISand import APISand
from RSPileScripting.SoilProperties.AxialAnalysisMethods.APIClay import APIClay
from RSPileScripting.SoilProperties.AxialAnalysisMethods.DrilledSand import DrilledSand
from RSPileScripting.SoilProperties.AxialAnalysisMethods.CoyleAndReeseClay import CoyleAndReeseClay
from RSPileScripting.SoilProperties.AxialAnalysisMethods.DrilledClay import DrilledClay
from RSPileScripting.SoilProperties.AxialAnalysisMethods.Elastic import Elastic
from RSPileScripting.SoilProperties.AxialAnalysisMethods.MosherSand import MosherSand
from RSPileScripting.SoilProperties.AxialAnalysisMethods.UserDefined import UserDefined

class AxialType(Enum):
	API_SAND = AxialSoilService_pb2.AxialSoilType.E_SAND_TZ_PILE
	API_CLAY = AxialSoilService_pb2.AxialSoilType.E_CLAY_TZ_PILE
	USER_DEFINED = AxialSoilService_pb2.AxialSoilType.E_USER_DEFINED_TZ_PILE
	ELASTIC = AxialSoilService_pb2.AxialSoilType.E_TZ_ELASTIC
	COYLE_AND_REESE_CLAY = AxialSoilService_pb2.AxialSoilType.E_COYLE_REESE_CLAY_TZ_PILE  
	MOSHER_SAND = AxialSoilService_pb2.AxialSoilType.E_MOSHER_SAND_TZ_PILE
	DRILLED_CLAY = AxialSoilService_pb2.AxialSoilType.E_DRILLED_CLAY_TZ_PILE
	DRILLED_SAND = AxialSoilService_pb2.AxialSoilType.E_DRILLED_SAND_TZ_PILE

class AxialProperties:
	def __init__(self, model_id: str, soil_id: int, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = AxialSoilService_pb2_grpc.AxialSoilServiceStub(self._client.channel)
		self.APISand = APISand(self._model_id, self._soil_id, self._client)
		self.APIClay = APIClay(self._model_id, self._soil_id, self._client)
		self.DrilledSand = DrilledSand(self._model_id, self._soil_id, self._client)
		self.CoyleAndReeseClay = CoyleAndReeseClay(self._model_id, self._soil_id, self._client)
		self.DrilledClay = DrilledClay(self._model_id, self._soil_id, self._client)
		self.Elastic = Elastic(self._model_id, self._soil_id, self._client)
		self.MosherSand = MosherSand(self._model_id, self._soil_id, self._client)
		self.UserDefined = UserDefined(self._model_id, self._soil_id, self._client)

	def _getAxialSoilProperties(self) -> AxialSoilService_pb2.AxialSoilProperties:
		request = AxialSoilService_pb2.GetAxialSoilRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetAxialSoilProperties, request)
		return response.axial_soil_props

	def _setAxialSoilProperties(self, axialSoilProps: AxialSoilService_pb2.AxialSoilProperties):
		request = AxialSoilService_pb2.SetAxialSoilRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, 
			axial_soil_props=axialSoilProps)
		self._client.callFunction(self._stub.SetAxialSoilProperties, request)

	def getAxialType(self) -> AxialType:
		properties = self._getAxialSoilProperties()
		return AxialType(properties.axial_soil_type)
	
	def setAxialType(self, axialType: AxialType):
		properties = self._getAxialSoilProperties()
		properties.axial_soil_type = axialType.value
		self._setAxialSoilProperties(properties)