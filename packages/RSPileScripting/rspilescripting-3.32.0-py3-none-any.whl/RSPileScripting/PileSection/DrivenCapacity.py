from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.DrivenCapacityService_pb2 as PileAnalysisDrivenService_pb2
import RSPileScripting.generated_python_files.pile_section_services.DrivenCapacityService_pb2_grpc as DrivenCapacityService_pb2_grpc
import RSPileScripting.PileSection.CrossSectionTypes.Driven.ClosedEndPipe as ClosedEndPipe
import RSPileScripting.PileSection.CrossSectionTypes.Driven.OpenEndPipe as OpenEndPipe
import RSPileScripting.PileSection.CrossSectionTypes.Driven.Timber as Timber
import RSPileScripting.PileSection.CrossSectionTypes.Driven.Concrete as Concrete
import RSPileScripting.PileSection.CrossSectionTypes.Driven.RolledSection as RolledSection
import RSPileScripting.PileSection.CrossSectionTypes.Driven.Raymond as Raymond

from enum import Enum

class DrivenCrossSectionType(Enum):
	PIPE_PILE_CLOSED_END = PileAnalysisDrivenService_pb2.CrossSectionType.E_PIPE_PILE_CLOSED_END
	PIPE_PILE_OPEN_END = PileAnalysisDrivenService_pb2.CrossSectionType.E_PIPE_PILE_OPEN_END
	TIMBER_PILE = PileAnalysisDrivenService_pb2.CrossSectionType.E_TIMBER_PILE
	CONCRETE_PILE = PileAnalysisDrivenService_pb2.CrossSectionType.E_CONCRETE_PILE
	H_PILE = PileAnalysisDrivenService_pb2.CrossSectionType.E_H_PILE
	RAYMOND_PILE = PileAnalysisDrivenService_pb2.CrossSectionType.E_RAYMOND_PILE

class DrivenCapacity:
	"""
	Examples:
	:ref:`pile sections driven`
	"""
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = DrivenCapacityService_pb2_grpc.DrivenCapacityServiceStub(self._client.channel)
		self.ClosedEndPipe = ClosedEndPipe.ClosedEndPipe(self._model_id, self._pile_id, self._client)
		self.OpenEndPipe = OpenEndPipe.OpenEndPipe(self._model_id, self._pile_id, self._client)
		self.Timber = Timber.Timber(self._model_id, self._pile_id, self._client)
		self.Concrete = Concrete.Concrete(self._model_id, self._pile_id, self._client)
		self.RolledSection = RolledSection.RolledSection(self._model_id, self._pile_id, self._client)
		self.Raymond = Raymond.Raymond(self._model_id, self._pile_id, self._client)

	def _getDrivenProperties(self) -> PileAnalysisDrivenService_pb2.DrivenProperties:
		request = PileAnalysisDrivenService_pb2.GetDrivenPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetDrivenProperties, request)
		return response.driven_props

	def _setDrivenProperties(self, drivenProps: PileAnalysisDrivenService_pb2.DrivenProperties):
		request = PileAnalysisDrivenService_pb2.SetDrivenPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			driven_props=drivenProps)
		self._client.callFunction(self._stub.SetDrivenProperties, request)

	def getCrossSectionType(self) -> DrivenCrossSectionType:
		properties = self._getDrivenProperties()
		return DrivenCrossSectionType(properties.cross_section_type)
	
	def setCrossSectionType(self, crossSectionType: DrivenCrossSectionType):
		properties = self._getDrivenProperties()
		properties.cross_section_type = crossSectionType.value
		self._setDrivenProperties(properties)