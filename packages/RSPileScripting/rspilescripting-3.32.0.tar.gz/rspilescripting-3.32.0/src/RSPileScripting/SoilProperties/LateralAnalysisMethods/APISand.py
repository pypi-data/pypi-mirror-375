from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.LateralAPISandService_pb2 as LateralAPISandService_pb2
import RSPileScripting.generated_python_files.soil_services.LateralAPISandService_pb2_grpc as LateralAPISandService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class LateralAPISandDatumProperties(Enum):
	FRICTION_ANGLE = "LAT_APISAND_PHI"
	INITIAL_MODULUS_OF_SUBGRADE_REACTION = "LAT_APISAND_MODULUS_SUBGRADE"

class APISand:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = LateralAPISandService_pb2_grpc.LateralAPISandServiceStub(self._client.channel)
		self.Datum: Datum[LateralAPISandDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.LATERAL
		)

	def _getAPISandProperties(self) -> LateralAPISandService_pb2.APISandProperties:
		
		request = LateralAPISandService_pb2.GetAPISandRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetAPISandProperties, request)
		return response.api_sand_props

	def _setAPISandProperties(self, apiSandProps: LateralAPISandService_pb2.APISandProperties):
		request = LateralAPISandService_pb2.SetAPISandRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, api_sand_props=apiSandProps)
		self._client.callFunction(self._stub.SetAPISandProperties, request)

	def getFrictionAngle(self) -> float:
		properties = self._getAPISandProperties()
		return properties.friction_angle_api_sand

	def setFrictionAngle(self, frictionAngle: float):
		properties = self._getAPISandProperties()
		properties.friction_angle_api_sand = frictionAngle
		self._setAPISandProperties(properties)

	def getInitialModulusOfSubgradeReaction(self) -> float:
		properties = self._getAPISandProperties()
		return properties.initial_modulus_of_subgrade_reaction

	def setInitialModulusOfSubgradeReaction(self, initialModulusOfSubgradeReaction: float):
		properties = self._getAPISandProperties()
		properties.initial_modulus_of_subgrade_reaction = initialModulusOfSubgradeReaction
		self._setAPISandProperties(properties)