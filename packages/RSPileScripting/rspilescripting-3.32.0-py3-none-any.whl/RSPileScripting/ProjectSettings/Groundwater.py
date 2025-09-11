from RSPileScripting._client import Client
from enum import Enum
import RSPileScripting.generated_python_files.ProjectSettingsService_pb2 as ProjectSettingsService_pb2
import RSPileScripting.generated_python_files.ProjectSettingsService_pb2_grpc as ProjectSettingsService_pb2_grpc

class GroundwaterMethod(Enum):
    PIEZOMETRIC_LINE = ProjectSettingsService_pb2.GroundwaterMethod.PIEZOMETRIC_LINE
    GRID = ProjectSettingsService_pb2.GroundwaterMethod.GRID
class Groundwater:
    def __init__(self, client: Client, model_id: str):
        self._client = client
        self._model_id = model_id
        self._stub = ProjectSettingsService_pb2_grpc.ProjectSettingsStub(self._client.channel)
        
    def _getGroundwaterProperties(self) -> ProjectSettingsService_pb2.GetGroundwaterResponse:
        request = ProjectSettingsService_pb2.GetGroundwaterRequest(session_id=self._client.sessionID, model_id=self._model_id)
        return self._client.callFunction(self._stub.GetGroundwater, request)
    
    def _setGroundwaterProperties(self, properties: ProjectSettingsService_pb2.GetGroundwaterResponse):
        request = ProjectSettingsService_pb2.SetGroundwaterRequest(session_id=self._client.sessionID, model_id=self._model_id, 
                                                                 is_groundwater_analysis=properties.is_groundwater_analysis,
                                                                 groundwater_method=properties.groundwater_method,
                                                                 water_unit_weight=properties.water_unit_weight)
        self._client.callFunction(self._stub.SetGroundwater, request)
        
    def getIsGroundwaterAnalysis(self) -> bool:
        properties = self._getGroundwaterProperties()
        return properties.is_groundwater_analysis
    
    def setIsGroundwaterAnalysis(self, isGroundwaterAnalysis: bool):
        properties = self._getGroundwaterProperties()
        properties.is_groundwater_analysis = isGroundwaterAnalysis
        self._setGroundwaterProperties(properties)
        
    def getGroundwaterMethod(self) -> GroundwaterMethod:
        properties = self._getGroundwaterProperties()
        return GroundwaterMethod(properties.groundwater_method)
    
    def setGroundwaterMethod(self, groundwaterMethod: GroundwaterMethod):
        properties = self._getGroundwaterProperties()
        properties.groundwater_method = groundwaterMethod.value
        self._setGroundwaterProperties(properties)
        
    def getWaterUnitWeight(self) -> float:
        properties = self._getGroundwaterProperties()
        return properties.water_unit_weight
    
    def setWaterUnitWeight(self, waterUnitWeight: float):
        properties = self._getGroundwaterProperties()
        properties.water_unit_weight = waterUnitWeight
        self._setGroundwaterProperties(properties)
        