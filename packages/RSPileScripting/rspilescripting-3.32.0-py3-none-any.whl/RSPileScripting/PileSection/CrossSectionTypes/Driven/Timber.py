from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.DrivenCrossSectionTimberService_pb2 as DrivenCrossSectionTimberService_pb2
import RSPileScripting.generated_python_files.pile_section_services.DrivenCrossSectionTimberService_pb2_grpc as DrivenCrossSectionTimberService_pb2_grpc

class Timber:
	"""
	Examples:
	:ref:`pile sections driven`
	"""
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = DrivenCrossSectionTimberService_pb2_grpc.DrivenCrossSectionTimberServiceStub(self._client.channel)

	def _getTimberProperties(self) -> DrivenCrossSectionTimberService_pb2.TimberProperties:
		request = DrivenCrossSectionTimberService_pb2.GetTimberPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetTimberProperties, request)
		return response.timber_props

	def _setTimberProperties(self, timberProps: DrivenCrossSectionTimberService_pb2.TimberProperties):
		request = DrivenCrossSectionTimberService_pb2.SetTimberPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			timber_props=timberProps)
		self._client.callFunction(self._stub.SetTimberProperties, request)

	def getDiameterOfPile(self) -> float:
		properties = self._getTimberProperties()
		return properties.diameter_top_t
	
	def setDiameterOfPile(self, diameterOfPile: float):
		properties = self._getTimberProperties()
		properties.diameter_top_t = diameterOfPile
		self._setTimberProperties(properties)