from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.DrivenCrossSectionRaymondService_pb2 as DrivenCrossSectionRaymondService_pb2
import RSPileScripting.generated_python_files.pile_section_services.DrivenCrossSectionRaymondService_pb2_grpc as DrivenCrossSectionRaymondService_pb2_grpc

class Raymond:
    def __init__(self, model_id: str, pile_id: str, client: Client):
        self._model_id = model_id
        self._pile_id = pile_id
        self._client = client
        self._stub = DrivenCrossSectionRaymondService_pb2_grpc.DrivenCrossSectionRaymondServiceStub(self._client.channel)

    def _getRaymondProperties(self) -> DrivenCrossSectionRaymondService_pb2.RaymondProperties:
        request = DrivenCrossSectionRaymondService_pb2.GetRaymondPropertiesRequest(
            session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
        response = self._client.callFunction(self._stub.GetRaymondProperties, request)
        return response.raymond_props

    def _setRaymondProperties(self, raymondProps: DrivenCrossSectionRaymondService_pb2.RaymondProperties):
        request = DrivenCrossSectionRaymondService_pb2.SetRaymondPropertiesRequest(
            session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
            raymond_props=raymondProps)
        self._client.callFunction(self._stub.SetRaymondProperties, request)

    def getDiameterOfPile(self) -> float:
        properties = self._getRaymondProperties()
        return properties.diameter_raymond
    
    def setDiameterOfPile(self, diameterOfPile: float):
        properties = self._getRaymondProperties()
        properties.diameter_raymond = diameterOfPile
        self._setRaymondProperties(properties)