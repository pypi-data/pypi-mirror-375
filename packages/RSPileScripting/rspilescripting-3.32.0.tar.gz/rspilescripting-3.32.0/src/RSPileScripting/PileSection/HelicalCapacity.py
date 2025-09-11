from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.HelicalCapacityService_pb2 as HelicalCapacityService_pb2
import RSPileScripting.generated_python_files.pile_section_services.HelicalCapacityService_pb2_grpc as HelicalCapacityService_pb2_grpc
from RSPileScripting.PileSection.CrossSectionTypes.Helical.CircularHollow import CircularHollow
from RSPileScripting.PileSection.CrossSectionTypes.Helical.CircularSolid import CircularSolid
from RSPileScripting.PileSection.CrossSectionTypes.Helical.SquareHollow import SquareHollow
from RSPileScripting.PileSection.CrossSectionTypes.Helical.SquareSolid import SquareSolid
from enum import Enum

class HelicalCrossSectionType(Enum):
	CIRCULAR_HOLLOW = "E_CIRCULAR_HOLLOW"
	CIRCULAR_SOLID = "E_CIRCULAR_SOLID"
	SQUARE_SOLID = "E_SQUARE_HOLLOW"
	SQUARE_HOLLOW = "E_SQUARE_SOLID"

class HelicalCapacity:
	"""
	Examples:
	:ref:`pile sections helical`
	"""
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = HelicalCapacityService_pb2_grpc.HelicalCapacityServiceStub(self._client.channel)
		self.CircularHollow = CircularHollow(self._model_id, self._pile_id, self._client)
		self.CircularSolid = CircularSolid(self._model_id, self._pile_id, self._client)
		self.SquareHollow = SquareHollow(self._model_id, self._pile_id, self._client)
		self.SquareSolid = SquareSolid(self._model_id, self._pile_id, self._client)

	def _getHelicalProperties(self) -> HelicalCapacityService_pb2.HelicalProperties:
		request = HelicalCapacityService_pb2.GetHelicalPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetHelicalProperties, request)
		return response.helical_props

	def _setHelicalProperties(self, helicalProps: HelicalCapacityService_pb2.HelicalProperties):
		request = HelicalCapacityService_pb2.SetHelicalPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			helical_props=helicalProps)
		self._client.callFunction(self._stub.SetHelicalProperties, request)

	def getCrossSectionType(self) -> HelicalCrossSectionType:
		properties = self._getHelicalProperties()
		return HelicalCrossSectionType(properties.cross_section_type)
	
	def setCrossSectionType(self, crossSectionType: HelicalCrossSectionType):
		properties = self._getHelicalProperties()
		properties.cross_section_type = crossSectionType.value
		self._setHelicalProperties(properties)