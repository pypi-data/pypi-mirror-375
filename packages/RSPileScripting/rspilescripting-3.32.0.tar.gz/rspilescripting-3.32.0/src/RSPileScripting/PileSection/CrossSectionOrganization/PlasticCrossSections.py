from RSPileScripting._client import Client
from RSPileScripting.PileSection.CrossSectionTypes.PileAnalysis.Rectangular import Rectangular
from RSPileScripting.PileSection.CrossSectionTypes.PileAnalysis.Circular import Circular
from RSPileScripting.PileSection.CrossSectionTypes.PileAnalysis.Pipe import Pipe

class PlasticCrossSections:
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self.Rectangular = Rectangular(self._model_id, self._pile_id, self._client)
		self.Circular = Circular(self._model_id, self._pile_id, self._client)
		self.Pipe = Pipe(self._model_id, self._pile_id, self._client)