from RSPileScripting._client import Client
from enum import Enum
import RSPileScripting.generated_python_files.ProjectSettingsService_pb2 as ProjectSettingsService_pb2
import RSPileScripting.generated_python_files.ProjectSettingsService_pb2_grpc as ProjectSettingsService_pb2_grpc

class Units(Enum):
    SI_Metric = ProjectSettingsService_pb2.Units.SI_METRIC
    USCS_Imperial = ProjectSettingsService_pb2.Units.USCS_IMPERIAL
    
class ProgramModeSelection(Enum):
    PileAnalysis = ProjectSettingsService_pb2.ProgramModeSelection.PILE_ANALYSIS
    CapacityCalcuations = ProjectSettingsService_pb2.ProgramModeSelection.CAPACITY_CALCULATIONS
    
class General():
    def __init__(self, client: Client, model_id: str):
        self._client = client
        self._model_id = model_id
        self._stub = ProjectSettingsService_pb2_grpc.ProjectSettingsStub(self._client.channel)
        
    def getUnits(self) -> Units:
        request = ProjectSettingsService_pb2.GetUnitsRequest(session_id=self._client.sessionID, model_id=self._model_id)
        response : ProjectSettingsService_pb2.GetUnitsResponse = self._client.callFunction(self._stub.GetUnits, request)
        return Units(response.units)
    
    def setUnits(self, units: Units, resetValues: bool):
        """if resetValues is True, resets all values used throughout the project to their default values for the selected units
        if resetValues is False, only changes the unit system to the selected units, leaving all other values unchanged.
        """
        request = ProjectSettingsService_pb2.SetUnitsRequest(session_id=self._client.sessionID,
                                                             model_id=self._model_id,
                                                             units=units.value, 
                                                             reset_values=resetValues)
        self._client.callFunction(self._stub.SetUnits, request)
    
    def getProgramMode(self) -> ProgramModeSelection:
        request = ProjectSettingsService_pb2.GetProgramModeRequest(session_id=self._client.sessionID,
                                                                   model_id=self._model_id)
        response : ProjectSettingsService_pb2.GetProgramModeResponse = self._client.callFunction(self._stub.GetProgramMode, request)
        return ProgramModeSelection(response.program_mode)
    
    def setProgramMode(self, programModeSelection: ProgramModeSelection):
        """if changed, resets the Capacity Calculations and Pile Analysis settings to their default values"""
        request = ProjectSettingsService_pb2.SetProgramModeRequest(session_id=self._client.sessionID,
                                                                   model_id=self._model_id,
                                                                   program_mode=programModeSelection.value)
        self._client.callFunction(self._stub.SetProgramMode, request)
    
