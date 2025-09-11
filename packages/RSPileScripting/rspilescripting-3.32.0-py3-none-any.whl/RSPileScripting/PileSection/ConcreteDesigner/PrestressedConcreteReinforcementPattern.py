from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.PrestressedConcreteDesignerReinforcementPatternService_pb2 as  ReinforcementPatternService_pb2
import RSPileScripting.generated_python_files.pile_section_services.PrestressedConcreteDesignerReinforcementPatternService_pb2_grpc as ReinforcementPatternService_pb2_grpc
from RSPileScripting.PileSection.ConcreteDesigner.ReinforcementPatternBaseClass import ReinforcementPatternBaseClass
from enum import Enum

class StrandType(Enum):
	GRADE_250_KSI_LOLAX = ReinforcementPatternService_pb2.StrandType.STRAND_TYPE_GRADE_250_KSI_LOLAX
	GRADE_270_KSI_LOLAX = ReinforcementPatternService_pb2.StrandType.STRAND_TYPE_GRADE_270_KSI_LOLAX
	GRADE_300_KSI_LOLAX = ReinforcementPatternService_pb2.StrandType.STRAND_TYPE_GRADE_300_KSI_LOLAX
	SMOOTH_BARS_145_KSI = ReinforcementPatternService_pb2.StrandType.STRAND_TYPE_SMOOTH_BARS_145_KSI
	SMOOTH_BARS_160_KSI = ReinforcementPatternService_pb2.StrandType.STRAND_TYPE_SMOOTH_BARS_160_KSI
	DEFORMED_BARS_150_160_KSI = ReinforcementPatternService_pb2.StrandType.STRAND_TYPE_DEFORMED_BARS_150_160_KSI

class StrandSize(Enum):
	SIZE_250_5_16_3_WIRE = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_250_5_16_3_WIRE
	SIZE_250_1_4_7_WIRE = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_250_1_4_7_WIRE
	SIZE_250_5_16_7_WIRE = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_250_5_16_7_WIRE
	SIZE_250_3_8_7_WIRE = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_250_3_8_7_WIRE
	SIZE_250_7_16_7_WIRE = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_250_7_16_7_WIRE
	SIZE_250_1_2_7_WIRE = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_250_1_2_7_WIRE
	SIZE_250_06_7_WIRE = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_250_06_7_WIRE
	SIZE_270_5_16_7_WIRE = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_270_5_16_7_WIRE
	SIZE_270_3_8_7_WIRE = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_270_3_8_7_WIRE
	SIZE_270_7_16_7_WIRE = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_270_7_16_7_WIRE
	SIZE_270_1_2_7_WIRE = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_270_1_2_7_WIRE
	SIZE_270_1_2_7_W_SPEC = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_270_1_2_7_W_SPEC
	SIZE_270_9_16_7_WIRE = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_270_9_16_7_WIRE
	SIZE_270_0_6_7_WIRE = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_270_0_6_7_WIRE
	SIZE_270_0_7_7_WIRE = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_270_0_7_7_WIRE
	SIZE_300_3_8_7_WIRE = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_300_3_8_7_WIRE
	SIZE_300_7_16_7_WIRE = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_300_7_16_7_WIRE
	SIZE_300_1_2_7_WIRE = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_300_1_2_7_WIRE
	SIZE_300_1_2_SUPER = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_300_1_2_SUPER
	SIZE_300_0_6_7_WIRE = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_300_0_6_7_WIRE
	SIZE_145_3_4_SMOOTH = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_145_3_4_SMOOTH
	SIZE_145_7_8_SMOOTH = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_145_7_8_SMOOTH
	SIZE_145_1_SMOOTH = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_145_1_SMOOTH
	SIZE_145_1_1_8_SMOOTH = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_145_1_1_8_SMOOTH
	SIZE_145_1_1_4_SMOOTH = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_145_1_1_4_SMOOTH
	SIZE_145_1_3_8_SMOOTH = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_145_1_3_8_SMOOTH
	SIZE_160_3_4_SMOOTH = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_160_3_4_SMOOTH
	SIZE_160_7_8_SMOOTH = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_160_7_8_SMOOTH
	SIZE_160_1_SMOOTH = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_160_1_SMOOTH
	SIZE_160_1_1_8_SMOOTH = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_160_1_1_8_SMOOTH
	SIZE_160_1_1_4_SMOOTH = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_160_1_1_4_SMOOTH
	SIZE_160_1_3_8_SMOOTH = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_160_1_3_8_SMOOTH
	SIZE_157_5_8_DEF_BAR = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_157_5_8_DEF_BAR
	SIZE_150_1_DEF_BAR = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_150_1_DEF_BAR
	SIZE_160_1_DEF_BAR = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_160_1_DEF_BAR
	SIZE_150_1_1_4_DEF_BAR = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_150_1_1_4_DEF_BAR
	SIZE_160_1_1_4_DEF_BAR = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_160_1_1_4_DEF_BAR
	SIZE_160_1_3_8_DEF_BAR = ReinforcementPatternService_pb2.StrandSize.STRAND_SIZE_160_1_3_8_DEF_BAR

class PrestressedConcreteReinforcementPattern(ReinforcementPatternBaseClass):
	"""
	Examples:
	:ref:`prestressed concrete section`
	"""
	def _create_stub(self):
		return ReinforcementPatternService_pb2_grpc.PrestressedConcreteDesignerReinforcementPatternServiceStub(self._client.channel)

	def _getReinforcementPatternProperties(self) -> ReinforcementPatternService_pb2.ReinforcementPatternProperties:
		request = ReinforcementPatternService_pb2.GetReinforcementPatternPropertiesRequest(
			session_id=self._client.sessionID, pattern_id=self._pattern_id)
		response = self._client.callFunction(self._stub.GetReinforcementPattern, request)
		return response.pattern_props

	def _setReinforcementPatternProperties(self, patternProps: ReinforcementPatternService_pb2.SetReinforcementPatternPropertiesRequest):
		request = ReinforcementPatternService_pb2.SetReinforcementPatternPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pattern_id=self._pattern_id, 
			pattern_props=patternProps)
		self._client.callFunction(self._stub.SetReinforcementPattern, request)

	def getStrandType(self) -> StrandType:
		properties = self._getReinforcementPatternProperties()
		return StrandType(properties.strand_type)
	
	def setStrandType(self, strandType: StrandType):
		properties = self._getReinforcementPatternProperties()
		properties.strand_type = strandType.value
		self._setReinforcementPatternProperties(properties)

	def getStrandSize(self) -> StrandSize:
		properties = self._getReinforcementPatternProperties()
		return StrandSize(properties.strand_size)
	
	def setStrandSize(self, strandSize: StrandSize):
		properties = self._getReinforcementPatternProperties()
		properties.strand_size = strandSize.value
		self._setReinforcementPatternProperties(properties)
