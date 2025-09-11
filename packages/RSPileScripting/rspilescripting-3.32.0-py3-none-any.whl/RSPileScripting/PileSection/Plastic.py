from enum import Enum
from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.PileAnalysisMaterialPlasticService_pb2 as PileAnalysisMaterialPlasticService_pb2
import RSPileScripting.generated_python_files.pile_section_services.PileAnalysisMaterialPlasticService_pb2_grpc as PileAnalysisMaterialPlasticService_pb2_grpc
import RSPileScripting.generated_python_files.pile_section_services.CommonPileAnalysisCrossSectionTypes_pb2 as CommonPileAnalysisCrossSectionTypes_pb2
from RSPileScripting.PileSection.CrossSectionOrganization.PlasticCrossSections import PlasticCrossSections as CrossSection

class PlasticCrossSectionType(Enum):
	CIRCULAR = CommonPileAnalysisCrossSectionTypes_pb2.CrossSectionType.P2_CIRCULAR
	RECTANGULAR = CommonPileAnalysisCrossSectionTypes_pb2.CrossSectionType.P2_RECTANGULAR
	PIPE = CommonPileAnalysisCrossSectionTypes_pb2.CrossSectionType.P2_PIPE

class Plastic:
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = PileAnalysisMaterialPlasticService_pb2_grpc.PileAnalysisMaterialPlasticServiceStub(self._client.channel)
		self.CrossSection = CrossSection(self._model_id, self._pile_id, self._client)

	def _getPlasticProperties(self) -> PileAnalysisMaterialPlasticService_pb2.PlasticProperties:
		request = PileAnalysisMaterialPlasticService_pb2.GetPlasticPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetPlasticProperties, request)
		return response.plastic_props

	def _setPlasticProperties(self, plasticProps: PileAnalysisMaterialPlasticService_pb2.PlasticProperties):
		request = PileAnalysisMaterialPlasticService_pb2.SetPlasticPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			plastic_props=plasticProps)
		self._client.callFunction(self._stub.SetPlasticProperties, request)

	def getYoungsModulus(self) -> float:
		properties = self._getPlasticProperties()
		return properties.elastic_modulus
	
	def setYoungsModulus(self, youngsModulus: float):
		properties = self._getPlasticProperties()
		properties.elastic_modulus = youngsModulus
		self._setPlasticProperties(properties)

	def getMomentCapacityMyz(self) -> float:
		properties = self._getPlasticProperties()
		return properties.plastic_moment_capacity_mxy
	
	def setMomentCapacityMyz(self, momentCapacityMyz: float):
		properties = self._getPlasticProperties()
		properties.plastic_moment_capacity_mxy = momentCapacityMyz
		self._setPlasticProperties(properties)

	def getMomentCapacityMxz(self) -> float:
		properties = self._getPlasticProperties()
		return properties.plastic_moment_capacity_mxz
	
	def setMomentCapacityMxz(self, momentCapacityMxz: float):
		properties = self._getPlasticProperties()
		properties.plastic_moment_capacity_mxz = momentCapacityMxz
		self._setPlasticProperties(properties)

	def getCrossSectionType(self) -> PlasticCrossSectionType:
		properties = self._getPlasticProperties()
		return PlasticCrossSectionType(properties.cross_section_type)
	
	def setCrossSectionType(self, crossSectionType: PlasticCrossSectionType):
		properties = self._getPlasticProperties()
		properties.cross_section_type = crossSectionType.value
		self._setPlasticProperties(properties)