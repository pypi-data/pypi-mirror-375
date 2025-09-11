from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.CommonReinforcementPattern_pb2 as CommonReinforcementPattern_pb2
import RSPileScripting.generated_python_files.pile_section_services.ReinforcedConcreteDesignerReinforcementPatternService_pb2 as ReinforcedConcreteDesignerReinforcementPatternService_pb2
import RSPileScripting.generated_python_files.pile_section_services.ReinforcedConcreteDesignerReinforcementPatternService_pb2_grpc as ReinforcedConcreteDesignerReinforcementPatternService_pb2_grpc
from RSPileScripting.PileSection.ConcreteDesigner.ReinforcementPatternBaseClass import ReinforcementPatternBaseClass
from enum import Enum

class RebarSize(Enum):
	US_STD_3 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_US_STD_3
	US_STD_4 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_US_STD_4
	US_STD_5 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_US_STD_5
	US_STD_6 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_US_STD_6
	US_STD_7 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_US_STD_7
	US_STD_8 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_US_STD_8
	US_STD_9 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_US_STD_9
	US_STD_10 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_US_STD_10
	US_STD_11 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_US_STD_11
	US_STD_14 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_US_STD_14
	US_STD_18 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_US_STD_18
	ASTM_10M = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_ASTM_10M
	ASTM_15M = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_ASTM_15M
	ASTM_20M = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_ASTM_20M
	ASTM_25M = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_ASTM_25M
	ASTM_30M = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_ASTM_30M
	ASTM_35M = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_ASTM_35M
	ASTM_45M = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_ASTM_45M
	ASTM_55M = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_ASTM_55M
	CEB_6_MM = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_CEB_6_MM
	CEB_8_MM = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_CEB_8_MM
	CEB_10_MM = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_CEB_10_MM
	CEB_12_MM = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_CEB_12_MM
	CEB_14_MM = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_CEB_14_MM
	CEB_16_MM = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_CEB_16_MM
	CEB_20_MM = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_CEB_20_MM
	CEB_25_MM = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_CEB_25_MM
	CEB_32_MM = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_CEB_32_MM
	CEB_40_MM = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_CEB_40_MM
	BS4449_6A = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_BS4449_6a
	BS4449_7A = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_BS4449_7a
	BS4449_8 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_BS4449_8
	BS4449_9A = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_BS4449_9a
	BS4449_10 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_BS4449_10
	BS4449_12 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_BS4449_12
	BS4449_16 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_BS4449_16
	BS4449_20 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_BS4449_20
	BS4449_25 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_BS4449_25
	BS4449_32 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_BS4449_32
	BS4449_40 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_BS4449_40
	BS4449_50 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_BS4449_50
	JD_6 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_JD_6
	JD_8 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_JD_8
	JD_10 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_JD_10
	JD_13 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_JD_13
	JD_16 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_JD_16
	JD_19 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_JD_19
	JD_22 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_JD_22
	JD_25 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_JD_25
	JD_29 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_JD_29
	JD_32 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_JD_32
	JD_35 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_JD_35
	JD_38 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_JD_38
	JD_41 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_JD_41
	AS_12 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_AS_12
	AS_16 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_AS_16
	AS_20 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_AS_20
	AS_24 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_AS_24
	AS_28 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_AS_28
	AS_32 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_AS_32
	AS_36 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_AS_36
	NZ_6 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_NZ_6
	NZ_10 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_NZ_10
	NZ_12 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_NZ_12
	NZ_16 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_NZ_16
	NZ_20 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_NZ_20
	NZ_25 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_NZ_25
	NZ_32 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_NZ_32
	NZ_40 = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_NZ_40
	CUSTOM = ReinforcedConcreteDesignerReinforcementPatternService_pb2.RebarSize.REBAR_CUSTOM

class ReinforcedConcreteReinforcementPattern(ReinforcementPatternBaseClass):

	def _create_stub(self):
		return ReinforcedConcreteDesignerReinforcementPatternService_pb2_grpc.ReinforcedConcreteDesignerReinforcementPatternServiceStub(self._client.channel)

	def _getReinforcementPatternProperties(self) -> ReinforcedConcreteDesignerReinforcementPatternService_pb2.ReinforcementPatternProperties:
		request = ReinforcedConcreteDesignerReinforcementPatternService_pb2.GetReinforcementPatternPropertiesRequest(
			session_id=self._client.sessionID, pattern_id=self._pattern_id)
		response = self._client.callFunction(self._stub.GetReinforcementPattern, request)
		return response.pattern_props

	def _setReinforcementPatternProperties(self, patternProps: ReinforcedConcreteDesignerReinforcementPatternService_pb2.SetReinforcementPatternPropertiesRequest):
		request = ReinforcedConcreteDesignerReinforcementPatternService_pb2.SetReinforcementPatternPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pattern_id=self._pattern_id, 
			pattern_props=patternProps)
		self._client.callFunction(self._stub.SetReinforcementPattern, request)

	def getRebarSize(self) -> RebarSize:
		properties = self._getReinforcementPatternProperties()
		return RebarSize(properties.rebar_size)
	
	def setRebarSize(self, rebarSize: RebarSize):
		properties = self._getReinforcementPatternProperties()
		properties.rebar_size = rebarSize.value
		self._setReinforcementPatternProperties(properties)

	def getRebarYieldStress(self) -> float:
		properties = self._getReinforcementPatternProperties()
		return properties.yield_stress_rebar
	
	def setRebarYieldStress(self, yieldStress: float):
		properties = self._getReinforcementPatternProperties()
		properties.yield_stress_rebar = yieldStress
		self._setReinforcementPatternProperties(properties)

	def getRebarElasticModulus(self) -> float:
		properties = self._getReinforcementPatternProperties()
		return properties.elastic_modulus_rebar
	
	def setRebarElasticModulus(self, ultimateStrength: float):
		properties = self._getReinforcementPatternProperties()
		properties.elastic_modulus_rebar = ultimateStrength
		self._setReinforcementPatternProperties(properties)