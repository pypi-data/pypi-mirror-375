from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.AxialElasticService_pb2 as AxialElasticService_pb2
import RSPileScripting.generated_python_files.soil_services.AxialElasticService_pb2_grpc as AxialElasticService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class AxialElasticDatumProperties(Enum):
	SKIN_FRICTION_STIFFNESS ="ELASTIC_SHEAR_MOD"
	END_BEARING_STIFFNESS ="ELASTIC_END_BEARING_MOD"

class Elastic:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = AxialElasticService_pb2_grpc.AxialElasticServiceStub(self._client.channel)
		self.Datum: Datum[AxialElasticDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.AXIAL
		)

	def _getElasticProperties(self) -> AxialElasticService_pb2.ElasticProperties:
		request = AxialElasticService_pb2.GetElasticRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetElasticProperties, request)
		return response.elastic_props

	def _setElasticProperties(self, elasticProps: AxialElasticService_pb2.ElasticProperties):
		request = AxialElasticService_pb2.SetElasticRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, elastic_props=elasticProps)
		self._client.callFunction(self._stub.SetElasticProperties, request)

	def getSkinFrictionStiffness(self) -> float:
		properties = self._getElasticProperties()
		return properties.elastic_shear_mod

	def setSkinFrictionStiffness(self, skinFrictionStiffness: float):
		properties = self._getElasticProperties()
		properties.elastic_shear_mod = skinFrictionStiffness
		self._setElasticProperties(properties)

	def getEndBearingStiffness(self) -> float:
		properties = self._getElasticProperties()
		return properties.elastic_end_bearing_mod

	def setEndBearingStiffness(self, endBearingStiffnesss: float):
		properties = self._getElasticProperties()
		properties.elastic_end_bearing_mod = endBearingStiffnesss
		self._setElasticProperties(properties)