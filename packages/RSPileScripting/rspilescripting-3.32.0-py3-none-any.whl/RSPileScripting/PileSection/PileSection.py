from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.GenericPileService_pb2 as GenericPileService_pb2
import RSPileScripting.generated_python_files.pile_section_services.GenericPileService_pb2_grpc as GenericPileService_pb2_grpc
from RSPileScripting.PileSection.PileAnalysis import PileAnalysis
from RSPileScripting.PileSection.BoredCapacity import BoredCapacity
from RSPileScripting.PileSection.DrivenCapacity import DrivenCapacity
from RSPileScripting.PileSection.HelicalCapacity import HelicalCapacity

class PileSection:
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._pile_id = pile_id
		self._client = client
		self._model_id = model_id
		self._stub = GenericPileService_pb2_grpc.GenericPileServiceStub(self._client.channel)
		self.PileAnalysis = PileAnalysis(self._model_id, self._pile_id, self._client)
		self.BoredCapacity = BoredCapacity(self._model_id, self._pile_id, self._client)
		self.DrivenCapacity = DrivenCapacity(self._model_id, self._pile_id, self._client)
		self.HelicalCapacity = HelicalCapacity(self._model_id, self._pile_id, self._client)

	def _getGenericPileProperties(self) -> GenericPileService_pb2.GenericPileProperties:
		request = GenericPileService_pb2.GetGenericPilePropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetGenericPileProperties, request)
		return response.generic_pile_props

	def _setGenericPileProperties(self, pileProps: GenericPileService_pb2.GenericPileProperties):
		request = GenericPileService_pb2.SetGenericPilePropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			generic_pile_props=pileProps)
		self._client.callFunction(self._stub.SetGenericPileProperties, request)

	def getName(self):
		properties = self._getGenericPileProperties()
		return properties.pile_name
	
	def setName(self, name):
		properties = self._getGenericPileProperties()
		properties.pile_name = name
		self._setGenericPileProperties(properties)

	def getColor(self):
		properties = self._getGenericPileProperties()
		return properties.pile_color

	def setColor(self, color):
		properties = self._getGenericPileProperties()
		properties.pile_color = color
		self._setGenericPileProperties(properties)