from enum import Enum
from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.PileAnalysisMaterialPrestressedConcreteService_pb2 as PileAnalysisMaterialPrestressedConcreteService_pb2
import RSPileScripting.generated_python_files.pile_section_services.PileAnalysisMaterialPrestressedConcreteService_pb2_grpc as PileAnalysisMaterialPrestressedConcreteService_pb2_grpc
import RSPileScripting.generated_python_files.pile_section_services.CommonPileAnalysisCrossSectionTypes_pb2 as CommonPileAnalysisCrossSectionTypes_pb2
from RSPileScripting.PileSection.CrossSectionOrganization.PrestressedConcreteCrossSections import PrestressedConcreteCrossSections as CrossSection

class PrestressedConcreteCrossSectionType(Enum):
	CIRCULAR = CommonPileAnalysisCrossSectionTypes_pb2.CrossSectionType.P2_CIRCULAR
	RECTANGULAR = CommonPileAnalysisCrossSectionTypes_pb2.CrossSectionType.P2_RECTANGULAR

class PrestressedConcrete:
	"""
	Examples:
	:ref:`prestressed concrete section`
	"""
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._pile_id = pile_id
		self._client = client
		self._model_id = model_id
		self._stub = PileAnalysisMaterialPrestressedConcreteService_pb2_grpc.PileAnalysisMaterialPrestressedConcreteServiceStub(self._client.channel)
		self.CrossSection = CrossSection(self._model_id, self._pile_id, self._client)

	def _getPrestressedConcreteProperties(self) -> PileAnalysisMaterialPrestressedConcreteService_pb2.PrestressedConcreteProperties:
		request = PileAnalysisMaterialPrestressedConcreteService_pb2.GetPrestressedConcretePropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetPrestressedConcreteProperties, request)
		return response.prestressed_concrete_props

	def _setPrestressedConcreteProperties(self, prestressedConcreteProps: PileAnalysisMaterialPrestressedConcreteService_pb2.PrestressedConcreteProperties):
		request = PileAnalysisMaterialPrestressedConcreteService_pb2.SetPrestressedConcretePropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			prestressed_concrete_props=prestressedConcreteProps)
		self._client.callFunction(self._stub.SetPrestressedConcreteProperties, request)

	def getCompressiveStrength(self) -> float:
		properties = self._getPrestressedConcreteProperties()
		return properties.compressive_strength
	
	def setCompressiveStrength(self, compressiveStrength: float):
		properties = self._getPrestressedConcreteProperties()
		properties.compressive_strength = compressiveStrength
		self._setPrestressedConcreteProperties(properties)

	def getCrossSectionType(self) -> PrestressedConcreteCrossSectionType:
		properties = self._getPrestressedConcreteProperties()
		return PrestressedConcreteCrossSectionType(properties.cross_section_type)
	
	def setCrossSectionType(self, crossSectionType: PrestressedConcreteCrossSectionType):
		properties = self._getPrestressedConcreteProperties()
		properties.cross_section_type = crossSectionType.value
		self._setPrestressedConcreteProperties(properties)