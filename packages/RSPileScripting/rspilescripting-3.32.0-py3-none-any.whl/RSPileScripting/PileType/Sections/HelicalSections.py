from RSPileScripting._client import Client
from RSPileScripting.PileType.Sections.SectionsBaseClass import SectionsBaseClass
import RSPileScripting.generated_python_files.pile_type_services.PileTypeSectionsService_pb2 as PileTypeSectionsService_pb2
from RSPileScripting.PileType.Sections.Helices import Helices
from enum import Enum

class HelicalPileTypeCrossSection(Enum):
	UNIFORM = PileTypeSectionsService_pb2.CrossSectionType.E_CROSS_SECTION_UNIFORM

class HelicalSections(SectionsBaseClass):
	"""
		Examples:
		:ref:`pile types helical`
	"""
	def __init__(self, model_id: str, pile_type_id: str, client: Client):
		super().__init__(model_id, pile_type_id, client)
		self.Helices = Helices(self._model_id, self._pile_type_id, self._client)

	def getCrossSectionType(self) -> HelicalPileTypeCrossSection:
		properties = self._getPileTypeSectionsProperties()
		return HelicalPileTypeCrossSection(properties.m_cross_section_type)
	
	def setCrossSectionType(self, crossSectionType: HelicalPileTypeCrossSection):
		properties = self._getPileTypeSectionsProperties()
		properties.m_cross_section_type = crossSectionType.value
		self._setPileTypeSectionsProperties(properties)