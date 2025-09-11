from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.LateralPiedmontService_pb2 as LateralPiedmontService_pb2
import RSPileScripting.generated_python_files.soil_services.LateralPiedmontService_pb2_grpc as LateralPiedmontService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class LateralPiedmontResidualDatumProperties(Enum):
	DILATOMETER_MODULUS = "LAT_PIEDMONT_DILATOMETER"
	CPT_TIP_RESISTANCE = "LAT_PIEDMONT_CPT"
	SPT_BLOW_COUNT = "LAT_PIEDMONT_SPT"
	MENARD_PRESSUREMETER_MODULUS = "LAT_PIEDMONT_MENARD_MODULUS"

class PiedmontTestValueType(Enum):
	DIALTOMETER_MODULUS = LateralPiedmontService_pb2.PiedmontAnalysisType.E_DILATOMETER_MODULUS
	CONE_PENETRATION_TIP_RESISTANCE = LateralPiedmontService_pb2.PiedmontAnalysisType.E_CONE_PENETRATION_TIP_RESISTANCE
	SPT_BLOW_COUNT = LateralPiedmontService_pb2.PiedmontAnalysisType.E_STANDARD_PENETRATION_BLOW_COUNT
	MENARD_PRESSUREMETER_MODULUS = LateralPiedmontService_pb2.PiedmontAnalysisType.E_MENARD_PRESSUREMETER_MODULUS

class PiedmontResidual:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = LateralPiedmontService_pb2_grpc.LateralPiedmontServiceStub(self._client.channel)
		self.Datum: Datum[LateralPiedmontResidualDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.LATERAL
		)

	def _getPiedmontProperties(self) -> LateralPiedmontService_pb2.PiedmontProperties:
		request = LateralPiedmontService_pb2.GetPiedmontRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetPiedmontProperties, request)
		return response.piedmont_props

	def _setPiedmontProperties(self, piedmontProps: LateralPiedmontService_pb2.PiedmontProperties):
		request = LateralPiedmontService_pb2.SetPiedmontRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, piedmont_props=piedmontProps)
		self._client.callFunction(self._stub.SetPiedmontProperties, request)

	def getPiedmontAnalysisType(self) -> PiedmontTestValueType:
		properties = self._getPiedmontProperties()
		return PiedmontTestValueType(properties.piedmont_analysis_type)

	def setPiedmontAnalysisType(self, piedmontTestValueType: PiedmontTestValueType):
		properties = self._getPiedmontProperties()
		properties.piedmont_analysis_type = piedmontTestValueType.value
		self._setPiedmontProperties(properties)

	def getDilatometerModulus(self) -> float:
		properties = self._getPiedmontProperties()
		return properties.dilatometer_modulus

	def setDilatometerModulus(self, dilatometerModulus: float):
		properties = self._getPiedmontProperties()
		properties.dilatometer_modulus = dilatometerModulus
		self._setPiedmontProperties(properties)

	def getConePenetrationTipResistance(self) -> float:
		properties = self._getPiedmontProperties()
		return properties.cone_penetration_piedmont

	def setConePenetrationTipResistance(self, conePenetrationTipResistance: float):
		properties = self._getPiedmontProperties()
		properties.cone_penetration_piedmont = conePenetrationTipResistance
		self._setPiedmontProperties(properties)

	def getStandardPenetrationBlowCount(self) -> float:
		properties = self._getPiedmontProperties()
		return properties.standard_penetration_blow_count

	def setStandardPenetrationBlowCount(self, standardPenetrationBlowCount: float):
		properties = self._getPiedmontProperties()
		properties.standard_penetration_blow_count = standardPenetrationBlowCount
		self._setPiedmontProperties(properties)

	def getMenardPressuremeterModulus(self) -> float:
		properties = self._getPiedmontProperties()
		return properties.menard_pressuremeter_modulus

	def setMenardPressuremeterModulus(self, menardPressuremeterModulus: float):
		properties = self._getPiedmontProperties()
		properties.menard_pressuremeter_modulus = menardPressuremeterModulus
		self._setPiedmontProperties(properties)