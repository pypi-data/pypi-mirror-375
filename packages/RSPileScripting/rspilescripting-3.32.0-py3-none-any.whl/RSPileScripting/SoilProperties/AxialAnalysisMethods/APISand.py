from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.AxialAPISandService_pb2 as AxialAPISandService_pb2
import RSPileScripting.generated_python_files.soil_services.AxialAPISandService_pb2_grpc as AxialAPISandService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class AxialAPISandDatumProperties(Enum):
	COEFFICIENT_OF_LATERAL_EARTH_PRESSURE = "SAND_LATERAL_EARTH_PRESSURE_COEFFICIENT"
	BEARING_CAPACITY_FACTOR = "SAND_BEARING_CAPACITY_FACTOR"
	FRICTION_ANGLE = "SAND_FRICTION_ANGLE"
	MAXIMUM_UNIT_SKIN_FRICTION = "TZ_API_SAND_MAX_UNIT_SKIN_FRICTION"
	MAXIUMUM_UNIT_END_BEARING_CAPACITY = "TZ_API_SAND_MAX_UNIT_END_BEARING_RESIST"

class APISand:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = AxialAPISandService_pb2_grpc.AxialAPISandServiceStub(self._client.channel)
		self.Datum: Datum[AxialAPISandDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.AXIAL
		)

	def _getAPISandProperties(self) -> AxialAPISandService_pb2.APISandProperties:
		request = AxialAPISandService_pb2.GetAPISandRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetAPISandProperties, request)
		return response.api_sand_props

	def _setAPISandProperties(self, apiSandProps: AxialAPISandService_pb2.APISandProperties):
		request = AxialAPISandService_pb2.SetAPISandRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, api_sand_props=apiSandProps)
		self._client.callFunction(self._stub.SetAPISandProperties, request)

	def getCoefficientOfLateralEarthPressure(self) -> float:
		properties = self._getAPISandProperties()
		return properties.lateral_earth_pressure_coefficient_s

	def setCoefficientOfLateralEarthPressure(self, coefficientOfLateralEarthPressure: float):
		properties = self._getAPISandProperties()
		properties.lateral_earth_pressure_coefficient_s = coefficientOfLateralEarthPressure
		self._setAPISandProperties(properties)

	def getBearingCapacityFactor(self) -> float:
		properties = self._getAPISandProperties()
		return properties.bearing_capacity_factor_s

	def setBearingCapacityFactor(self, bearingCapacityFactor: float):
		properties = self._getAPISandProperties()
		properties.bearing_capacity_factor_s = bearingCapacityFactor
		self._setAPISandProperties(properties)

	def getFrictionAngle(self) -> float:
		properties = self._getAPISandProperties()
		return properties.friction_angle_s

	def setFrictionAngle(self, frictionAngle: float):
		properties = self._getAPISandProperties()
		properties.friction_angle_s = frictionAngle
		self._setAPISandProperties(properties)

	def getMaximumUnitSkinFriction(self) -> float:
		properties = self._getAPISandProperties()
		return properties.maximum_unit_side_friction_s

	def setMaximumUnitSkinFriction(self, maximumUnitSkinFriction: float):
		properties = self._getAPISandProperties()
		properties.maximum_unit_side_friction_s = maximumUnitSkinFriction
		self._setAPISandProperties(properties)

	def getMaximumUnitEndBearingResistance(self) -> float:
		properties = self._getAPISandProperties()
		return properties.maximum_tip_resistance_s

	def setMaximumUnitEndBearingResistance(self, maximumUnitEndBearingResistance: float):
		properties = self._getAPISandProperties()
		properties.maximum_tip_resistance_s = maximumUnitEndBearingResistance
		self._setAPISandProperties(properties)