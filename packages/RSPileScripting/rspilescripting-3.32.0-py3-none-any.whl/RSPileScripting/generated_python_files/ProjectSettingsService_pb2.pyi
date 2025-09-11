from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Units(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNITS_UNSPECIFIED: _ClassVar[Units]
    SI_METRIC: _ClassVar[Units]
    USCS_IMPERIAL: _ClassVar[Units]

class ProgramModeSelection(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PROGRAM_MODE_SELECTION_UNSPECIFIED: _ClassVar[ProgramModeSelection]
    PILE_ANALYSIS: _ClassVar[ProgramModeSelection]
    CAPACITY_CALCULATIONS: _ClassVar[ProgramModeSelection]

class CapacityCalculationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CAPACITY_CALCULATION_TYPE_UNSPECIFIED: _ClassVar[CapacityCalculationType]
    DRIVEN: _ClassVar[CapacityCalculationType]
    BORED: _ClassVar[CapacityCalculationType]
    HELICAL: _ClassVar[CapacityCalculationType]
    CAPACITY_TABLE_GENERATOR: _ClassVar[CapacityCalculationType]

class IndividualPileAnalysisType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INDIVIDUAL_PILE_ANALYSIS_TYPE_UNSPECIFIED: _ClassVar[IndividualPileAnalysisType]
    AXIALLY_LOADED: _ClassVar[IndividualPileAnalysisType]
    LATERALLY_LOADED: _ClassVar[IndividualPileAnalysisType]
    AXIALLY_LATERALLY_LOADED: _ClassVar[IndividualPileAnalysisType]

class PileAnalysisType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PILE_ANALYSIS_TYPE_UNSPECIFIED: _ClassVar[PileAnalysisType]
    INDIVIDUAL_PILE_ANALYSIS: _ClassVar[PileAnalysisType]
    GROUPED_PILE_ANALYSIS: _ClassVar[PileAnalysisType]

class GroundwaterMethod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GROUNDWATER_METHOD_UNSPECIFIED: _ClassVar[GroundwaterMethod]
    PIEZOMETRIC_LINE: _ClassVar[GroundwaterMethod]
    GRID: _ClassVar[GroundwaterMethod]

class ConcreteStressStrainCurveModel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONCRETE_STRESS_STRAIN_CURVE_MODEL_UNSPECIFIED: _ClassVar[ConcreteStressStrainCurveModel]
    INTERACTION_DIAGRAM_MODIFIED_HOGNESTAD: _ClassVar[ConcreteStressStrainCurveModel]
    INTERACTION_DIAGRAM_WHITNEY_BLOCK: _ClassVar[ConcreteStressStrainCurveModel]
    INTERACTION_DIAGRAM_EC2_BILINEAR: _ClassVar[ConcreteStressStrainCurveModel]
    INTERACTION_DIAGRAM_EC2_PARABOLA: _ClassVar[ConcreteStressStrainCurveModel]
    INTERACTION_DIAGRAM_EC2_RECTANGULAR_BLOCK: _ClassVar[ConcreteStressStrainCurveModel]

class DesignStandard(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DESIGN_STANDARD_UNSPECIFIED: _ClassVar[DesignStandard]
    SINGLE_FACTOR_FOR_M_AND_P: _ClassVar[DesignStandard]
    ACI_318_FACTORS_2022: _ClassVar[DesignStandard]
    EUROCODE_FACTORS_EC2_2004: _ClassVar[DesignStandard]

class PileDiscretization(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PILE_DISCRETIZATION_UNSPECIFIED: _ClassVar[PileDiscretization]
    AUTO: _ClassVar[PileDiscretization]
    CUSTOM: _ClassVar[PileDiscretization]
UNITS_UNSPECIFIED: Units
SI_METRIC: Units
USCS_IMPERIAL: Units
PROGRAM_MODE_SELECTION_UNSPECIFIED: ProgramModeSelection
PILE_ANALYSIS: ProgramModeSelection
CAPACITY_CALCULATIONS: ProgramModeSelection
CAPACITY_CALCULATION_TYPE_UNSPECIFIED: CapacityCalculationType
DRIVEN: CapacityCalculationType
BORED: CapacityCalculationType
HELICAL: CapacityCalculationType
CAPACITY_TABLE_GENERATOR: CapacityCalculationType
INDIVIDUAL_PILE_ANALYSIS_TYPE_UNSPECIFIED: IndividualPileAnalysisType
AXIALLY_LOADED: IndividualPileAnalysisType
LATERALLY_LOADED: IndividualPileAnalysisType
AXIALLY_LATERALLY_LOADED: IndividualPileAnalysisType
PILE_ANALYSIS_TYPE_UNSPECIFIED: PileAnalysisType
INDIVIDUAL_PILE_ANALYSIS: PileAnalysisType
GROUPED_PILE_ANALYSIS: PileAnalysisType
GROUNDWATER_METHOD_UNSPECIFIED: GroundwaterMethod
PIEZOMETRIC_LINE: GroundwaterMethod
GRID: GroundwaterMethod
CONCRETE_STRESS_STRAIN_CURVE_MODEL_UNSPECIFIED: ConcreteStressStrainCurveModel
INTERACTION_DIAGRAM_MODIFIED_HOGNESTAD: ConcreteStressStrainCurveModel
INTERACTION_DIAGRAM_WHITNEY_BLOCK: ConcreteStressStrainCurveModel
INTERACTION_DIAGRAM_EC2_BILINEAR: ConcreteStressStrainCurveModel
INTERACTION_DIAGRAM_EC2_PARABOLA: ConcreteStressStrainCurveModel
INTERACTION_DIAGRAM_EC2_RECTANGULAR_BLOCK: ConcreteStressStrainCurveModel
DESIGN_STANDARD_UNSPECIFIED: DesignStandard
SINGLE_FACTOR_FOR_M_AND_P: DesignStandard
ACI_318_FACTORS_2022: DesignStandard
EUROCODE_FACTORS_EC2_2004: DesignStandard
PILE_DISCRETIZATION_UNSPECIFIED: PileDiscretization
AUTO: PileDiscretization
CUSTOM: PileDiscretization

class GetUnitsRequest(_message.Message):
    __slots__ = ("session_id", "model_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ...) -> None: ...

class GetUnitsResponse(_message.Message):
    __slots__ = ("units",)
    UNITS_FIELD_NUMBER: _ClassVar[int]
    units: Units
    def __init__(self, units: _Optional[_Union[Units, str]] = ...) -> None: ...

class SetUnitsRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "units", "reset_values")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    UNITS_FIELD_NUMBER: _ClassVar[int]
    RESET_VALUES_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    units: Units
    reset_values: bool
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., units: _Optional[_Union[Units, str]] = ..., reset_values: bool = ...) -> None: ...

class SetUnitsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetProgramModeRequest(_message.Message):
    __slots__ = ("session_id", "model_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ...) -> None: ...

class GetProgramModeResponse(_message.Message):
    __slots__ = ("program_mode",)
    PROGRAM_MODE_FIELD_NUMBER: _ClassVar[int]
    program_mode: ProgramModeSelection
    def __init__(self, program_mode: _Optional[_Union[ProgramModeSelection, str]] = ...) -> None: ...

class SetProgramModeRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "program_mode")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PROGRAM_MODE_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    program_mode: ProgramModeSelection
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., program_mode: _Optional[_Union[ProgramModeSelection, str]] = ...) -> None: ...

class SetProgramModeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetCapacityCalculationTypeRequest(_message.Message):
    __slots__ = ("session_id", "model_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ...) -> None: ...

class GetCapacityCalculationTypeResponse(_message.Message):
    __slots__ = ("capacity_calculation_type",)
    CAPACITY_CALCULATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    capacity_calculation_type: CapacityCalculationType
    def __init__(self, capacity_calculation_type: _Optional[_Union[CapacityCalculationType, str]] = ...) -> None: ...

class SetCapacityCalculationTypeRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "capacity_calculation_type")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    CAPACITY_CALCULATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    capacity_calculation_type: CapacityCalculationType
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., capacity_calculation_type: _Optional[_Union[CapacityCalculationType, str]] = ...) -> None: ...

class SetCapacityCalculationTypeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetCalculateAllowableCapacitiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ...) -> None: ...

class GetCalculateAllowableCapacitiesResponse(_message.Message):
    __slots__ = ("is_total_capacity", "is_skin_friction", "is_skin_friction_end_bearing", "fs1", "fs2", "fs3", "fs4")
    IS_TOTAL_CAPACITY_FIELD_NUMBER: _ClassVar[int]
    IS_SKIN_FRICTION_FIELD_NUMBER: _ClassVar[int]
    IS_SKIN_FRICTION_END_BEARING_FIELD_NUMBER: _ClassVar[int]
    FS1_FIELD_NUMBER: _ClassVar[int]
    FS2_FIELD_NUMBER: _ClassVar[int]
    FS3_FIELD_NUMBER: _ClassVar[int]
    FS4_FIELD_NUMBER: _ClassVar[int]
    is_total_capacity: bool
    is_skin_friction: bool
    is_skin_friction_end_bearing: bool
    fs1: float
    fs2: float
    fs3: float
    fs4: float
    def __init__(self, is_total_capacity: bool = ..., is_skin_friction: bool = ..., is_skin_friction_end_bearing: bool = ..., fs1: _Optional[float] = ..., fs2: _Optional[float] = ..., fs3: _Optional[float] = ..., fs4: _Optional[float] = ...) -> None: ...

class SetCalculateAllowableCapacitiesRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "is_total_capacity", "is_skin_friction", "is_skin_friction_end_bearing", "fs1", "fs2", "fs3", "fs4")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    IS_TOTAL_CAPACITY_FIELD_NUMBER: _ClassVar[int]
    IS_SKIN_FRICTION_FIELD_NUMBER: _ClassVar[int]
    IS_SKIN_FRICTION_END_BEARING_FIELD_NUMBER: _ClassVar[int]
    FS1_FIELD_NUMBER: _ClassVar[int]
    FS2_FIELD_NUMBER: _ClassVar[int]
    FS3_FIELD_NUMBER: _ClassVar[int]
    FS4_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    is_total_capacity: bool
    is_skin_friction: bool
    is_skin_friction_end_bearing: bool
    fs1: float
    fs2: float
    fs3: float
    fs4: float
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., is_total_capacity: bool = ..., is_skin_friction: bool = ..., is_skin_friction_end_bearing: bool = ..., fs1: _Optional[float] = ..., fs2: _Optional[float] = ..., fs3: _Optional[float] = ..., fs4: _Optional[float] = ...) -> None: ...

class SetCalculateAllowableCapacitiesResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetLimitAverageStressRequest(_message.Message):
    __slots__ = ("session_id", "model_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ...) -> None: ...

class GetLimitAverageStressResponse(_message.Message):
    __slots__ = ("limit_average_stress",)
    LIMIT_AVERAGE_STRESS_FIELD_NUMBER: _ClassVar[int]
    limit_average_stress: bool
    def __init__(self, limit_average_stress: bool = ...) -> None: ...

class SetLimitAverageStressRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "limit_average_stress")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    LIMIT_AVERAGE_STRESS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    limit_average_stress: bool
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., limit_average_stress: bool = ...) -> None: ...

class SetLimitAverageStressResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetHelicalOptionsRequest(_message.Message):
    __slots__ = ("session_id", "model_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ...) -> None: ...

class GetHelicalOptionsResponse(_message.Message):
    __slots__ = ("is_include_shaft_adhesion_friction", "is_apply_local_shear_failure_for_helices", "is_use_reduced_helix_area_for_end_bearing", "is_include_shape_and_depth_factors")
    IS_INCLUDE_SHAFT_ADHESION_FRICTION_FIELD_NUMBER: _ClassVar[int]
    IS_APPLY_LOCAL_SHEAR_FAILURE_FOR_HELICES_FIELD_NUMBER: _ClassVar[int]
    IS_USE_REDUCED_HELIX_AREA_FOR_END_BEARING_FIELD_NUMBER: _ClassVar[int]
    IS_INCLUDE_SHAPE_AND_DEPTH_FACTORS_FIELD_NUMBER: _ClassVar[int]
    is_include_shaft_adhesion_friction: bool
    is_apply_local_shear_failure_for_helices: bool
    is_use_reduced_helix_area_for_end_bearing: bool
    is_include_shape_and_depth_factors: bool
    def __init__(self, is_include_shaft_adhesion_friction: bool = ..., is_apply_local_shear_failure_for_helices: bool = ..., is_use_reduced_helix_area_for_end_bearing: bool = ..., is_include_shape_and_depth_factors: bool = ...) -> None: ...

class SetHelicalOptionsRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "is_include_shaft_adhesion_friction", "is_apply_local_shear_failure_for_helices", "is_use_reduced_helix_area_for_end_bearing", "is_include_shape_and_depth_factors")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    IS_INCLUDE_SHAFT_ADHESION_FRICTION_FIELD_NUMBER: _ClassVar[int]
    IS_APPLY_LOCAL_SHEAR_FAILURE_FOR_HELICES_FIELD_NUMBER: _ClassVar[int]
    IS_USE_REDUCED_HELIX_AREA_FOR_END_BEARING_FIELD_NUMBER: _ClassVar[int]
    IS_INCLUDE_SHAPE_AND_DEPTH_FACTORS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    is_include_shaft_adhesion_friction: bool
    is_apply_local_shear_failure_for_helices: bool
    is_use_reduced_helix_area_for_end_bearing: bool
    is_include_shape_and_depth_factors: bool
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., is_include_shaft_adhesion_friction: bool = ..., is_apply_local_shear_failure_for_helices: bool = ..., is_use_reduced_helix_area_for_end_bearing: bool = ..., is_include_shape_and_depth_factors: bool = ...) -> None: ...

class SetHelicalOptionsResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetPileAnalysisTypeRequest(_message.Message):
    __slots__ = ("session_id", "model_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ...) -> None: ...

class GetPileAnalysisTypeResponse(_message.Message):
    __slots__ = ("pile_analysis_type", "individual_pile_analysis_type", "is_multiple_load_cases", "is_include_p_delta_effects")
    PILE_ANALYSIS_TYPE_FIELD_NUMBER: _ClassVar[int]
    INDIVIDUAL_PILE_ANALYSIS_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_MULTIPLE_LOAD_CASES_FIELD_NUMBER: _ClassVar[int]
    IS_INCLUDE_P_DELTA_EFFECTS_FIELD_NUMBER: _ClassVar[int]
    pile_analysis_type: PileAnalysisType
    individual_pile_analysis_type: IndividualPileAnalysisType
    is_multiple_load_cases: bool
    is_include_p_delta_effects: bool
    def __init__(self, pile_analysis_type: _Optional[_Union[PileAnalysisType, str]] = ..., individual_pile_analysis_type: _Optional[_Union[IndividualPileAnalysisType, str]] = ..., is_multiple_load_cases: bool = ..., is_include_p_delta_effects: bool = ...) -> None: ...

class SetPileAnalysisTypeRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_analysis_type", "individual_pile_analysis_type", "is_multiple_load_cases", "is_include_p_delta_effects")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_ANALYSIS_TYPE_FIELD_NUMBER: _ClassVar[int]
    INDIVIDUAL_PILE_ANALYSIS_TYPE_FIELD_NUMBER: _ClassVar[int]
    IS_MULTIPLE_LOAD_CASES_FIELD_NUMBER: _ClassVar[int]
    IS_INCLUDE_P_DELTA_EFFECTS_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_analysis_type: PileAnalysisType
    individual_pile_analysis_type: IndividualPileAnalysisType
    is_multiple_load_cases: bool
    is_include_p_delta_effects: bool
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_analysis_type: _Optional[_Union[PileAnalysisType, str]] = ..., individual_pile_analysis_type: _Optional[_Union[IndividualPileAnalysisType, str]] = ..., is_multiple_load_cases: bool = ..., is_include_p_delta_effects: bool = ...) -> None: ...

class SetPileAnalysisTypeResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetGroundwaterRequest(_message.Message):
    __slots__ = ("session_id", "model_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ...) -> None: ...

class GetGroundwaterResponse(_message.Message):
    __slots__ = ("is_groundwater_analysis", "groundwater_method", "water_unit_weight")
    IS_GROUNDWATER_ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    GROUNDWATER_METHOD_FIELD_NUMBER: _ClassVar[int]
    WATER_UNIT_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    is_groundwater_analysis: bool
    groundwater_method: GroundwaterMethod
    water_unit_weight: float
    def __init__(self, is_groundwater_analysis: bool = ..., groundwater_method: _Optional[_Union[GroundwaterMethod, str]] = ..., water_unit_weight: _Optional[float] = ...) -> None: ...

class SetGroundwaterRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "is_groundwater_analysis", "groundwater_method", "water_unit_weight")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    IS_GROUNDWATER_ANALYSIS_FIELD_NUMBER: _ClassVar[int]
    GROUNDWATER_METHOD_FIELD_NUMBER: _ClassVar[int]
    WATER_UNIT_WEIGHT_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    is_groundwater_analysis: bool
    groundwater_method: GroundwaterMethod
    water_unit_weight: float
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., is_groundwater_analysis: bool = ..., groundwater_method: _Optional[_Union[GroundwaterMethod, str]] = ..., water_unit_weight: _Optional[float] = ...) -> None: ...

class SetGroundwaterResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetEurocodeParametersRequest(_message.Message):
    __slots__ = ("session_id", "model_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ...) -> None: ...

class GetEurocodeParametersResponse(_message.Message):
    __slots__ = ("gamma_c", "gamma_s", "gamma_a", "alpha_cc", "alpha_kt", "alpha_kf", "use_reduced_section")
    GAMMA_C_FIELD_NUMBER: _ClassVar[int]
    GAMMA_S_FIELD_NUMBER: _ClassVar[int]
    GAMMA_A_FIELD_NUMBER: _ClassVar[int]
    ALPHA_CC_FIELD_NUMBER: _ClassVar[int]
    ALPHA_KT_FIELD_NUMBER: _ClassVar[int]
    ALPHA_KF_FIELD_NUMBER: _ClassVar[int]
    USE_REDUCED_SECTION_FIELD_NUMBER: _ClassVar[int]
    gamma_c: float
    gamma_s: float
    gamma_a: float
    alpha_cc: float
    alpha_kt: float
    alpha_kf: float
    use_reduced_section: bool
    def __init__(self, gamma_c: _Optional[float] = ..., gamma_s: _Optional[float] = ..., gamma_a: _Optional[float] = ..., alpha_cc: _Optional[float] = ..., alpha_kt: _Optional[float] = ..., alpha_kf: _Optional[float] = ..., use_reduced_section: bool = ...) -> None: ...

class SetEurocodeParametersRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "properties")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    properties: GetEurocodeParametersResponse
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., properties: _Optional[_Union[GetEurocodeParametersResponse, _Mapping]] = ...) -> None: ...

class SetEurocodeParametersResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetInteractionDiagramRequest(_message.Message):
    __slots__ = ("session_id", "model_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ...) -> None: ...

class GetInteractionDiagramResponse(_message.Message):
    __slots__ = ("concrete_stress_strain_curve_model", "is_calculate_factored_interaction_mp", "design_standard", "single_factor_for_m_and_p", "is_calculate_capacity_ratio_and_3d_interaction_surfaces", "number_of_load_divisions", "number_of_angle_divisions")
    CONCRETE_STRESS_STRAIN_CURVE_MODEL_FIELD_NUMBER: _ClassVar[int]
    IS_CALCULATE_FACTORED_INTERACTION_MP_FIELD_NUMBER: _ClassVar[int]
    DESIGN_STANDARD_FIELD_NUMBER: _ClassVar[int]
    SINGLE_FACTOR_FOR_M_AND_P_FIELD_NUMBER: _ClassVar[int]
    IS_CALCULATE_CAPACITY_RATIO_AND_3D_INTERACTION_SURFACES_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_LOAD_DIVISIONS_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_ANGLE_DIVISIONS_FIELD_NUMBER: _ClassVar[int]
    concrete_stress_strain_curve_model: ConcreteStressStrainCurveModel
    is_calculate_factored_interaction_mp: bool
    design_standard: DesignStandard
    single_factor_for_m_and_p: float
    is_calculate_capacity_ratio_and_3d_interaction_surfaces: bool
    number_of_load_divisions: int
    number_of_angle_divisions: int
    def __init__(self, concrete_stress_strain_curve_model: _Optional[_Union[ConcreteStressStrainCurveModel, str]] = ..., is_calculate_factored_interaction_mp: bool = ..., design_standard: _Optional[_Union[DesignStandard, str]] = ..., single_factor_for_m_and_p: _Optional[float] = ..., is_calculate_capacity_ratio_and_3d_interaction_surfaces: bool = ..., number_of_load_divisions: _Optional[int] = ..., number_of_angle_divisions: _Optional[int] = ...) -> None: ...

class SetInteractionDiagramRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "properties")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    properties: GetInteractionDiagramResponse
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., properties: _Optional[_Union[GetInteractionDiagramResponse, _Mapping]] = ...) -> None: ...

class SetInteractionDiagramResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class GetAdvancedRequest(_message.Message):
    __slots__ = ("session_id", "model_id")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ...) -> None: ...

class GetAdvancedResponse(_message.Message):
    __slots__ = ("pile_discretization", "pile_depth_increment", "pile_segments", "convergence_tolerance", "number_of_iterations", "reinforced_concrete_slices", "use_method_of_gergiadis_layering_effect")
    PILE_DISCRETIZATION_FIELD_NUMBER: _ClassVar[int]
    PILE_DEPTH_INCREMENT_FIELD_NUMBER: _ClassVar[int]
    PILE_SEGMENTS_FIELD_NUMBER: _ClassVar[int]
    CONVERGENCE_TOLERANCE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_ITERATIONS_FIELD_NUMBER: _ClassVar[int]
    REINFORCED_CONCRETE_SLICES_FIELD_NUMBER: _ClassVar[int]
    USE_METHOD_OF_GERGIADIS_LAYERING_EFFECT_FIELD_NUMBER: _ClassVar[int]
    pile_discretization: PileDiscretization
    pile_depth_increment: float
    pile_segments: int
    convergence_tolerance: float
    number_of_iterations: int
    reinforced_concrete_slices: int
    use_method_of_gergiadis_layering_effect: bool
    def __init__(self, pile_discretization: _Optional[_Union[PileDiscretization, str]] = ..., pile_depth_increment: _Optional[float] = ..., pile_segments: _Optional[int] = ..., convergence_tolerance: _Optional[float] = ..., number_of_iterations: _Optional[int] = ..., reinforced_concrete_slices: _Optional[int] = ..., use_method_of_gergiadis_layering_effect: bool = ...) -> None: ...

class SetAdvancedRequest(_message.Message):
    __slots__ = ("session_id", "model_id", "pile_discretization", "pile_depth_increment", "pile_segments", "convergence_tolerance", "number_of_iterations", "reinforced_concrete_slices", "use_method_of_gergiadis_layering_effect")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    PILE_DISCRETIZATION_FIELD_NUMBER: _ClassVar[int]
    PILE_DEPTH_INCREMENT_FIELD_NUMBER: _ClassVar[int]
    PILE_SEGMENTS_FIELD_NUMBER: _ClassVar[int]
    CONVERGENCE_TOLERANCE_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_ITERATIONS_FIELD_NUMBER: _ClassVar[int]
    REINFORCED_CONCRETE_SLICES_FIELD_NUMBER: _ClassVar[int]
    USE_METHOD_OF_GERGIADIS_LAYERING_EFFECT_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    model_id: str
    pile_discretization: PileDiscretization
    pile_depth_increment: float
    pile_segments: int
    convergence_tolerance: float
    number_of_iterations: int
    reinforced_concrete_slices: int
    use_method_of_gergiadis_layering_effect: bool
    def __init__(self, session_id: _Optional[str] = ..., model_id: _Optional[str] = ..., pile_discretization: _Optional[_Union[PileDiscretization, str]] = ..., pile_depth_increment: _Optional[float] = ..., pile_segments: _Optional[int] = ..., convergence_tolerance: _Optional[float] = ..., number_of_iterations: _Optional[int] = ..., reinforced_concrete_slices: _Optional[int] = ..., use_method_of_gergiadis_layering_effect: bool = ...) -> None: ...

class SetAdvancedResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
