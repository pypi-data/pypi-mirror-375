from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_type_services.GenericPileTypeService_pb2 as GenericPileTypeService_pb2
import RSPileScripting.generated_python_files.pile_type_services.GenericPileTypeService_pb2_grpc as GenericPileTypeService_pb2_grpc
from RSPileScripting.PileType.AvailablePileTypeOptions.BoredPileType import BoredPileType as Bored
from RSPileScripting.PileType.AvailablePileTypeOptions.DrivenPileType import DrivenPileType as Driven
from RSPileScripting.PileType.AvailablePileTypeOptions.PileAnalysisPileType import PileAnalysisPileType as PileAnalysis
from RSPileScripting.PileType.AvailablePileTypeOptions.HelicalPileType import HelicalPileType as Helical

class PileType:
	"""
	Examples:
	:ref:`pile types pile analysis`
	"""
	def __init__(self, model_id: str, pile_type_id: str, client: Client):
		self._pile_type_id = pile_type_id
		self._client = client
		self._model_id = model_id
		self._stub = GenericPileTypeService_pb2_grpc.GenericPileTypeServiceStub(self._client.channel)
		self.Bored = Bored(self._model_id, self._pile_type_id, self._client)
		self.Driven = Driven(self._model_id, self._pile_type_id, self._client)
		self.PileAnalysis = PileAnalysis(self._model_id, self._pile_type_id, self._client)
		self.Helical = Helical(self._model_id, self._pile_type_id, self._client)

	def _getGenericPileTypeProperties(self) -> GenericPileTypeService_pb2.GenericPileTypeProperties:
		request = GenericPileTypeService_pb2.GetGenericPileTypePropertiesRequest(
			session_id=self._client.sessionID, pile_type_id=self._pile_type_id)
		response = self._client.callFunction(self._stub.GetGenericPileTypeProperties, request)
		return response.generic_pile_type_props

	def _setGenericPileTypeProperties(self, pileTypeProps: GenericPileTypeService_pb2.GenericPileTypeProperties):
		request = GenericPileTypeService_pb2.SetGenericPileTypePropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_type_id=self._pile_type_id, 
			generic_pile_type_props=pileTypeProps)
		self._client.callFunction(self._stub.SetGenericPileTypeProperties, request)

	def getName(self):
		properties = self._getGenericPileTypeProperties()
		return properties.pile_type_name
	
	def setName(self, name):
		properties = self._getGenericPileTypeProperties()
		properties.pile_type_name = name
		self._setGenericPileTypeProperties(properties)

	def getColor(self):
		properties = self._getGenericPileTypeProperties()
		return properties.pile_type_color

	def setColor(self, color):
		properties = self._getGenericPileTypeProperties()
		properties.pile_type_color = color
		self._setGenericPileTypeProperties(properties)