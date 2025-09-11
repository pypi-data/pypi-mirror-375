from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.DrivenCrossSectionOpenEndPipeService_pb2 as DrivenCrossSectionOpenEndPipeService_pb2
import RSPileScripting.generated_python_files.pile_section_services.DrivenCrossSectionOpenEndPipeService_pb2_grpc as DrivenCrossSectionOpenEndPipeService_pb2_grpc

class OpenEndPipe:
    def __init__(self, model_id: str, pile_id: str, client: Client):
        self._model_id = model_id
        self._pile_id = pile_id
        self._client = client
        self._stub = DrivenCrossSectionOpenEndPipeService_pb2_grpc.DrivenCrossSectionOpenEndPipeServiceStub(self._client.channel)

    def _getOpenEndPipeProperties(self) -> DrivenCrossSectionOpenEndPipeService_pb2.OpenEndPipeProperties:
        request = DrivenCrossSectionOpenEndPipeService_pb2.GetOpenEndPipePropertiesRequest(
            session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
        response = self._client.callFunction(self._stub.GetOpenEndPipeProperties, request)
        return response.open_end_pipe_props

    def _setOpenEndPipeProperties(self, openEndPipeProps: DrivenCrossSectionOpenEndPipeService_pb2.OpenEndPipeProperties):
        request = DrivenCrossSectionOpenEndPipeService_pb2.SetOpenEndPipePropertiesRequest(
            session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
            open_end_pipe_props=openEndPipeProps)
        self._client.callFunction(self._stub.SetOpenEndPipeProperties, request)

    def getDiameterOfPile(self) -> float:
        properties = self._getOpenEndPipeProperties()
        return properties.diameter_ppo
    
    def setDiameterOfPile(self, diameterOfPile: float):
        properties = self._getOpenEndPipeProperties()
        properties.diameter_ppo = diameterOfPile
        self._setOpenEndPipeProperties(properties)

    def getShellThickness(self) -> float:
        properties = self._getOpenEndPipeProperties()
        return properties.shell_thickness_ppo
    
    def setShellThickness(self, shellThickness: float):
        properties = self._getOpenEndPipeProperties()
        properties.shell_thickness_ppo = shellThickness
        self._setOpenEndPipeProperties(properties)