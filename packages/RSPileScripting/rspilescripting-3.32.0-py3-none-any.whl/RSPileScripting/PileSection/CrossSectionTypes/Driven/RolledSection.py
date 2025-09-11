from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.DrivenCrossSectionRolledSectionService_pb2 as DrivenCrossSectionRolledSectionService_pb2
import RSPileScripting.generated_python_files.pile_section_services.DrivenCrossSectionRolledSectionService_pb2_grpc as DrivenCrossSectionRolledSectionService_pb2_grpc
from RSPileScripting.PileSection.CrossSectionTypes.Driven.UserSelectedArea import UserSelectedArea
from RSPileScripting.PileSection.CrossSectionTypes.Driven.section_types import PileSectionDesignation

from enum import Enum

class RolledSectionPerimeter(Enum):
	ROLLED_SECTION_PERIMETER = DrivenCrossSectionRolledSectionService_pb2.RolledSectionPerimeter.E_H_PILE_PERIMETER
	ROLLED_SECTION_BOX_PERIMETER = DrivenCrossSectionRolledSectionService_pb2.RolledSectionPerimeter.E_H_BOX_PERIMETER

class RolledSectionArea(Enum):
	ROLLED_SECTION_AREA = DrivenCrossSectionRolledSectionService_pb2.RolledSectionArea.E_H_PILE_AREA
	ROLLED_SECTION_BOX_AREA = DrivenCrossSectionRolledSectionService_pb2.RolledSectionArea.E_H_BOX_AREA
	USER_SELECT = DrivenCrossSectionRolledSectionService_pb2.RolledSectionArea.E_H_USER_SELECT

class RolledSectionShape(Enum):
	I_BEAM = "I-beam"
	HOLLOW_SECTION = "Hollow section"

class RolledSectionType(Enum):
	# Types for I-beam shape
	W = "W"
	M = "M"
	S = "S"
	HP = "HP"
	# Types for Hollow section shape
	PIPE = "PIPE"
	HSS = "HSS"

class RolledSection:
	"""
	Examples:
	:ref:`pile sections driven`
	"""
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = DrivenCrossSectionRolledSectionService_pb2_grpc.DrivenCrossSectionRolledSectionServiceStub(self._client.channel)
		self.UserSelectedArea = UserSelectedArea(self._model_id, self._pile_id, self._client)

	def _getRolledSectionProperties(self) -> DrivenCrossSectionRolledSectionService_pb2.RolledSectionProperties:
		request = DrivenCrossSectionRolledSectionService_pb2.GetRolledSectionPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetRolledSectionProperties, request)
		return response.rolled_section_props

	def _setRolledSectionProperties(self, RolledSectionProps: DrivenCrossSectionRolledSectionService_pb2.RolledSectionProperties):
		request = DrivenCrossSectionRolledSectionService_pb2.SetRolledSectionPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			rolled_section_props=RolledSectionProps)
		self._client.callFunction(self._stub.SetRolledSectionProperties, request)

	def getSectionDepth(self) -> float:
		return self._getRolledSectionProperties().depth

	def getSectionWidth(self) -> float:
		return self._getRolledSectionProperties().width

	def getSectionArea(self) -> float:
		return self._getRolledSectionProperties().section_area

	def getSectionBoxArea(self) -> float:
		return self._getRolledSectionProperties().box_area

	def getSectionPerimeter(self) -> float:
		return self._getRolledSectionProperties().section_perimeter

	def getSectionBoxPerimeter(self) -> float:
		return self._getRolledSectionProperties().box_perimeter

	def getMinimumMomentOfInertia(self) -> float:
		return self._getRolledSectionProperties().minimum_moment_of_inertia

	def getMaximumMomentOfInertia(self) -> float:
		return self._getRolledSectionProperties().maximum_moment_of_inertia

	def getWeight(self) -> float:
		return self._getRolledSectionProperties().weight

	def getWebThickness(self) -> float:
		return self._getRolledSectionProperties().web_thickness

	def getFlangeThickness(self) -> float:
		return self._getRolledSectionProperties().flange_thickness

	def getShape(self) -> RolledSectionShape:
		return RolledSectionShape(self._getRolledSectionProperties().shape)

	def getType(self) -> RolledSectionType:
		return RolledSectionType(self._getRolledSectionProperties().type)

	def getDesignation(self) -> str:
		"""Returns the designation string (see PileSectionDesignation for valid values)."""
		return self._getRolledSectionProperties().designation

	def getAreaForEndBearing(self):
		return RolledSectionArea(self._getRolledSectionProperties().area_for_end_bearing)

	def setAreaForEndBearing(self, value: RolledSectionArea):
		props = self._getRolledSectionProperties()
		props.area_for_end_bearing = value.value
		self._setRolledSectionProperties(props)

	def getPerimeterForSkinFriction(self):
		return RolledSectionPerimeter(self._getRolledSectionProperties().perimeter_for_skin_friction)

	def setPerimeterForSkinFriction(self, value: RolledSectionPerimeter):
		props = self._getRolledSectionProperties()
		props.perimeter_for_skin_friction = value.value
		self._setRolledSectionProperties(props)

	def getShapeType(self):
		return self._getRolledSectionProperties().shape

	def setDesignation(self, designation: PileSectionDesignation):
		"""
		Sets the shape, type, and designation. Shape and type are inferred from the designation.
		
		Args:
			designation: PileSectionDesignation enum value from section_types.py 
						 (e.g., PileSectionDesignation.HP250_x_85)
		"""
		props = self._getRolledSectionProperties()
		designation_name = designation.name
		if designation_name.startswith("W") or designation_name.startswith("M") or designation_name.startswith("S") or designation_name.startswith("HP"):
			props.shape = RolledSectionShape.I_BEAM.value
			if designation_name.startswith("W"):
				props.type = RolledSectionType.W.value
			elif designation_name.startswith("M"):
				props.type = RolledSectionType.M.value
			elif designation_name.startswith("S"):
				props.type = RolledSectionType.S.value
			elif designation_name.startswith("HP"):
				props.type = RolledSectionType.HP.value
		elif designation_name.startswith("HSS") or designation_name.startswith("Pipe"):
			props.shape = RolledSectionShape.HOLLOW_SECTION.value
			if designation_name.startswith("HSS"):
				props.type = RolledSectionType.HSS.value
			elif designation_name.startswith("Pipe"):
				props.type = RolledSectionType.PIPE.value
		else:
			raise ValueError("Could not infer shape and type from designation.")
			
		props.designation = designation.value
		self._setRolledSectionProperties(props)
