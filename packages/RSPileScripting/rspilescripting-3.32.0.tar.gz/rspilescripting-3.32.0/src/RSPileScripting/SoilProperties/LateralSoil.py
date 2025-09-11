from enum import Enum
from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.LateralSoilService_pb2 as LateralSoilService_pb2
import RSPileScripting.generated_python_files.soil_services.LateralSoilService_pb2_grpc as LateralSoilService_pb2_grpc
from RSPileScripting.SoilProperties.LateralAnalysisMethods.Elastic import Elastic
from RSPileScripting.SoilProperties.LateralAnalysisMethods.SoftClay import SoftClay
from RSPileScripting.SoilProperties.LateralAnalysisMethods.SubmergedStiffClay import SubmergedStiffClay
from RSPileScripting.SoilProperties.LateralAnalysisMethods.WeakRock import WeakRock
from RSPileScripting.SoilProperties.LateralAnalysisMethods.UserDefined import UserDefined
from RSPileScripting.SoilProperties.LateralAnalysisMethods.DryStiffClay import DryStiffClay
from RSPileScripting.SoilProperties.LateralAnalysisMethods.Sand import Sand
from RSPileScripting.SoilProperties.LateralAnalysisMethods.APISand import APISand
from RSPileScripting.SoilProperties.LateralAnalysisMethods.Loess import Loess
from RSPileScripting.SoilProperties.LateralAnalysisMethods.PiedmontResidual import PiedmontResidual
from RSPileScripting.SoilProperties.LateralAnalysisMethods.StrongRock import StrongRock
from RSPileScripting.SoilProperties.LateralAnalysisMethods.ModifiedStiffClayWithoutFreeWater import ModifiedStiffClayWithoutFreeWater
from RSPileScripting.SoilProperties.LateralAnalysisMethods.Silt import Silt
from RSPileScripting.SoilProperties.LateralAnalysisMethods.SoftClayWithUserDefinedJ import SoftClayWithUserDefinedJ
from RSPileScripting.SoilProperties.LateralAnalysisMethods.HybridLiquefiedSand import HybridLiquefiedSand
from RSPileScripting.SoilProperties.LateralAnalysisMethods.MassiveRock import MassiveRock

class LateralType(Enum):
	ELASTIC = LateralSoilService_pb2.LateralSoilType.E_ELASTIC_SOIL_LAT
	SOFT_CLAY= LateralSoilService_pb2.LateralSoilType.E_SOFT_CLAY_SOIL_LAT
	SUBMERGED_STIFF_CLAY = LateralSoilService_pb2.LateralSoilType.E_SUBMERGED_STIFF_CLAY_LAT
	DRY_STIFF_CLAY = LateralSoilService_pb2.LateralSoilType.E_DRY_STIFF_CLAY_LAT
	SAND = LateralSoilService_pb2.LateralSoilType.E_SAND_LAT
	WEAK_ROCK = LateralSoilService_pb2.LateralSoilType.E_WEAK_ROCK_LAT
	USER_DEFINED = LateralSoilService_pb2.LateralSoilType.E_USER_DEFINED_LAT
	SMALL_STRAIN_SAND = LateralSoilService_pb2.LateralSoilType.E_SMALL_STRAIN_SAND
	API_SAND = LateralSoilService_pb2.LateralSoilType.E_API_SAND_LAT
	LOESS = LateralSoilService_pb2.LateralSoilType.E_LOESS_LAT
	LIQUEFIED_SAND = LateralSoilService_pb2.LateralSoilType.E_LIQUEFIED_SAND_LAT
	PIEDMONT_RESIDUAL_SOILS = LateralSoilService_pb2.LateralSoilType.E_PIEDMONT_RESIDUAL_SOILS_LAT
	STRONG_ROCK = LateralSoilService_pb2.LateralSoilType.E_STRONG_ROCK_LAT
	MODIFIED_STIFF_CLAY_WITHOUT_FREE_WATER = LateralSoilService_pb2.LateralSoilType.E_MODIFIED_STIFF_CLAY_WITHOUT_FREE_WATER_LAT
	SILT = LateralSoilService_pb2.LateralSoilType.E_SILT_LAT
	SOFT_CLAY_WITH_USER_DEFINED_J = LateralSoilService_pb2.LateralSoilType.E_SOFT_CLAY_WITH_USER_DEFINED_J_LAT
	HYBRID_LIQUEFIED_SAND = LateralSoilService_pb2.LateralSoilType.E_LAT_HYBRID_LIQUEFIED_SAND
	MASSIVE_ROCK = LateralSoilService_pb2.LateralSoilType.E_LAT_MASSIVE_ROCK

class LateralProperties:
	def __init__(self, model_id: str, soil_id: int, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = LateralSoilService_pb2_grpc.LateralSoilServiceStub(self._client.channel)
		self.Elastic = Elastic(self._model_id, self._soil_id, self._client)
		self.SoftClay = SoftClay(self._model_id, self._soil_id, self._client)
		self.SubmergedStiffClay = SubmergedStiffClay(self._model_id, self._soil_id, self._client)
		self.WeakRock = WeakRock(self._model_id, self._soil_id, self._client)
		self.UserDefined = UserDefined(self._model_id, self._soil_id, self._client)
		self.DryStiffClay = DryStiffClay(self._model_id, self._soil_id, self._client)
		self.Sand = Sand(self._model_id, self._soil_id, self._client)
		self.APISand = APISand(self._model_id, self._soil_id, self._client)
		self.Loess = Loess(self._model_id, self._soil_id, self._client)
		self.PiedmontResidual = PiedmontResidual(self._model_id, self._soil_id, self._client)
		self.StrongRock = StrongRock(self._model_id, self._soil_id, self._client)
		self.ModifiedStiffClayWithoutFreeWater = ModifiedStiffClayWithoutFreeWater(self._model_id, self._soil_id, self._client)
		self.Silt = Silt(self._model_id, self._soil_id, self._client)
		self.SoftClayWithUserDefinedJ = SoftClayWithUserDefinedJ(self._model_id, self._soil_id, self._client)
		self.HybridLiquefiedSand = HybridLiquefiedSand(self._model_id, self._soil_id, self._client)
		self.MassiveRock = MassiveRock(self._model_id, self._soil_id, self._client)

	def _getLateralProperties(self) -> LateralSoilService_pb2.LateralSoilProperties:
		request = LateralSoilService_pb2.GetLateralSoilRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetLateralSoilProperties, request)
		return response.lateral_soil_props

	def _setLateralProperties(self, lateralProps: LateralSoilService_pb2.LateralSoilProperties):
		request = LateralSoilService_pb2.SetLateralSoilRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, 
			lateral_soil_props=lateralProps)
		self._client.callFunction(self._stub.SetLateralSoilProperties, request)

	def getLateralType(self) -> LateralType:
		properties = self._getLateralProperties()
		return LateralType(properties.lateral_soil_type)

	def setLateralType(self, lateralType: LateralType):
		properties = self._getLateralProperties()
		properties.lateral_soil_type = lateralType.value
		self._setLateralProperties(properties)