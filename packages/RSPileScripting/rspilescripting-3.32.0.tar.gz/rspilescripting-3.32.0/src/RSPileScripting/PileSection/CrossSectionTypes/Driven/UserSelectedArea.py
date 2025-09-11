from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.DrivenCrossSectionRolledSectionUserSelectedAreaService_pb2 as DrivenCrossSectionRolledSectionUserSelectedAreaService_pb2
import RSPileScripting.generated_python_files.pile_section_services.DrivenCrossSectionRolledSectionUserSelectedAreaService_pb2_grpc as DrivenCrossSectionRolledSectionUserSelectedAreaService_pb2_grpc

class UserSelectedArea:
    def __init__(self, model_id: str, pile_id: str, client: Client):
        self._model_id = model_id
        self._pile_id = pile_id
        self._client = client
        self._stub = DrivenCrossSectionRolledSectionUserSelectedAreaService_pb2_grpc.DrivenCrossSectionRolledSectionUserSelectedAreaServiceStub(self._client.channel)

    def _getUserSelectedAreaProperties(self) -> DrivenCrossSectionRolledSectionUserSelectedAreaService_pb2.RolledSectionUserSelectedAreaProperties:
        request = DrivenCrossSectionRolledSectionUserSelectedAreaService_pb2.GetRolledSectionUserSelectedAreaPropertiesRequest(
            session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
        response = self._client.callFunction(self._stub.GetRolledSectionUserSelectedAreaProperties, request)
        return response.rolled_section_user_selected_area_props

    def _setUserSelectedAreaProperties(self, RolledSectionUserSelectedAreaProps: DrivenCrossSectionRolledSectionUserSelectedAreaService_pb2.RolledSectionUserSelectedAreaProperties):
        request = DrivenCrossSectionRolledSectionUserSelectedAreaService_pb2.SetRolledSectionUserSelectedAreaPropertiesRequest(
            session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
            rolled_section_user_selected_area_props=RolledSectionUserSelectedAreaProps)
        self._client.callFunction(self._stub.SetRolledSectionUserSelectedAreaProperties, request)

    def getAreaOfTip(self) -> float:
        properties = self._getUserSelectedAreaProperties()
        return properties.rolled_section_area_user_select
    
    def setAreaOfTip(self, areaOfTip: float):
        properties = self._getUserSelectedAreaProperties()
        properties.rolled_section_area_user_select = areaOfTip
        self._setUserSelectedAreaProperties(properties)