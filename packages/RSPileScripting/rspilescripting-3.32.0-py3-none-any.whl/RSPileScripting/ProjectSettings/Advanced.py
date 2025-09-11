from RSPileScripting._client import Client
from enum import Enum
import RSPileScripting.generated_python_files.ProjectSettingsService_pb2 as ProjectSettingsService_pb2
import RSPileScripting.generated_python_files.ProjectSettingsService_pb2_grpc as ProjectSettingsService_pb2_grpc

class PileDiscretizationOptions(Enum):
    AUTO = ProjectSettingsService_pb2.PileDiscretization.AUTO
    CUSTOM = ProjectSettingsService_pb2.PileDiscretization.CUSTOM
class Advanced():
    def __init__(self, client: Client, model_id: str):
        self._client = client
        self._model_id = model_id
        self._stub = ProjectSettingsService_pb2_grpc.ProjectSettingsStub(self._client.channel)
        
    def _getAdvancedProperties(self) -> ProjectSettingsService_pb2.GetAdvancedResponse:
        request = ProjectSettingsService_pb2.GetAdvancedRequest(session_id=self._client.sessionID, model_id=self._model_id)
        return self._client.callFunction(self._stub.GetAdvanced, request)
    
    def _setAdvancedProperties(self, properties: ProjectSettingsService_pb2.GetAdvancedResponse):
        request = ProjectSettingsService_pb2.SetAdvancedRequest(
            session_id=self._client.sessionID, 
            model_id=self._model_id, 
            pile_discretization=properties.pile_discretization,
            pile_depth_increment=properties.pile_depth_increment,
            pile_segments=properties.pile_segments,
            convergence_tolerance=properties.convergence_tolerance,
            number_of_iterations=properties.number_of_iterations,
            reinforced_concrete_slices=properties.reinforced_concrete_slices,
            use_method_of_gergiadis_layering_effect=properties.use_method_of_gergiadis_layering_effect
        )
        self._client.callFunction(self._stub.SetAdvanced, request)
            
    def getPileDiscretization(self) -> PileDiscretizationOptions:
        properties = self._getAdvancedProperties()
        return PileDiscretizationOptions(properties.pile_discretization)
    
    def setPileDiscretization(self, pileDiscretization: PileDiscretizationOptions):
        properties = self._getAdvancedProperties()
        properties.pile_discretization = pileDiscretization.value
        self._setAdvancedProperties(properties)
        
    def getPileDepthIncrement(self) -> float:
        properties = self._getAdvancedProperties()
        return properties.pile_depth_increment
    
    def setPileDepthIncrement(self, pileDepthIncrement: float):
        properties = self._getAdvancedProperties()
        properties.pile_depth_increment = pileDepthIncrement
        self._setAdvancedProperties(properties)
        
    def getPileSegments(self) -> int:
        properties = self._getAdvancedProperties()
        return properties.pile_segments
    
    def setPileSegments(self, pileSegments: int):
        properties = self._getAdvancedProperties()
        properties.pile_segments = pileSegments
        self._setAdvancedProperties(properties)
    
    def getConvergenceTolerance(self) -> float:
        properties = self._getAdvancedProperties()
        return properties.convergence_tolerance

    def setConvergenceTolerance(self, convergenceTolerance: float):
        properties = self._getAdvancedProperties()
        properties.convergence_tolerance = convergenceTolerance
        self._setAdvancedProperties(properties)
    
    def getNumberOfIterations(self) -> int:
        properties = self._getAdvancedProperties()
        return properties.number_of_iterations

    def setNumberOfIterations(self, numberOfIterations: int):
        properties = self._getAdvancedProperties()
        properties.number_of_iterations = numberOfIterations
        self._setAdvancedProperties(properties)
    
    def getReinforcedConcreteSlices(self) -> int:
        properties = self._getAdvancedProperties()
        return properties.reinforced_concrete_slices
    
    def setReinforcedConcreteSlices(self, reinforcedConcreteSlices: int):
        properties = self._getAdvancedProperties()
        properties.reinforced_concrete_slices = reinforcedConcreteSlices
        self._setAdvancedProperties(properties)

    def getUseMethodOfGergiadisLayeringEffect(self) -> bool:
        properties = self._getAdvancedProperties()
        return properties.use_method_of_gergiadis_layering_effect
    
    def setUseMethodOfGergiadisLayeringEffect(self, useMethodOfGergiadisLayeringEffect: bool):
        properties = self._getAdvancedProperties()
        properties.use_method_of_gergiadis_layering_effect = useMethodOfGergiadisLayeringEffect
        self._setAdvancedProperties(properties)
