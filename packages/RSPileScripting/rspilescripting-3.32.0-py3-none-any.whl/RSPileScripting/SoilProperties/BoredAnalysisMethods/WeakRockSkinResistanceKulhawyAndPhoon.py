from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.BoredWeakRockKulhawyAndPhoonService_pb2 as BoredWeakRockKulhawyAndPhoonService_pb2
import RSPileScripting.generated_python_files.soil_services.BoredWeakRockKulhawyAndPhoonService_pb2_grpc as BoredWeakRockKulhawyAndPhoonService_pb2_grpc

class KulhawyAndPhoon:
	"""
	Examples:
	:ref:`soil properties bored`
	"""
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = BoredWeakRockKulhawyAndPhoonService_pb2_grpc.BoredWeakRockKulhawyAndPhoonServiceStub(self._client.channel)

	def _getKulhawyAndPhoonProperties(self) -> BoredWeakRockKulhawyAndPhoonService_pb2.KulhawyAndPhoonProperties:
		request = BoredWeakRockKulhawyAndPhoonService_pb2.GetKulhawyAndPhoonRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetKulhawyAndPhoonProperties, request)
		return response.kulhawy_and_phoon_props

	def _setKulhawyAndPhoonProperties(self, kulhawyAndPhoonProperties: BoredWeakRockKulhawyAndPhoonService_pb2.KulhawyAndPhoonProperties):
		request = BoredWeakRockKulhawyAndPhoonService_pb2.SetKulhawyAndPhoonRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, kulhawy_and_phoon_props=kulhawyAndPhoonProperties)
		self._client.callFunction(self._stub.SetKulhawyAndPhoonProperties, request)

	def setChi(self, chi: float):
		properties = self._getKulhawyAndPhoonProperties()
		properties.val_omega = chi
		self._setKulhawyAndPhoonProperties(properties)

	def getChi(self) -> float:
		properties = self._getKulhawyAndPhoonProperties()
		return properties.val_omega