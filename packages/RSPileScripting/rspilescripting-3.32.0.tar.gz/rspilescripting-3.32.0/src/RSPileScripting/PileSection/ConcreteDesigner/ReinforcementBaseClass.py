from RSPileScripting._client import Client
from RSPileScripting.PileSection.ConcreteDesigner.ReinforcementPatternBaseClass import ReinforcementPatternBaseClass
import RSPileScripting.generated_python_files.pile_section_services.CommonReinforcement_pb2 as CommonReinforcement_pb2
from typing import TypeVar, Generic, List
from abc import ABC, abstractmethod

T = TypeVar("T", bound=ReinforcementPatternBaseClass)
class ReinforcementBaseClass(ABC, Generic[T]):
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = self._create_stub()

	@abstractmethod
	def _create_stub(self):
		pass
	
	@abstractmethod
	def _createReinforcementPattern(self, model_id : str, client : Client, pattern_id: str):
		pass

	def getReinforcementPatterns(self) -> List[T]:
		getNumberOfReinforcementPatternsResponse: CommonReinforcement_pb2.GetNumberOfReinforcementPatternsResponse = \
			self._client.callFunction(self._stub.GetNumberOfReinforcementPatterns, CommonReinforcement_pb2.GetNumberOfReinforcementPatternsRequest(session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id))
		reinforcementPatternList = []
		for index in range(0, getNumberOfReinforcementPatternsResponse.number_of_reinforcement_patterns):
			response = self._client.callFunction(self._stub.GetReinforcementPattern, CommonReinforcement_pb2.GetReinforcementPatternRequest(session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, pattern_index=index))
			reinforcementPatternList.append(self._createReinforcementPattern(model_id=self._model_id, pattern_id=response.pattern_id, client=self._client))
		return reinforcementPatternList

	def addReinforcementPattern(self, name: str):
		request = CommonReinforcement_pb2.AddReinforcementPatternRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, name=name)
		self._client.callFunction(self._stub.AddReinforcementPattern, request)

	def removeReinforcementPattern(self, name: str):
		request = CommonReinforcement_pb2.RemoveReinforcementPatternRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, name=name)
		self._client.callFunction(self._stub.RemoveReinforcementPattern, request)