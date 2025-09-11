from RSPileScripting._client import Client
from RSPileScripting.PileType.Sections.BoredSections import BoredSections as Sections

class BoredPileType:
    def __init__(self, model_id: str, pile_type_id: str, client: Client):
        self._pile_type_id = pile_type_id
        self._client = client
        self._model_id = model_id     
        self.Sections = Sections(self._model_id, self._pile_type_id, self._client)