from RSPileScripting._client import Client
from RSPileScripting.PileSection.ConcreteDesigner.PrestressedConcreteCasing import PrestressedConcreteCasing as Casing
from RSPileScripting.PileSection.ConcreteDesigner.PrestressedConcreteReinforcement import PrestressedConcreteReinforcement as Reinforcement
from RSPileScripting.PileSection.ConcreteDesigner.PrestressedConcreteCore import PrestressedConcreteCore as Core

class PrestressedConcreteDesigner:
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self.Casing = Casing(self._model_id, self._pile_id, self._client)
		self.Reinforcement = Reinforcement(self._model_id, self._pile_id, self._client)
		self.Core = Core(self._model_id, self._pile_id, self._client)