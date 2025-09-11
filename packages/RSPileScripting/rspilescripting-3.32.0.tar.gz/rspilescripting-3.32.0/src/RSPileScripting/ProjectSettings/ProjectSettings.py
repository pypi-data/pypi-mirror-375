from RSPileScripting._client import Client
from RSPileScripting.ProjectSettings.General import General
from RSPileScripting.ProjectSettings.CapacityCalculations import CapacityCalculations
from RSPileScripting.ProjectSettings.PileAnalysisTypeSettings import PileAnalysisTypeSettings
from RSPileScripting.ProjectSettings.Groundwater import Groundwater
from RSPileScripting.ProjectSettings.InteractionDiagram import InteractionDiagram
from RSPileScripting.ProjectSettings.Advanced import Advanced

class ProjectSettings():
    def __init__(self, client: Client, model_id: str):
        self._client = client
        self.General = General(client, model_id)
        self.CapacityCalculations = CapacityCalculations(client, model_id)
        self.PileAnalysisTypeSettings = PileAnalysisTypeSettings(client, model_id)
        self.Groundwater = Groundwater(client, model_id)
        self.InteractionDiagram = InteractionDiagram(client, model_id)
        self.Advanced = Advanced(client, model_id)