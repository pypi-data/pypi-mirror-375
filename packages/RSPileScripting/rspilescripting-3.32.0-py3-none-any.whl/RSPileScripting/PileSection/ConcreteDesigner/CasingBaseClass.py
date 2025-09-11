import RSPileScripting.generated_python_files.pile_section_services.CommonCasing_pb2 as CommonCasing_pb2
from RSPileScripting._client import Client
from abc import ABC, abstractmethod

class CasingBaseClass(ABC):
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = self._create_stub()

	@abstractmethod
	def _create_stub(self):
		pass

	def _getCasingProperties(self) -> CommonCasing_pb2.CasingProperties:
		request = CommonCasing_pb2.GetCasingPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetCasingProperties, request)
		return response.casing_props

	def _setCasingProperties(self, properties: CommonCasing_pb2.CasingProperties):
		request = CommonCasing_pb2.SetCasingPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			casing_props=properties)
		self._client.callFunction(self._stub.SetCasingProperties, request)

	def getUseCasing(self) -> bool:
		properties = self._getCasingProperties()
		return properties.has_casing
	
	def setUseCasing(self, useCasing: bool):
		properties = self._getCasingProperties()
		properties.has_casing = useCasing
		self._setCasingProperties(properties)

	def getYieldStress(self) -> float:
		properties = self._getCasingProperties()
		return properties.yield_stress_of_casing
	
	def setYieldStress(self, yieldStress: float):
		properties = self._getCasingProperties()
		properties.yield_stress_of_casing = yieldStress
		self._setCasingProperties(properties)

	def getElasticModulus(self) -> float:
		properties = self._getCasingProperties()
		return properties.elastic_modulus_of_casing
	
	def setElasticModulus(self, elasticModulus: float):
		properties = self._getCasingProperties()
		properties.elastic_modulus_of_casing = elasticModulus
		self._setCasingProperties(properties)

	def getCasingThickness(self) -> float:
		properties = self._getCasingProperties()
		return properties.thickness_of_casing
	
	def setCasingThickness(self, thickness: float):
		properties = self._getCasingProperties()
		properties.thickness_of_casing = thickness
		self._setCasingProperties(properties)