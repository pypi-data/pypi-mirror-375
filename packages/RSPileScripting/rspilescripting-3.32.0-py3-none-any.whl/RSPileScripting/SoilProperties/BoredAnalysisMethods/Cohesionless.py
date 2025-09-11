from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.BoredCohesionlessService_pb2 as BoredCohesionlessService_pb2
import RSPileScripting.generated_python_files.soil_services.BoredCohesionlessService_pb2_grpc as BoredCohesionlessService_pb2_grpc
from RSPileScripting.SoilProperties.BoredAnalysisMethods.CohesionlessBetaNQMethod import BetaNQ
from RSPileScripting.SoilProperties.BoredAnalysisMethods.CohesionlessKsDelta import KsDelta
from RSPileScripting.SoilProperties.BoredAnalysisMethods.CohesionlessSPTAASHTO import SPTAASHTO
from RSPileScripting.SoilProperties.BoredAnalysisMethods.CohesionlessSPTUserDefined import SPTUserFactors
from RSPileScripting.SoilProperties.BoredAnalysisMethods.CohesionlessSPTTable import SPTTable
from RSPileScripting.SoilProperties.InternalFrictionAngleMethod import InternalFrictionAngleMethod
from enum import Enum

class CohesionlessType(Enum):
	KS_DELTA_METHOD = BoredCohesionlessService_pb2.BoredCohesionlessType.E_SF_KS_DELTA
	SPT_AASHTO_METHOD = BoredCohesionlessService_pb2.BoredCohesionlessType.E_SF_SPT_AASHTO
	SPT_USER_FACTORS_METHOD = BoredCohesionlessService_pb2.BoredCohesionlessType.E_SF_SPT_USER_FACTORS
	BETA_NQ_METHOD = BoredCohesionlessService_pb2.BoredCohesionlessType.E_SF_BETA_NQ

class Cohesionless:
	def __init__(self, model_id: str, soil_id: int, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = BoredCohesionlessService_pb2_grpc.BoredCohesionlessServiceStub(self._client.channel)
		self.BetaNQ = BetaNQ(model_id=self._model_id, soil_id=self._soil_id, client=self._client)
		self.KsDelta = KsDelta(model_id=self._model_id, soil_id=self._soil_id, client=self._client)
		self.SPTAASHTO = SPTAASHTO(model_id=self._model_id, soil_id=self._soil_id, client=self._client)
		self.SPTUserFactors = SPTUserFactors(model_id=self._model_id, soil_id=self._soil_id, client=self._client)
		self.SPTTable = SPTTable(model_id=self._model_id, soil_id=self._soil_id, client=self._client)

	def _getCohesionlessProperties(self) -> BoredCohesionlessService_pb2.BoredCohesionlessProperties:
		request = BoredCohesionlessService_pb2.GetCohesionlessRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetCohesionlessProperties, request)
		return response.bored_cohesionless_props

	def _setCohesionlessProperties(self, cohesionlessProperties: BoredCohesionlessService_pb2.BoredCohesionlessProperties):
		request = BoredCohesionlessService_pb2.SetCohesionlessRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, bored_cohesionless_props=cohesionlessProperties)
		self._client.callFunction(self._stub.SetCohesionlessProperties, request)

	def getCohesionlessType(self) -> CohesionlessType:
		properties = self._getCohesionlessProperties()
		return CohesionlessType(properties.bored_cohesionless_type)

	def setCohesionlessType(self, cohesionlessType: CohesionlessType):
		properties = self._getCohesionlessProperties()
		properties.bored_cohesionless_type = cohesionlessType.value
		self._setCohesionlessProperties(properties)

	def setInternalFrictionAngleMethod(self, internalFrictionAngleMethod: InternalFrictionAngleMethod):
		properties = self._getCohesionlessProperties()

		if internalFrictionAngleMethod == InternalFrictionAngleMethod.USE_FRICTION_ANGLE:
			properties.use_sptn_test_skin_friction = False
		elif internalFrictionAngleMethod == InternalFrictionAngleMethod.USE_SPT_N_VALUES:
			properties.use_sptn_test_skin_friction = True
		else:
			raise ValueError("Invalid internal friction angle method")

		self._setCohesionlessProperties(properties)

	def getInternalFrictionAngleMethod(self) -> InternalFrictionAngleMethod:
		properties = self._getCohesionlessProperties()
		if properties.use_sptn_test_skin_friction:
			return InternalFrictionAngleMethod.USE_SPT_N_VALUES
		else:
			return InternalFrictionAngleMethod.USE_FRICTION_ANGLE

	def setSkinFrictionAngle(self, skinFrictionAngle: float):
		properties = self._getCohesionlessProperties()
		properties.skin_friction_angle = skinFrictionAngle
		self._setCohesionlessProperties(properties)

	def getSkinFrictionAngle(self) -> float:
		properties = self._getCohesionlessProperties()
		return properties.skin_friction_angle

	def setEndBearingAngle(self, endBearingAngle: float):
		properties = self._getCohesionlessProperties()
		properties.end_bearing_angle = endBearingAngle
		self._setCohesionlessProperties(properties)

	def getEndBearingAngle(self) -> float:
		properties = self._getCohesionlessProperties()
		return properties.end_bearing_angle