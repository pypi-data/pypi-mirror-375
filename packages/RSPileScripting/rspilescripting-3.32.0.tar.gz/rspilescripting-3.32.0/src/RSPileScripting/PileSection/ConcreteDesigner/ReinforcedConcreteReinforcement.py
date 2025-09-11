from RSPileScripting._client import Client
from RSPileScripting.PileSection.ConcreteDesigner.ReinforcedConcreteReinforcementPattern import ReinforcedConcreteReinforcementPattern as ReinforcementPattern
import RSPileScripting.generated_python_files.pile_section_services.ReinforcedConcreteDesignerReinforcementService_pb2_grpc as ReinforcementService_pb2_grpc
from RSPileScripting.PileSection.ConcreteDesigner.ReinforcementBaseClass import ReinforcementBaseClass

class ReinforcedConcreteReinforcement(ReinforcementBaseClass[ReinforcementPattern]):
		def _create_stub(self):
			return ReinforcementService_pb2_grpc.ReinforcedConcreteDesignerReinforcementServiceStub(self._client.channel)
		
		def _createReinforcementPattern(self, model_id : str, client : Client, pattern_id: str):
			return ReinforcementPattern(model_id=model_id, pattern_id=pattern_id, client=client)