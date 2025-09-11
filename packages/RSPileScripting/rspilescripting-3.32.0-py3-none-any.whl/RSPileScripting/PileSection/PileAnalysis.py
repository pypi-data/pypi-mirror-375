from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.PileAnalysisMaterialPropertiesService_pb2 as PileAnalysisMaterialPropertiesService_pb2
import RSPileScripting.generated_python_files.pile_section_services.PileAnalysisMaterialPropertiesService_pb2_grpc as PileAnalysisMaterialPropertiesService_pb2_grpc
from RSPileScripting.PileSection.Elastic import Elastic
from RSPileScripting.PileSection.Plastic import Plastic
from RSPileScripting.PileSection.ReinforcedConcrete import ReinforcedConcrete
from RSPileScripting.PileSection.PrestressedConcrete import PrestressedConcrete
from enum import Enum

class SectionType(Enum):
	ELASTIC = PileAnalysisMaterialPropertiesService_pb2.MaterialType.PILE_TYPE_ELASTIC
	PLASTIC = PileAnalysisMaterialPropertiesService_pb2.MaterialType.PILE_TYPE_PLASTIC
	REINFORCED_CONCRETE = PileAnalysisMaterialPropertiesService_pb2.MaterialType.PILE_TYPE_REINF_CONCRETE
	PRESTRESSED_CONCRETE = PileAnalysisMaterialPropertiesService_pb2.MaterialType.PILE_TYPE_PRESTR_CONCRETE

class PileAnalysis:
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = PileAnalysisMaterialPropertiesService_pb2_grpc.PileAnalysisMaterialPropertiesServiceStub(self._client.channel)
		self.Elastic = Elastic(self._model_id, self._pile_id, self._client)
		self.Plastic = Plastic(self._model_id, self._pile_id, self._client)
		self.ReinforcedConcrete = ReinforcedConcrete(self._model_id, self._pile_id, self._client)
		self.PrestressedConcrete = PrestressedConcrete(self._model_id, self._pile_id, self._client)

	def _getMaterialProperties(self) -> PileAnalysisMaterialPropertiesService_pb2.MaterialProperties:
		request = PileAnalysisMaterialPropertiesService_pb2.GetMaterialPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetMaterialProperties, request)
		return response.material_props

	def _setMaterialProperties(self, materialProps: PileAnalysisMaterialPropertiesService_pb2.MaterialProperties):
		request = PileAnalysisMaterialPropertiesService_pb2.SetMaterialPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			material_props=materialProps)
		self._client.callFunction(self._stub.SetMaterialProperties, request)

	def getSectionType(self) -> SectionType:
		properties = self._getMaterialProperties()
		return SectionType(properties.material_type)
	
	def setSectionType(self, sectionType: SectionType):
		properties = self._getMaterialProperties()
		properties.material_type = sectionType.value
		self._setMaterialProperties(properties)