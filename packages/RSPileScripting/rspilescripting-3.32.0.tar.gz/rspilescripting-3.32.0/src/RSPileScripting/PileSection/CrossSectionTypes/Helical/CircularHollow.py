from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.HelicalCrossSectionCircularHollowService_pb2 as HelicalCrossSectionCircularHollowService_pb2
import RSPileScripting.generated_python_files.pile_section_services.HelicalCrossSectionCircularHollowService_pb2_grpc as HelicalCrossSectionCircularHollowService_pb2_grpc

class CircularHollow:
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = HelicalCrossSectionCircularHollowService_pb2_grpc.HelicalCrossSectionCircularHollowServiceStub(self._client.channel)

	def _getCircularHollowProperties(self) -> HelicalCrossSectionCircularHollowService_pb2.CircularHollowProperties:
		request = HelicalCrossSectionCircularHollowService_pb2.GetCircularHollowPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetCircularHollowProperties, request)
		return response.circular_hollow_props

	def _setCircularHollowProperties(self, circularHollowProps: HelicalCrossSectionCircularHollowService_pb2.CircularHollowProperties):
		request = HelicalCrossSectionCircularHollowService_pb2.SetCircularHollowPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			circular_hollow_props=circularHollowProps)
		self._client.callFunction(self._stub.SetCircularHollowProperties, request)

	def getOuterDiameter(self) -> float:
		properties = self._getCircularHollowProperties()
		return properties.outer_diameter
	
	def setOuterDiameter(self, outerDiameter: float):
		properties = self._getCircularHollowProperties()
		properties.outer_diameter = outerDiameter
		self._setCircularHollowProperties(properties)

	def getThickness(self) -> float:
		properties = self._getCircularHollowProperties()
		return properties.circular_thickness
	
	def setThickness(self, thickness: float):
		properties = self._getCircularHollowProperties()
		properties.circular_thickness = thickness
		self._setCircularHollowProperties(properties)