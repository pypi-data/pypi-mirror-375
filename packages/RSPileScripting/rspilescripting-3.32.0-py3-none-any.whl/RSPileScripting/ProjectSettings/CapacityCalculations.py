from RSPileScripting._client import Client
from enum import Enum
import RSPileScripting.generated_python_files.ProjectSettingsService_pb2 as ProjectSettingsService_pb2
import RSPileScripting.generated_python_files.ProjectSettingsService_pb2_grpc as ProjectSettingsService_pb2_grpc

class CapacityCalculationType(Enum):
    Driven = ProjectSettingsService_pb2.CapacityCalculationType.DRIVEN
    Bored = ProjectSettingsService_pb2.CapacityCalculationType.BORED
    Helical = ProjectSettingsService_pb2.CapacityCalculationType.HELICAL
    CapacityTableGenerator = ProjectSettingsService_pb2.CapacityCalculationType.CAPACITY_TABLE_GENERATOR

class CapacityTableGeneratorOptions:
    """These options are only available when the capacity calculation type is set to Capacity Table Generator"""
    def __init__(self, client: Client, model_id: str):
        self._client = client
        self._model_id = model_id
        self._stub = ProjectSettingsService_pb2_grpc.ProjectSettingsStub(self._client.channel)
    
    def _getCalculateAllowableCapacitiesProperties(self) -> ProjectSettingsService_pb2.GetCalculateAllowableCapacitiesResponse:
        request = ProjectSettingsService_pb2.GetCalculateAllowableCapacitiesRequest(session_id=self._client.sessionID, model_id=self._model_id)
        return self._client.callFunction(self._stub.GetCalculateAllowableCapacities, request)
    
    def _setCalculateAllowableCapacitiesProperties(self, properties: ProjectSettingsService_pb2.GetCalculateAllowableCapacitiesResponse):
        request = ProjectSettingsService_pb2.SetCalculateAllowableCapacitiesRequest(
            session_id=self._client.sessionID,
            model_id=self._model_id,
            is_total_capacity=properties.is_total_capacity,
            is_skin_friction=properties.is_skin_friction,
            is_skin_friction_end_bearing=properties.is_skin_friction_end_bearing,
            fs1=properties.fs1, fs2=properties.fs2, fs3=properties.fs3, fs4=properties.fs4)
        self._client.callFunction(self._stub.SetCalculateAllowableCapacities, request)
    
    def getIsTotalCapacity(self) -> bool:
        properties = self._getCalculateAllowableCapacitiesProperties()
        return properties.is_total_capacity
    
    def setIsTotalCapacity(self, isTotalCapacity: bool):
        properties = self._getCalculateAllowableCapacitiesProperties()
        properties.is_total_capacity = isTotalCapacity
        self._setCalculateAllowableCapacitiesProperties(properties)
    
    def getIsSkinFriction(self) -> bool:
        properties = self._getCalculateAllowableCapacitiesProperties()
        return properties.is_skin_friction
    
    def setIsSkinFriction(self, isSkinFriction: bool):
        properties = self._getCalculateAllowableCapacitiesProperties()
        properties.is_skin_friction = isSkinFriction
        self._setCalculateAllowableCapacitiesProperties(properties)
    
    def getIsSkinFrictionEndBearing(self) -> bool:
        properties = self._getCalculateAllowableCapacitiesProperties()
        return properties.is_skin_friction_end_bearing
    
    def setIsSkinFrictionEndBearing(self, isSkinFrictionEndBearing: bool):
        properties = self._getCalculateAllowableCapacitiesProperties()
        properties.is_skin_friction_end_bearing = isSkinFrictionEndBearing
        self._setCalculateAllowableCapacitiesProperties(properties)
    
    def getFS1(self) -> float:
        properties = self._getCalculateAllowableCapacitiesProperties()
        return properties.fs1
    
    def setFS1(self, fs1: float):
        """total capacity must be set to true"""
        properties = self._getCalculateAllowableCapacitiesProperties()
        properties.fs1 = fs1
        self._setCalculateAllowableCapacitiesProperties(properties)
    
    def getFS2(self) -> float:
        properties = self._getCalculateAllowableCapacitiesProperties()
        return properties.fs2
    
    def setFS2(self, fs2: float):
        """skin friction must be set to true"""
        properties = self._getCalculateAllowableCapacitiesProperties()
        properties.fs2 = fs2
        self._setCalculateAllowableCapacitiesProperties(properties)
    
    def getFS3(self) -> float:
        properties = self._getCalculateAllowableCapacitiesProperties()
        return properties.fs3
    
    def setFS3(self, fs3: float):
        """skin friction end bearing must be set to true"""
        properties = self._getCalculateAllowableCapacitiesProperties()
        properties.fs3 = fs3
        self._setCalculateAllowableCapacitiesProperties(properties)
    
    def getFS4(self) -> float:
        properties = self._getCalculateAllowableCapacitiesProperties()
        return properties.fs4
    
    def setFS4(self, fs4: float):
        """skin friction end bearing must be set to true"""
        properties = self._getCalculateAllowableCapacitiesProperties()
        properties.fs4 = fs4
        self._setCalculateAllowableCapacitiesProperties(properties)
        
    def getLimitAverageStress(self) -> bool:
        request = ProjectSettingsService_pb2.GetLimitAverageStressRequest(session_id=self._client.sessionID, model_id=self._model_id)
        response : ProjectSettingsService_pb2.GetLimitAverageStressResponse = self._client.callFunction(self._stub.GetLimitAverageStress, request)
        return response.limit_average_stress

    def setLimitAverageStress(self, limitAverageStress: bool):
        request = ProjectSettingsService_pb2.SetLimitAverageStressRequest(session_id=self._client.sessionID,
                                                                        model_id=self._model_id,
                                                                        limit_average_stress=limitAverageStress)
        self._client.callFunction(self._stub.SetLimitAverageStress, request)
class HelicalPileOptions:
    """These options are only available when the capacity calculation type is set to Helical"""
    def __init__(self, client: Client, model_id: str):
        self._client = client
        self._model_id = model_id
        self._stub = ProjectSettingsService_pb2_grpc.ProjectSettingsStub(self._client.channel)
        
    def _getHelicalPileOptionsProperties(self) -> ProjectSettingsService_pb2.GetHelicalOptionsResponse:
        request = ProjectSettingsService_pb2.GetHelicalOptionsRequest(session_id=self._client.sessionID, model_id=self._model_id)
        return self._client.callFunction(self._stub.GetHelicalOptions, request)
    
    def _setHelicalPileOptionsProperties(self, properties: ProjectSettingsService_pb2.GetHelicalOptionsResponse):
        request = ProjectSettingsService_pb2.SetHelicalOptionsRequest(session_id=self._client.sessionID,
                                                                        model_id=self._model_id,
                                                                        is_include_shaft_adhesion_friction=properties.is_include_shaft_adhesion_friction,
                                                                        is_apply_local_shear_failure_for_helices=properties.is_apply_local_shear_failure_for_helices,
                                                                        is_use_reduced_helix_area_for_end_bearing=properties.is_use_reduced_helix_area_for_end_bearing,
                                                                        is_include_shape_and_depth_factors=properties.is_include_shape_and_depth_factors)
        self._client.callFunction(self._stub.SetHelicalOptions, request)
    
    def getIsIncludeShaftAdhesionFriction(self) -> bool:
        properties = self._getHelicalPileOptionsProperties()
        return properties.is_include_shaft_adhesion_friction
    
    def setIsIncludeShaftAdhesionFriction(self, isIncludeShaftAdhesionFriction: bool):
        properties = self._getHelicalPileOptionsProperties()
        properties.is_include_shaft_adhesion_friction = isIncludeShaftAdhesionFriction
        self._setHelicalPileOptionsProperties(properties)
    
    def getIsApplyLocalShearFailureForHelices(self) -> bool:
        properties = self._getHelicalPileOptionsProperties()
        return properties.is_apply_local_shear_failure_for_helices
    
    def setIsApplyLocalShearFailureForHelices(self, isApplyLocalShearFailureForHelices: bool):
        properties = self._getHelicalPileOptionsProperties()
        properties.is_apply_local_shear_failure_for_helices = isApplyLocalShearFailureForHelices
        self._setHelicalPileOptionsProperties(properties)
    
    def getIsUseReducedHelixAreaForEndBearing(self) -> bool:
        properties = self._getHelicalPileOptionsProperties()
        return properties.is_use_reduced_helix_area_for_end_bearing
    
    def setIsUseReducedHelixAreaForEndBearing(self, isUseReducedHelixAreaForEndBearing: bool):
        properties = self._getHelicalPileOptionsProperties()
        properties.is_use_reduced_helix_area_for_end_bearing = isUseReducedHelixAreaForEndBearing
        self._setHelicalPileOptionsProperties(properties)
    
    def getIsIncludeShapeAndDepthFactors(self) -> bool:
        properties = self._getHelicalPileOptionsProperties()
        return properties.is_include_shape_and_depth_factors
    
    def setIsIncludeShapeAndDepthFactors(self, isIncludeShapeAndDepthFactors: bool):
        properties = self._getHelicalPileOptionsProperties()
        properties.is_include_shape_and_depth_factors = isIncludeShapeAndDepthFactors
        self._setHelicalPileOptionsProperties(properties)
class CapacityCalculations():
    def __init__(self, client: Client, model_id: str):
        self._client = client
        self._model_id = model_id
        self._stub = ProjectSettingsService_pb2_grpc.ProjectSettingsStub(self._client.channel)
        self.CapacityTableGeneratorOptions = CapacityTableGeneratorOptions(client, model_id)
        self.HelicalPileOptions = HelicalPileOptions(client, model_id)
        
    def getCapacityCalculationType(self) -> CapacityCalculationType:
        request = ProjectSettingsService_pb2.GetCapacityCalculationTypeRequest(session_id=self._client.sessionID, model_id=self._model_id)
        response : ProjectSettingsService_pb2.GetCapacityCalculationTypeResponse = self._client.callFunction(self._stub.GetCapacityCalculationType, request)
        return CapacityCalculationType(response.capacity_calculation_type)
    
    def setCapacityCalculationType(self, capacityCalculationType: CapacityCalculationType):
        request = ProjectSettingsService_pb2.SetCapacityCalculationTypeRequest(session_id=self._client.sessionID,
                                                                              model_id=self._model_id,
                                                                              capacity_calculation_type=capacityCalculationType.value)
        self._client.callFunction(self._stub.SetCapacityCalculationType, request)
    
