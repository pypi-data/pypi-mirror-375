from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.PileAnalysisCrossSectionCircularService_pb2 as PileAnalysisCrossSectionCircularService_pb2
import RSPileScripting.generated_python_files.pile_section_services.PileAnalysisCrossSectionCircularService_pb2_grpc as PileAnalysisCrossSectionCircularService_pb2_grpc

class Circular:
	"""
	Examples:
	:ref:`pile sections pile analysis`
	"""
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = PileAnalysisCrossSectionCircularService_pb2_grpc.PileAnalysisCrossSectionCircularServiceStub(self._client.channel)

	def _getCircularProperties(self) -> PileAnalysisCrossSectionCircularService_pb2.CircularProperties:
		request = PileAnalysisCrossSectionCircularService_pb2.GetCircularPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetCircularProperties, request)
		return response.circular_props

	def _setCircularProperties(self, circularProps: PileAnalysisCrossSectionCircularService_pb2.CircularProperties):
		request = PileAnalysisCrossSectionCircularService_pb2.SetCircularPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			circular_props=circularProps)
		self._client.callFunction(self._stub.SetCircularProperties, request)

	def getDiameter(self) -> float:
		properties = self._getCircularProperties()
		return properties.diameter
	
	def setDiameter(self, diameter: float):
		properties = self._getCircularProperties()
		properties.diameter = diameter
		self._setCircularProperties(properties)