from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.LateralElasticService_pb2 as LateralElasticService_pb2
import RSPileScripting.generated_python_files.soil_services.LateralElasticService_pb2_grpc as LateralElasticService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class LateralElasticDatumProperties(Enum):
	ELASTIC_SUBGRADE_REACTION = "LAT_ELASTIC_STIFFNESS"

class Elastic:
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = LateralElasticService_pb2_grpc.LateralElasticServiceStub(self._client.channel)
		self.Datum: Datum[LateralElasticDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.LATERAL
		)

	def _getElasticProperties(self) -> LateralElasticService_pb2.ElasticProperties:
		request = LateralElasticService_pb2.GetElasticRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetElasticProperties, request)
		return response.elastic_props

	def _setElasticProperties(self, elasticProps: LateralElasticService_pb2.ElasticProperties):
		request = LateralElasticService_pb2.SetElasticRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, elastic_props=elasticProps)
		self._client.callFunction(self._stub.SetElasticProperties, request)

	def getElasticSubgradeReaction(self) -> float:
		properties = self._getElasticProperties()
		return properties.stiffness_e

	def setElasticSubgradeReaction(self, elasticSubgradeReaction: float):
		properties = self._getElasticProperties()
		properties.stiffness_e = elasticSubgradeReaction
		self._setElasticProperties(properties)