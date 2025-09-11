from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.PileAnalysisMaterialElasticService_pb2 as PileAnalysisMaterialElasticService_pb2
import RSPileScripting.generated_python_files.pile_section_services.PileAnalysisMaterialElasticService_pb2_grpc as PileAnalysisMaterialElasticService_pb2_grpc
import RSPileScripting.generated_python_files.pile_section_services.CommonPileAnalysisCrossSectionTypes_pb2 as CommonPileAnalysisCrossSectionTypes_pb2
from RSPileScripting.PileSection.CrossSectionOrganization.ElasticCrossSections import ElasticCrossSections as CrossSection
from enum import Enum

class ElasticCrossSectionType(Enum):
	CIRCULAR = CommonPileAnalysisCrossSectionTypes_pb2.CrossSectionType.P2_CIRCULAR
	RECTANGULAR = CommonPileAnalysisCrossSectionTypes_pb2.CrossSectionType.P2_RECTANGULAR
	PIPE = CommonPileAnalysisCrossSectionTypes_pb2.CrossSectionType.P2_PIPE
	USER_DEFINED = CommonPileAnalysisCrossSectionTypes_pb2.CrossSectionType.P2_CUSTOM

class Elastic:
	"""
	Examples:
	:ref:`pile sections pile analysis`
	"""
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._pile_id = pile_id
		self._client = client
		self._model_id = model_id
		self._stub = PileAnalysisMaterialElasticService_pb2_grpc.PileAnalysisMaterialElasticServiceStub(self._client.channel)
		self.CrossSection = CrossSection(self._model_id, self._pile_id, self._client)

	def _getElasticProperties(self) -> PileAnalysisMaterialElasticService_pb2.ElasticProperties:
		request = PileAnalysisMaterialElasticService_pb2.GetElasticPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetElasticProperties, request)
		return response.elastic_props

	def _setElasticProperties(self, elasticProps: PileAnalysisMaterialElasticService_pb2.ElasticProperties):
		request = PileAnalysisMaterialElasticService_pb2.SetElasticPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			elastic_props=elasticProps)
		self._client.callFunction(self._stub.SetElasticProperties, request)

	def getYoungsModulus(self) -> float:
		properties = self._getElasticProperties()
		return properties.elastic_modulus
	
	def setYoungsModulus(self, youngsModulus: float):
		properties = self._getElasticProperties()
		properties.elastic_modulus = youngsModulus
		self._setElasticProperties(properties)
		
	def getCrossSectionType(self) -> ElasticCrossSectionType:
		properties = self._getElasticProperties()
		return ElasticCrossSectionType(properties.cross_section_type)
	
	def setCrossSectionType(self, crossSectionType: ElasticCrossSectionType):
		properties = self._getElasticProperties()
		properties.cross_section_type = crossSectionType.value
		self._setElasticProperties(properties)