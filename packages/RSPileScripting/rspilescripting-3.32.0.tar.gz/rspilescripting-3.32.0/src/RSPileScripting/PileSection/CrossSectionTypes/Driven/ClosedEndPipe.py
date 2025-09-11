from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.DrivenCrossSectionClosedEndPipeService_pb2 as DrivenCrossSectionClosedEndPipeService_pb2
import RSPileScripting.generated_python_files.pile_section_services.DrivenCrossSectionClosedEndPipeService_pb2_grpc as DrivenCrossSectionClosedEndPipeService_pb2_grpc

class ClosedEndPipe:
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = DrivenCrossSectionClosedEndPipeService_pb2_grpc.DrivenCrossSectionClosedEndPipeServiceStub(self._client.channel)

	def _getClosedEndPipeProperties(self) -> DrivenCrossSectionClosedEndPipeService_pb2.ClosedEndPipeProperties:
		request = DrivenCrossSectionClosedEndPipeService_pb2.GetClosedEndPipePropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetClosedEndPipeProperties, request)
		return response.closed_end_pipe_props

	def _setClosedEndPipeProperties(self, closedEndPipeProps: DrivenCrossSectionClosedEndPipeService_pb2.ClosedEndPipeProperties):
		request = DrivenCrossSectionClosedEndPipeService_pb2.SetClosedEndPipePropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			closed_end_pipe_props=closedEndPipeProps)
		self._client.callFunction(self._stub.SetClosedEndPipeProperties, request)

	def getDiameterOfPile(self) -> float:
		properties = self._getClosedEndPipeProperties()
		return properties.diameter_ppc
	
	def setDiameterOfPile(self, diameterOfPile: float):
		properties = self._getClosedEndPipeProperties()
		properties.diameter_ppc = diameterOfPile
		self._setClosedEndPipeProperties(properties)