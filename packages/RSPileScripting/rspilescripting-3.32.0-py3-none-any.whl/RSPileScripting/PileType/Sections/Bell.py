from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_type_services.PileTypeSectionsBellService_pb2 as PileTypeSectionsBellService_pb2
import RSPileScripting.generated_python_files.pile_type_services.PileTypeSectionsBellService_pb2_grpc as PileTypeSectionsBellService_pb2_grpc
from enum import Enum

class BaseDiamaterDefinitionType(Enum):
	FACTOR = PileTypeSectionsBellService_pb2.BellBaseDiameterDefinedBy.E_FACTOR_OF_TOP_DIAMETER
	VALUE = PileTypeSectionsBellService_pb2.BellBaseDiameterDefinedBy.E_VALUE

class Bell:
	def __init__(self, model_id: str, pile_type_id: str, client: Client):
		self.pile_type_id = pile_type_id
		self._client = client
		self._model_id = model_id
		self._stub = PileTypeSectionsBellService_pb2_grpc.PileTypeSectionsBellServiceStub(self._client.channel)

	def _getPileTypeBellProperties(self) -> PileTypeSectionsBellService_pb2.BellProperties:
		request = PileTypeSectionsBellService_pb2.GetBellPropertiesRequest(
			session_id=self._client.sessionID, pile_type_id=self.pile_type_id)
		response = self._client.callFunction(self._stub.GetBellProperties, request)
		return response.bell_props

	def _setPileTypeBellProperties(self, bellProps: PileTypeSectionsBellService_pb2.BellProperties):
		request = PileTypeSectionsBellService_pb2.SetBellPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_type_id=self.pile_type_id, 
			bell_props=bellProps)
		self._client.callFunction(self._stub.SetBellProperties, request)

	def getLengthAboveBell(self) -> float:
		properties = self._getPileTypeBellProperties()
		return properties.length_above_bell
	
	def setLengthAboveBell(self, length: float):
		properties = self._getPileTypeBellProperties()
		properties.length_above_bell = length
		self._setPileTypeBellProperties(properties)

	def getAngle(self) -> float:
		properties = self._getPileTypeBellProperties()
		return properties.bell_angle
	
	def setAngle(self, angle: float):
		properties = self._getPileTypeBellProperties()
		properties.bell_angle = angle
		self._setPileTypeBellProperties(properties)

	def getBaseThickness(self) -> float:
		properties = self._getPileTypeBellProperties()
		return properties.bell_base_thickness
	
	def setBaseThickness(self, thickness: float):
		properties = self._getPileTypeBellProperties()
		properties.bell_base_thickness = thickness
		self._setPileTypeBellProperties(properties)

	def getBaseDiameterDefinitionType(self) -> BaseDiamaterDefinitionType:
		properties = self._getPileTypeBellProperties()
		return BaseDiamaterDefinitionType(properties.bell_base_diameter_defined_by)
	
	def setBaseDiameterDefinitionType(self, baseDiamaterDefinitionType: BaseDiamaterDefinitionType):
		properties = self._getPileTypeBellProperties()
		properties.bell_base_diameter_defined_by = baseDiamaterDefinitionType.value
		self._setPileTypeBellProperties(properties)
		
	def getBaseDiameter(self) -> float:
		properties = self._getPileTypeBellProperties()
		return properties.base_diameter
	
	def setBaseDiameter(self, baseDiameter: float):
		properties = self._getPileTypeBellProperties()
		properties.base_diameter = baseDiameter
		self._setPileTypeBellProperties(properties)
		
	def getBaseFactor(self) -> float:
		properties = self._getPileTypeBellProperties()
		return properties.factor
	
	def setBaseFactor(self, baseDiameter: float):
		properties = self._getPileTypeBellProperties()
		properties.factor = baseDiameter
		self._setPileTypeBellProperties(properties)