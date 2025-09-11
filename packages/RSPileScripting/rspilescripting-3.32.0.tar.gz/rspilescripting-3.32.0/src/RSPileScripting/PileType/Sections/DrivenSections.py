from RSPileScripting.PileType.Sections.SectionsBaseClass import SectionsBaseClass
import RSPileScripting.generated_python_files.pile_type_services.PileTypeSectionsService_pb2 as PileTypeSectionsService_pb2
from enum import Enum

class DrivenPileTypeCrossSection(Enum):
	UNIFORM = PileTypeSectionsService_pb2.CrossSectionType.E_CROSS_SECTION_UNIFORM
	TAPERED = PileTypeSectionsService_pb2.CrossSectionType.E_CROSS_SECTION_TAPERED

class DrivenSections(SectionsBaseClass):
	"""
		Examples:
		:ref:`pile types driven`
	"""
	def getCrossSectionType(self) -> DrivenPileTypeCrossSection:
		properties = self._getPileTypeSectionsProperties()
		return DrivenPileTypeCrossSection(properties.m_cross_section_type)
	
	def setCrossSectionType(self, crossSectionType: DrivenPileTypeCrossSection):
		properties = self._getPileTypeSectionsProperties()
		properties.m_cross_section_type = crossSectionType.value
		self._setPileTypeSectionsProperties(properties)

	def getTaperAngle(self) -> float:
		properties = self._getPileTypeSectionsProperties()
		return properties.m_taper_angle
	
	def setTaperAngle(self, taperAngle: float):
		properties = self._getPileTypeSectionsProperties()
		properties.m_taper_angle = taperAngle
		self._setPileTypeSectionsProperties(properties)