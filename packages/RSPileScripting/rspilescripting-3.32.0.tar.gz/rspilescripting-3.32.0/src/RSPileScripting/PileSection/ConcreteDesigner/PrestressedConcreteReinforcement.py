from RSPileScripting._client import Client
from RSPileScripting.PileSection.ConcreteDesigner.ReinforcementBaseClass import ReinforcementBaseClass
from RSPileScripting.PileSection.ConcreteDesigner.PrestressedConcreteReinforcementPattern import PrestressedConcreteReinforcementPattern as ReinforcementPattern
import RSPileScripting.generated_python_files.pile_section_services.PrestressedConcreteDesignerReinforcementService_pb2_grpc as ReinforcementService_pb2_grpc
import RSPileScripting.generated_python_files.pile_section_services.PrestressedConcreteDesignerReinforcementService_pb2 as PrestressedConcreteDesignerReinforcementService_pb2  

class PrestressedConcreteReinforcement(ReinforcementBaseClass[ReinforcementPattern]):
	def _create_stub(self):
		return ReinforcementService_pb2_grpc.PrestressedConcreteDesignerReinforcementServiceStub(self._client.channel)

	def _createReinforcementPattern(self, model_id : str, client : Client, pattern_id: str):
		return ReinforcementPattern(model_id=model_id, pattern_id=pattern_id, client=client)
	
	def _getReinforcementProperties(self) -> PrestressedConcreteDesignerReinforcementService_pb2.ReinforcementProperties:
		request = PrestressedConcreteDesignerReinforcementService_pb2.GetReinforcementPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetReinforcementProperties, request)
		return response.reinforcement_props

	def _setReinforcementProperties(self, reinforcementProps: PrestressedConcreteDesignerReinforcementService_pb2.SetReinforcementPropertiesRequest):
		request = PrestressedConcreteDesignerReinforcementService_pb2.SetReinforcementPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			reinforcement_props=reinforcementProps)
		self._client.callFunction(self._stub.SetReinforcementProperties, request)

	def getForceBeforeLosses(self) -> float:
		properties =  self._getReinforcementProperties()
		return properties.prestress_force_before_losses
	
	def setForceBeforeLosses(self, fractionBeforeLosses: float):
		properties = self._getReinforcementProperties()
		properties.prestress_force_before_losses = fractionBeforeLosses
		self._setReinforcementProperties(properties)

	def getFractionOfLoss(self) -> float:
		properties =  self._getReinforcementProperties()
		return properties.fraction_of_loss_of_prestress
	
	def setFractionOfLoss(self, fractionOfLoss: float):
		properties = self._getReinforcementProperties()
		properties.fraction_of_loss_of_prestress = fractionOfLoss
		self._setReinforcementProperties(properties)