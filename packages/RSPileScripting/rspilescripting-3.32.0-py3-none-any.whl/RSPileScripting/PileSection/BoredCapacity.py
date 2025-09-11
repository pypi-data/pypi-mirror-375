from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.BoredCapacityService_pb2 as BoredCapacityService_pb2
import RSPileScripting.generated_python_files.pile_section_services.BoredCapacityService_pb2_grpc as BoredCapacityService_pb2_grpc
import RSPileScripting.PileSection.CrossSectionTypes.Bored.Circular as Circular
import RSPileScripting.PileSection.CrossSectionTypes.Bored.Square as Square
import RSPileScripting.PileSection.CrossSectionTypes.Bored.Rectangular as Rectangular

from enum import Enum

class BoredCrossSectionType(Enum):
	CIRCULAR = BoredCapacityService_pb2.CrossSectionType.E_CIRCULAR
	SQUARE = BoredCapacityService_pb2.CrossSectionType.E_SQUARE
	RECTANGULAR = BoredCapacityService_pb2.CrossSectionType.E_RECTANGLE

class BoredCapacity:
	"""
	Examples:
	:ref:`pile sections bored`
	"""
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = BoredCapacityService_pb2_grpc.BoredCapacityServiceStub(self._client.channel)
		self.Circular = Circular.Circular(self._model_id, self._pile_id, self._client)
		self.Square = Square.Square(self._model_id, self._pile_id, self._client)
		self.Rectangular = Rectangular.Rectangular(self._model_id, self._pile_id, self._client)

	def _getBoredProperties(self) -> BoredCapacityService_pb2.BoredProperties:
		request = BoredCapacityService_pb2.GetBoredPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetBoredProperties, request)
		return response.bored_props

	def _setBoredProperties(self, boredProps: BoredCapacityService_pb2.BoredProperties):
		request = BoredCapacityService_pb2.SetBoredPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			bored_props=boredProps)
		self._client.callFunction(self._stub.SetBoredProperties, request)

	def getCrossSectionType(self) -> BoredCrossSectionType:
		properties = self._getBoredProperties()
		return BoredCrossSectionType(properties.cross_section_type)
	
	def setCrossSectionType(self, crossSectionType: BoredCrossSectionType):
		properties = self._getBoredProperties()
		properties.cross_section_type = crossSectionType.value
		self._setBoredProperties(properties)
		
	def getConcreteCylinderStrength(self) -> float:
		properties = self._getBoredProperties()
		return properties.concrete_cylinder_strength
	
	def setConcreteCylinderStrength(self, concreteCylinderStrength: float):
		properties = self._getBoredProperties()
		properties.concrete_cylinder_strength = concreteCylinderStrength
		self._setBoredProperties(properties)