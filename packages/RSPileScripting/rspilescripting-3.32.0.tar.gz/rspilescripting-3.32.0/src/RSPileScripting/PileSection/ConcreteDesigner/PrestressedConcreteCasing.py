from RSPileScripting.generated_python_files.pile_section_services import PrestressedConcreteDesignerCasingService_pb2_grpc as CasingService_pb2_grpc
from RSPileScripting.PileSection.ConcreteDesigner.CasingBaseClass import CasingBaseClass

class PrestressedConcreteCasing(CasingBaseClass):
	def _create_stub(self):
		return CasingService_pb2_grpc.PrestressedConcreteDesignerCasingServiceStub(self._client.channel)

