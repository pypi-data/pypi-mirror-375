from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.GenericSoilService_pb2 as GenericSoilService_pb2
import RSPileScripting.generated_python_files.soil_services.GenericSoilService_pb2_grpc as GenericSoilService_pb2_grpc
from RSPileScripting.SoilProperties.AxialSoil import AxialProperties
from RSPileScripting.SoilProperties.LateralSoil import LateralProperties
from RSPileScripting.SoilProperties.BoredSoil import BoredProperties
from RSPileScripting.SoilProperties.DrivenSoil import DrivenProperties
from RSPileScripting.SoilProperties.HelicalSoil import HelicalProperties
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class GeneralDatumProperties(Enum):
	UNIT_WEIGHT = "GENERAL_UNIT_WEIGHT"
	SATURATED_UNIT_WEIGHT = "GENERAL_UNIT_WEIGHT_SAT"

class HatchStyle(Enum):
	HORIZONTAL = GenericSoilService_pb2.HatchStyles.HORIZONTAL
	SOLID = GenericSoilService_pb2.HatchStyles.SOLID_FILL
	VERTICAL = GenericSoilService_pb2.HatchStyles.VERTICAL
	FORWARD_DIAGONAL = GenericSoilService_pb2.HatchStyles.FDIAGONAL
	BACKWARD_DIAGONAL = GenericSoilService_pb2.HatchStyles.BDIAGONAL
	GRID = GenericSoilService_pb2.HatchStyles.CROSS
	DIAGONAL_CROSS = GenericSoilService_pb2.HatchStyles.DIAGCROSS

class SoilProperty:
	"""
	Examples:
	:ref:`soil properties basic example`
	"""
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._soil_id = soil_id
		self._client = client
		self._model_id = model_id
		self._stub = GenericSoilService_pb2_grpc.GenericSoilServiceStub(self._client.channel)
		self.AxialProperties = AxialProperties(model_id, soil_id, client)
		self.LateralProperties = LateralProperties(model_id, soil_id, client)
		self.BoredProperties = BoredProperties(model_id, soil_id, client)
		self.DrivenProperties = DrivenProperties(model_id, soil_id, client)
		self.HelicalProperties = HelicalProperties(model_id, soil_id, client)
		self.Datum: Datum[GeneralDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.GENERAL
		)

	def _getGenericSoilProperties(self) -> GenericSoilService_pb2.GenericSoilProperties:
		request = GenericSoilService_pb2.GetGenericSoilRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetGenericSoilProperties, request)
		return response.generic_soil_props

	def _setGenericSoilProperties(self, soilProps: GenericSoilService_pb2.GenericSoilProperties):
		request = GenericSoilService_pb2.SetGenericSoilRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, 
			generic_soil_props=soilProps)
		self._client.callFunction(self._stub.SetGenericSoilProperties, request)

	def getName(self) -> str:
		properties = self._getGenericSoilProperties()
		return properties.soil_name

	def setName(self, name : str):
		properties = self._getGenericSoilProperties()
		properties.soil_name = name
		self._setGenericSoilProperties(properties)

	def getColor(self) -> int:
		properties = self._getGenericSoilProperties()
		return properties.soil_color

	def setColor(self, color : int):
		properties = self._getGenericSoilProperties()
		properties.soil_color = color
		self._setGenericSoilProperties(properties)

	def getHatch(self) -> HatchStyle:
		properties = self._getGenericSoilProperties()
		return HatchStyle(properties.hatch_style)

	def setHatch(self, hatch_style: HatchStyle):
		properties = self._getGenericSoilProperties()
		properties.hatch_style = hatch_style.value
		self._setGenericSoilProperties(properties)

	def getUnitWeight(self) -> float:
		properties = self._getGenericSoilProperties()
		return properties.soil_unit_weight

	def setUnitWeight(self, unit_weight : float):
		properties = self._getGenericSoilProperties()
		properties.soil_unit_weight = unit_weight
		self._setGenericSoilProperties(properties)

	def getUseSaturatedUnitWeight(self) -> bool:
		properties = self._getGenericSoilProperties()
		return properties.use_saturated_unit_weight

	def setUseSaturatedUnitWeight(self, use_saturated_unit_weight : bool):
		properties = self._getGenericSoilProperties()
		properties.use_saturated_unit_weight = use_saturated_unit_weight
		self._setGenericSoilProperties(properties)

	def getSaturatedUnitWeight(self) -> float:
		properties = self._getGenericSoilProperties()
		return properties.saturated_unit_weight

	def setSaturatedUnitWeight(self, saturated_unit_weight : float):
		properties = self._getGenericSoilProperties()
		properties.saturated_unit_weight = saturated_unit_weight
		self._setGenericSoilProperties(properties)

	def getUseDatumDependency(self) -> bool:
		properties = self._getGenericSoilProperties()
		return properties.m_consider_datum_dependency

	def setUseDatumDependency(self, datumDependency : bool):
		properties = self._getGenericSoilProperties()
		properties.m_consider_datum_dependency = datumDependency
		self._setGenericSoilProperties(properties)