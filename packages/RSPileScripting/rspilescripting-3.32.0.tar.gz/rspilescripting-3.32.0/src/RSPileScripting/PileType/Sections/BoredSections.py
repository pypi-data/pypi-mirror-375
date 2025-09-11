from RSPileScripting._client import Client
from RSPileScripting.PileType.Sections.SectionsBaseClass import SectionsBaseClass
from RSPileScripting.PileType.Sections.Bell import Bell
import RSPileScripting.generated_python_files.pile_type_services.PileTypeSectionsService_pb2 as PileTypeSectionsService_pb2
from enum import Enum

class BoredPileTypeCrossSection(Enum):
	UNIFORM = PileTypeSectionsService_pb2.CrossSectionType.E_CROSS_SECTION_UNIFORM
	BELL = PileTypeSectionsService_pb2.CrossSectionType.E_CROSS_SECTION_BELL

class BoredSections(SectionsBaseClass):
	"""
		Examples:
		:ref:`pile types bored`
	"""
	def __init__(self, model_id: str, pile_type_id: str, client: Client):
		super().__init__(model_id, pile_type_id, client)
		self.Bell = Bell(self._model_id, self._pile_type_id, self._client)

	def getCrossSectionType(self) -> BoredPileTypeCrossSection:
		properties = self._getPileTypeSectionsProperties()
		return BoredPileTypeCrossSection(properties.m_cross_section_type)
	
	def setCrossSectionType(self, crossSectionType: BoredPileTypeCrossSection):
		properties = self._getPileTypeSectionsProperties()
		properties.m_cross_section_type = crossSectionType.value
		self._setPileTypeSectionsProperties(properties)