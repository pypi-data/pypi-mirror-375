from RSPileScripting._client import Client
from enum import Enum
import RSPileScripting.generated_python_files.ProjectSettingsService_pb2 as ProjectSettingsService_pb2
import RSPileScripting.generated_python_files.ProjectSettingsService_pb2_grpc as ProjectSettingsService_pb2_grpc

class IndividualPileAnalysisType(Enum):
    AXIALLY_LOADED = ProjectSettingsService_pb2.IndividualPileAnalysisType.AXIALLY_LOADED
    LATERALLY_LOADED = ProjectSettingsService_pb2.IndividualPileAnalysisType.LATERALLY_LOADED
    AXIALLY_LATERALLY_LOADED = ProjectSettingsService_pb2.IndividualPileAnalysisType.AXIALLY_LATERALLY_LOADED
        
class PileAnalysisType(Enum):
    INDIVIDUAL_PILE_ANALYSIS = ProjectSettingsService_pb2.PileAnalysisType.INDIVIDUAL_PILE_ANALYSIS
    GROUPED_PILE_ANALYSIS = ProjectSettingsService_pb2.PileAnalysisType.GROUPED_PILE_ANALYSIS
    
class PileAnalysisTypeSettings:
    """These options are only available when the capacity calculation type is set to Capacity Table Generator"""
    def __init__(self, client: Client, model_id: str):
        self._client = client
        self._model_id = model_id
        self._stub = ProjectSettingsService_pb2_grpc.ProjectSettingsStub(self._client.channel)
        
    def _getPileAnalysisTypeProperties(self) -> ProjectSettingsService_pb2.GetPileAnalysisTypeResponse:
        request = ProjectSettingsService_pb2.GetPileAnalysisTypeRequest(session_id=self._client.sessionID, model_id=self._model_id)
        return self._client.callFunction(self._stub.GetPileAnalysisType, request)
    
    def _setPileAnalysisTypeProperties(self, properties: ProjectSettingsService_pb2.GetPileAnalysisTypeResponse):
        request = ProjectSettingsService_pb2.SetPileAnalysisTypeRequest(
            session_id=self._client.sessionID,
            model_id=self._model_id,
            pile_analysis_type=properties.pile_analysis_type,
            individual_pile_analysis_type=properties.individual_pile_analysis_type,
            is_multiple_load_cases=properties.is_multiple_load_cases,
            is_include_p_delta_effects=properties.is_include_p_delta_effects)
        self._client.callFunction(self._stub.SetPileAnalysisType, request)
        
    def getPileAnalysisType(self) -> PileAnalysisType:
        properties = self._getPileAnalysisTypeProperties()
        return PileAnalysisType(properties.pile_analysis_type)
    
    def setPileAnalysisType(self, pileAnalysisType: PileAnalysisType):
        properties = self._getPileAnalysisTypeProperties()
        properties.pile_analysis_type = pileAnalysisType.value
        self._setPileAnalysisTypeProperties(properties)
    
    def getIndividualPileAnalysisType(self) -> IndividualPileAnalysisType:
        """Only available if the pile analysis type is set to INDIVIDUAL_PILE_ANALYSIS"""
        properties = self._getPileAnalysisTypeProperties()
        return IndividualPileAnalysisType(properties.individual_pile_analysis_type)
    
    def setIndividualPileAnalysisType(self, individualPileAnalysisType: IndividualPileAnalysisType):
        """Only available if the pile analysis type is set to INDIVIDUAL_PILE_ANALYSIS"""
        properties = self._getPileAnalysisTypeProperties()
        properties.individual_pile_analysis_type = individualPileAnalysisType.value
        self._setPileAnalysisTypeProperties(properties)
    
    def getIsMultipleLoadCases(self) -> bool:
        """Only available if the individual pile analysis type is set to AXIALLY_LATERALLY_LOADED"""
        properties = self._getPileAnalysisTypeProperties()
        return properties.is_multiple_load_cases
    
    def setIsMultipleLoadCases(self, isMultipleLoadCases: bool):
        """Only available if the individual pile analysis type is set to AXIALLY_LATERALLY_LOADED"""
        properties = self._getPileAnalysisTypeProperties()
        properties.is_multiple_load_cases = isMultipleLoadCases
        self._setPileAnalysisTypeProperties(properties)
    
    def getIsIncludePDeltaEffects(self) -> bool:
        """Only available if the individual pile analysis type is set to AXIALLY_LATERALLY_LOADED"""
        properties = self._getPileAnalysisTypeProperties()
        return properties.is_include_p_delta_effects
    
    def setIsIncludePDeltaEffects(self, isIncludePDeltaEffects: bool):
        """Only available if the individual pile analysis type is set to AXIALLY_LATERALLY_LOADED"""
        properties = self._getPileAnalysisTypeProperties()
        properties.is_include_p_delta_effects = isIncludePDeltaEffects
        self._setPileAnalysisTypeProperties(properties)
    
