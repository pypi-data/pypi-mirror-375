from RSPileScripting._client import Client
from RSPileScripting.generated_python_files.pile_section_services import CommonCore_pb2 as CommonCore_pb2
from abc import ABC, abstractmethod

class CoreBaseClass(ABC):
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = self._create_stub()

	@abstractmethod
	def _create_stub(self):
		pass

	def _getCoreProperties(self) -> CommonCore_pb2.CoreProperties:
		request = CommonCore_pb2.GetCorePropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetCoreProperties, request)
		return response.core_props

	def _setCoreProperties(self, properties: CommonCore_pb2.CoreProperties):
		request = CommonCore_pb2.SetCorePropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			core_props=properties)
		self._client.callFunction(self._stub.SetCoreProperties, request)

	def getUseCore(self) -> bool:
		properties = self._getCoreProperties()
		return properties.has_core
	
	def setUseCore(self, useCore: bool):
		properties = self._getCoreProperties()
		properties.has_core = useCore
		self._setCoreProperties(properties)

	def getIsFilledCore(self) -> bool:
		properties = self._getCoreProperties()
		return properties.is_filled_core
	
	def setIsFilledCore(self, isFilledCore: bool):
		properties = self._getCoreProperties()
		properties.is_filled_core = isFilledCore
		self._setCoreProperties(properties)

	def getYieldStress(self) -> float:
		properties = self._getCoreProperties()
		return properties.yield_stress_of_core
	
	def setYieldStress(self, yieldStress: float):
		properties = self._getCoreProperties()
		properties.yield_stress_of_core = yieldStress
		self._setCoreProperties(properties)

	def getElasticModulus(self) -> float:
		properties = self._getCoreProperties()
		return properties.elastic_modulus_of_core
	
	def setElasticModulus(self, elasticModulus: float):
		properties = self._getCoreProperties()
		properties.elastic_modulus_of_core = elasticModulus
		self._setCoreProperties(properties)

	def getCoreDiameter(self) -> float:
		properties = self._getCoreProperties()
		return properties.diameter_of_core
	
	def setCoreDiameter(self, diameter: float):
		properties = self._getCoreProperties()
		properties.diameter_of_core = diameter
		self._setCoreProperties(properties)

	def getWallThickness(self) -> float:
		properties = self._getCoreProperties()
		return properties.thickness_of_core
	
	def setWallThickness(self, wallThickness: float):
		properties = self._getCoreProperties()
		properties.thickness_of_core = wallThickness
		self._setCoreProperties(properties)