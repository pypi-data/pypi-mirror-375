from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.PileAnalysisMaterialReinforcedConcreteService_pb2 as PileAnalysisMaterialReinforcedConcreteService_pb2
import RSPileScripting.generated_python_files.pile_section_services.PileAnalysisMaterialReinforcedConcreteService_pb2_grpc as PileAnalysisMaterialReinforcedConcreteService_pb2_grpc
import RSPileScripting.generated_python_files.pile_section_services.CommonPileAnalysisCrossSectionTypes_pb2 as CommonPileAnalysisCrossSectionTypes_pb2
from RSPileScripting.PileSection.CrossSectionOrganization.ReinforcedConcreteCrossSections import ReinforcedConcreteCrossSections as CrossSection
from enum import Enum

class ReinforcedConcreteCrossSectionType(Enum):
	CIRCULAR = CommonPileAnalysisCrossSectionTypes_pb2.CrossSectionType.P2_CIRCULAR
	RECTANGULAR = CommonPileAnalysisCrossSectionTypes_pb2.CrossSectionType.P2_RECTANGULAR

class ReinforcedConcrete:
	"""
	Examples:
	:ref:`pile sections pile analysis`
	"""
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._pile_id = pile_id
		self._client = client
		self._model_id = model_id
		self._stub = PileAnalysisMaterialReinforcedConcreteService_pb2_grpc.PileAnalysisMaterialReinforcedConcreteServiceStub(self._client.channel)
		self.CrossSection = CrossSection(self._model_id, self._pile_id, self._client)
		
	def _getReinforcedConcreteProperties(self) -> PileAnalysisMaterialReinforcedConcreteService_pb2.ReinforcedConcreteProperties:
		request = PileAnalysisMaterialReinforcedConcreteService_pb2.GetReinforcedConcretePropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetReinforcedConcreteProperties, request)
		return response.reinforced_concrete_props

	def _setReinforcedConcreteProperties(self, reinforcedConcreteProps: PileAnalysisMaterialReinforcedConcreteService_pb2.ReinforcedConcreteProperties):
		request = PileAnalysisMaterialReinforcedConcreteService_pb2.SetReinforcedConcretePropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			reinforced_concrete_props=reinforcedConcreteProps)
		self._client.callFunction(self._stub.SetReinforcedConcreteProperties, request)

	def getCrossSectionType(self) -> ReinforcedConcreteCrossSectionType:
		properties = self._getReinforcedConcreteProperties()
		return ReinforcedConcreteCrossSectionType(properties.cross_section_type)

	def setCrossSectionType(self, crossSectionType: ReinforcedConcreteCrossSectionType):
		properties = self._getReinforcedConcreteProperties()
		properties.cross_section_type = crossSectionType.value
		self._setReinforcedConcreteProperties(properties)

	def getCompressiveStrength(self) -> float:
		properties = self._getReinforcedConcreteProperties()
		return properties.compressive_strength
	
	def setCompressiveStrength(self, compressiveStrength: float):
		properties = self._getReinforcedConcreteProperties()
		properties.compressive_strength = compressiveStrength
		self._setReinforcedConcreteProperties(properties)