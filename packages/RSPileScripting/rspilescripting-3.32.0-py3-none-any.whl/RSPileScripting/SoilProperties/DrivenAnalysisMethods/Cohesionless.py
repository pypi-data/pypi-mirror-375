from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.DrivenCohesionlessService_pb2 as DrivenCohesionlessService_pb2
import RSPileScripting.generated_python_files.soil_services.DrivenCohesionlessService_pb2_grpc as DrivenCohesionlessService_pb2_grpc
from RSPileScripting.SoilProperties.DrivenAnalysisMethods.CohesionlessSkinFrictionSPTTable import SkinFrictionSPTTable
from RSPileScripting.SoilProperties.DrivenAnalysisMethods.CohesionlessEndBearingSPTTable import EndBearingSPTTable
from RSPileScripting.SoilProperties.InternalFrictionAngleMethod import InternalFrictionAngleMethod

class Cohesionless:
	"""
	Examples:
	:ref:`soil properties driven`
	"""
	def __init__(self, model_id: str, soil_id: int, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = DrivenCohesionlessService_pb2_grpc.DrivenCohesionlessServiceStub(self._client.channel)
		self.SkinFrictionSPTTable = SkinFrictionSPTTable(model_id=self._model_id, soil_id=self._soil_id, client=self._client)
		self.EndBearingSPTTable = EndBearingSPTTable(model_id=self._model_id, soil_id=self._soil_id, client=self._client)

	def _getCohesionlessProperties(self) -> DrivenCohesionlessService_pb2.DrivenCohesionlessProperties:
		request = DrivenCohesionlessService_pb2.GetCohesionlessRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetCohesionlessProperties, request)
		return response.driven_cohesionless_props

	def _setCohesionlessProperties(self, cohesionlessProperties: DrivenCohesionlessService_pb2.DrivenCohesionlessProperties):
		request = DrivenCohesionlessService_pb2.SetCohesionlessRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, driven_cohesionless_props=cohesionlessProperties)
		self._client.callFunction(self._stub.SetCohesionlessProperties, request)

	def setInternalFrictionAngleSkinFrictionMethod(self, internalFrictionAngleMethod: InternalFrictionAngleMethod):
		properties = self._getCohesionlessProperties()

		if internalFrictionAngleMethod == InternalFrictionAngleMethod.USE_FRICTION_ANGLE:
			properties.use_sptn_test_skin_friction = False
		elif internalFrictionAngleMethod == InternalFrictionAngleMethod.USE_SPT_N_VALUES:
			properties.use_sptn_test_skin_friction = True
		else:
			raise ValueError("Invalid internal friction angle method")
		self._setCohesionlessProperties(properties)

	def getInternalFrictionAngleSkinFrictionMethod(self) -> InternalFrictionAngleMethod:
		properties = self._getCohesionlessProperties()

		if properties.use_sptn_test_skin_friction:
			return InternalFrictionAngleMethod.USE_SPT_N_VALUES
		else:
			return InternalFrictionAngleMethod.USE_FRICTION_ANGLE
		
	def setInternalFrictionAngleEndBearingMethod(self, internalFrictionAngleMethod: InternalFrictionAngleMethod):
		properties = self._getCohesionlessProperties()

		if internalFrictionAngleMethod == InternalFrictionAngleMethod.USE_FRICTION_ANGLE:
			properties.use_sptn_test_end_bearing = False
		elif internalFrictionAngleMethod == InternalFrictionAngleMethod.USE_SPT_N_VALUES:
			properties.use_sptn_test_end_bearing = True
		else:
			raise ValueError("Invalid internal friction angle method")
		self._setCohesionlessProperties(properties)

	def getInternalFrictionAngleEndBearingMethod(self) -> InternalFrictionAngleMethod:
		properties = self._getCohesionlessProperties()

		if properties.use_sptn_test_end_bearing:
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