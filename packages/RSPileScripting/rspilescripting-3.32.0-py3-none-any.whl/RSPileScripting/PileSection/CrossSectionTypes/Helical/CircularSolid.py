from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.HelicalCrossSectionCircularSolidService_pb2 as HelicalCrossSectionCircularSolidService_pb2
import RSPileScripting.generated_python_files.pile_section_services.HelicalCrossSectionCircularSolidService_pb2_grpc as HelicalCrossSectionCircularSolidService_pb2_grpc

class CircularSolid:
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = HelicalCrossSectionCircularSolidService_pb2_grpc.HelicalCrossSectionCircularSolidServiceStub(self._client.channel)

	def _getCircularSolidProperties(self) -> HelicalCrossSectionCircularSolidService_pb2.CircularSolidProperties:
		request = HelicalCrossSectionCircularSolidService_pb2.GetCircularSolidPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetCircularSolidProperties, request)
		return response.circular_solid_props

	def _setCircularSolidProperties(self, circularSolidProps: HelicalCrossSectionCircularSolidService_pb2.CircularSolidProperties):
		request = HelicalCrossSectionCircularSolidService_pb2.SetCircularSolidPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			circular_solid_props=circularSolidProps)
		self._client.callFunction(self._stub.SetCircularSolidProperties, request)

	def getDiameter(self) -> float:
		properties = self._getCircularSolidProperties()
		return properties.diameter
	
	def setDiameter(self, diameter: float):
		properties = self._getCircularSolidProperties()
		properties.diameter = diameter
		self._setCircularSolidProperties(properties)