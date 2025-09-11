from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.DrivenCrossSectionConcreteService_pb2 as DrivenCrossSectionConcreteService_pb2
import RSPileScripting.generated_python_files.pile_section_services.DrivenCrossSectionConcreteService_pb2_grpc as DrivenCrossSectionConcreteService_pb2_grpc

class Concrete:
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = DrivenCrossSectionConcreteService_pb2_grpc.DrivenCrossSectionConcreteServiceStub(self._client.channel)

	def _getConcreteProperties(self) -> DrivenCrossSectionConcreteService_pb2.ConcreteProperties:
		request = DrivenCrossSectionConcreteService_pb2.GetConcretePropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetConcreteProperties, request)
		return response.concrete_props

	def _setConcreteProperties(self, concreteProps: DrivenCrossSectionConcreteService_pb2.ConcreteProperties):
		request = DrivenCrossSectionConcreteService_pb2.SetConcretePropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			concrete_props=concreteProps)
		self._client.callFunction(self._stub.SetConcreteProperties, request)

	def getSideOfSquareSection(self) -> float:
		properties = self._getConcreteProperties()
		return properties.side_c
	
	def setSideOfSquareSection(self, sideOfSquareSection: float):
		properties = self._getConcreteProperties()
		properties.side_c = sideOfSquareSection
		self._setConcreteProperties(properties)