from RSPileScripting._client import Client
from RSPileScripting.PileSection.ConcreteDesigner.IBeam import IBeam
from RSPileScripting.PileSection.ConcreteDesigner.ReinforcedConcreteCasing import ReinforcedConcreteCasing as Casing
from RSPileScripting.PileSection.ConcreteDesigner.ReinforcedConcreteReinforcement import ReinforcedConcreteReinforcement as Reinforcement
from RSPileScripting.PileSection.ConcreteDesigner.ReinforcedConcreteCore import ReinforcedConcreteCore as Core

class ReinforcedConcreteDesigner:
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self.IBeam = IBeam(self._model_id, self._pile_id, self._client)
		self.Casing = Casing(self._model_id, self._pile_id, self._client)
		self.Reinforcement = Reinforcement(self._model_id, self._pile_id, self._client)
		self.Core = Core(self._model_id, self._pile_id, self._client)