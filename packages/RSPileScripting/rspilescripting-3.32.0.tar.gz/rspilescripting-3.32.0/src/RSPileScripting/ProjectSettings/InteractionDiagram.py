from RSPileScripting._client import Client
from enum import Enum
import RSPileScripting.generated_python_files.ProjectSettingsService_pb2 as ProjectSettingsService_pb2
import RSPileScripting.generated_python_files.ProjectSettingsService_pb2_grpc as ProjectSettingsService_pb2_grpc

class ConcreteStressStrainCurveModel(Enum):
    """Unified enum for all concrete stress-strain curve model options"""
    MODIFIED_HOGNESTAD = ProjectSettingsService_pb2.ConcreteStressStrainCurveModel.INTERACTION_DIAGRAM_MODIFIED_HOGNESTAD
    WHITNEY_BLOCK = ProjectSettingsService_pb2.ConcreteStressStrainCurveModel.INTERACTION_DIAGRAM_WHITNEY_BLOCK
    EC2_BILINEAR = ProjectSettingsService_pb2.ConcreteStressStrainCurveModel.INTERACTION_DIAGRAM_EC2_BILINEAR
    EC2_PARABOLA = ProjectSettingsService_pb2.ConcreteStressStrainCurveModel.INTERACTION_DIAGRAM_EC2_PARABOLA
    EC2_RECTANGULAR_BLOCK = ProjectSettingsService_pb2.ConcreteStressStrainCurveModel.INTERACTION_DIAGRAM_EC2_RECTANGULAR_BLOCK

class DesignStandard(Enum):
    SINGLE_FACTOR_FOR_M_AND_P = ProjectSettingsService_pb2.DesignStandard.SINGLE_FACTOR_FOR_M_AND_P
    ACI_318_FACTORS_2022 = ProjectSettingsService_pb2.DesignStandard.ACI_318_FACTORS_2022
    EUROCODE_FACTORS_EC2_2004 = ProjectSettingsService_pb2.DesignStandard.EUROCODE_FACTORS_EC2_2004
    
class EurocodeParameters:
    """Only available if the Interaction Diagram Design Standard is set to EUROCODE_FACTORS_EC2_2004"""
    def __init__(self, client: Client, model_id: str):
        self._client = client
        self._model_id = model_id
        self._stub = ProjectSettingsService_pb2_grpc.ProjectSettingsStub(self._client.channel)
        
    def _getEurocodeParametersProperties(self) -> ProjectSettingsService_pb2.GetEurocodeParametersResponse:
        request = ProjectSettingsService_pb2.GetEurocodeParametersRequest(session_id=self._client.sessionID, model_id=self._model_id)
        return self._client.callFunction(self._stub.GetEurocodeParameters, request)
    
    def _setEurocodeParametersProperties(self, properties: ProjectSettingsService_pb2.GetEurocodeParametersResponse):
        request = ProjectSettingsService_pb2.SetEurocodeParametersRequest(session_id=self._client.sessionID, model_id=self._model_id, 
                                                                       properties=properties)
        self._client.callFunction(self._stub.SetEurocodeParameters, request)
        
    def getGammaC(self) -> float:
        properties = self._getEurocodeParametersProperties()
        return properties.gamma_c
    
    def setGammaC(self, gammaC: float):
        properties = self._getEurocodeParametersProperties()
        properties.gamma_c = gammaC
        self._setEurocodeParametersProperties(properties)
        
    def getGammaS(self) -> float:
        properties = self._getEurocodeParametersProperties()
        return properties.gamma_s
    
    def setGammaS(self, gammaS: float):
        properties = self._getEurocodeParametersProperties()
        properties.gamma_s = gammaS
        self._setEurocodeParametersProperties(properties)
        
    def getGammaA(self) -> float:
        properties = self._getEurocodeParametersProperties()
        return properties.gamma_a
    
    def setGammaA(self, gammaA: float):
        properties = self._getEurocodeParametersProperties()
        properties.gamma_a = gammaA
        self._setEurocodeParametersProperties(properties)
        
    def getAlphaCC(self) -> float:
        properties = self._getEurocodeParametersProperties()
        return properties.alpha_cc
    
    def setAlphaCC(self, alphaCC: float):
        properties = self._getEurocodeParametersProperties()
        properties.alpha_cc = alphaCC
        self._setEurocodeParametersProperties(properties)
        
    def getAlphaKt(self) -> float:
        properties = self._getEurocodeParametersProperties()
        return properties.alpha_kt
    
    def setAlphaKt(self, alphaKt: float):
        properties = self._getEurocodeParametersProperties()
        properties.alpha_kt = alphaKt
        self._setEurocodeParametersProperties(properties)
        
    def getAlphaKf(self) -> float:
        properties = self._getEurocodeParametersProperties()
        return properties.alpha_kf
    
    def setAlphaKf(self, alphaKf: float):
        properties = self._getEurocodeParametersProperties()
        properties.alpha_kf = alphaKf
        self._setEurocodeParametersProperties(properties)
        
    def getUseReducedSection(self) -> bool:
        properties = self._getEurocodeParametersProperties()
        return properties.use_reduced_section
    
    def setUseReducedSection(self, useReducedSection: bool):
        properties = self._getEurocodeParametersProperties()
        properties.use_reduced_section = useReducedSection
        self._setEurocodeParametersProperties(properties)
class InteractionDiagram:
    def __init__(self, client: Client, model_id: str):
        self._client = client
        self._model_id = model_id
        self._stub = ProjectSettingsService_pb2_grpc.ProjectSettingsStub(self._client.channel)
        self.EurocodeParameters = EurocodeParameters(client, model_id)
        
    def _getInteractionDiagramProperties(self) -> ProjectSettingsService_pb2.GetInteractionDiagramResponse:
        request = ProjectSettingsService_pb2.GetInteractionDiagramRequest(session_id=self._client.sessionID, model_id=self._model_id)
        return self._client.callFunction(self._stub.GetInteractionDiagram, request)
    
    def _setInteractionDiagramProperties(self, properties: ProjectSettingsService_pb2.GetInteractionDiagramResponse):
        request = ProjectSettingsService_pb2.SetInteractionDiagramRequest(session_id=self._client.sessionID, model_id=self._model_id, 
                                                                 properties=properties)
        self._client.callFunction(self._stub.SetInteractionDiagram, request)
        
    def getConcreteStressStrainCurveModel(self) -> ConcreteStressStrainCurveModel:
        properties = self._getInteractionDiagramProperties()
        return ConcreteStressStrainCurveModel(properties.concrete_stress_strain_curve_model)
    
    def setConcreteStressStrainCurveModel(self, concreteStressStrainCurveModel: ConcreteStressStrainCurveModel):
        properties = self._getInteractionDiagramProperties()
        properties.concrete_stress_strain_curve_model = concreteStressStrainCurveModel.value
        self._setInteractionDiagramProperties(properties)
        
    def getIsCalculateFactoredInteractionMP(self) -> bool:
        properties = self._getInteractionDiagramProperties()
        return properties.is_calculate_factored_interaction_mp
    
    def setIsCalculateFactoredInteractionMP(self, isCalculateFactoredInteractionMP: bool):
        properties = self._getInteractionDiagramProperties()
        properties.is_calculate_factored_interaction_mp = isCalculateFactoredInteractionMP
        self._setInteractionDiagramProperties(properties)
        
    def getDesignStandard(self) -> DesignStandard:
        """Only available if IsCalculateFactoredInteractionMP is enabled"""
        properties = self._getInteractionDiagramProperties()
        return DesignStandard(properties.design_standard)
    
    def setDesignStandard(self, designStandard: DesignStandard):
        """Only available if IsCalculateFactoredInteractionMP is enabled"""
        properties = self._getInteractionDiagramProperties()
        properties.design_standard = designStandard.value
        self._setInteractionDiagramProperties(properties)
        
    def getSingleFactorForMAndP(self) -> float:
        """Only available if SINGLE_FACTOR_FOR_M_AND_P is selected as the Design Standard"""
        properties = self._getInteractionDiagramProperties()
        return properties.single_factor_for_m_and_p
    
    def setSingleFactorForMAndP(self, singleFactorForMAndP: float):
        """Only available if SINGLE_FACTOR_FOR_M_AND_P is selected as the Design Standard"""
        properties = self._getInteractionDiagramProperties()
        properties.single_factor_for_m_and_p = singleFactorForMAndP
        self._setInteractionDiagramProperties(properties)
        
    def getIsCalculateCapacityRatioAnd3DInteractionSurfaces(self) -> bool:
        """Only available if IsCalculateFactoredInteractionMP is enabled"""
        properties = self._getInteractionDiagramProperties()
        return properties.is_calculate_capacity_ratio_and_3d_interaction_surfaces
    
    def setIsCalculateCapacityRatioAnd3DInteractionSurfaces(self, isCalculateCapacityRatioAnd3DInteractionSurfaces: bool):
        """Only available if IsCalculateFactoredInteractionMP is enabled"""
        properties = self._getInteractionDiagramProperties()
        properties.is_calculate_capacity_ratio_and_3d_interaction_surfaces = isCalculateCapacityRatioAnd3DInteractionSurfaces
        self._setInteractionDiagramProperties(properties)
        
    def getNumberOfLoadDivisions(self) -> int:
        """Only available if Calculate Capacity Ratio and 3D Interaction Surfaces is enabled
        should be between [10,500]
        """
        properties = self._getInteractionDiagramProperties()
        return properties.number_of_load_divisions
    
    def setNumberOfLoadDivisions(self, numberOfLoadDivisions: int):
        """Only available if Calculate Capacity Ratio and 3D Interaction Surfaces is enabled
        should be between [10,500]
        """
        properties = self._getInteractionDiagramProperties()
        properties.number_of_load_divisions = numberOfLoadDivisions
        self._setInteractionDiagramProperties(properties)
        
    def getNumberOfAngleDivisions(self) -> int:
        """Only available if Calculate Capacity Ratio and 3D Interaction Surfaces is enabled
        Should be between [18,360)
        """
        properties = self._getInteractionDiagramProperties()
        return properties.number_of_angle_divisions
    
    def setNumberOfAngleDivisions(self, numberOfAngleDivisions: int):
        """Only available if Calculate Capacity Ratio and 3D Interaction Surfaces is enabled
        Should be between [18,360)
        """
        properties = self._getInteractionDiagramProperties()
        properties.number_of_angle_divisions = numberOfAngleDivisions
        self._setInteractionDiagramProperties(properties)