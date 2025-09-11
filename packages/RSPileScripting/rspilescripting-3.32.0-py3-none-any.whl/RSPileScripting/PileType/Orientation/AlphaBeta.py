from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_type_services.PileTypeOrientationAlphaBetaService_pb2 as PileTypeOrientationAlphaBetaService_pb2
import RSPileScripting.generated_python_files.pile_type_services.PileTypeOrientationAlphaBetaService_pb2_grpc as PileTypeOrientationAlphaBetaService_pb2_grpc

class AlphaBeta:
	"""
		Examples:
		:ref:`pile types pile analysis`
	"""
	def __init__(self, model_id: str, pile_type_id: str, client: Client):
		self.pile_type_id = pile_type_id
		self._client = client
		self._model_id = model_id
		self._stub = PileTypeOrientationAlphaBetaService_pb2_grpc.PileTypeOrientationAlphaBetaServiceStub(self._client.channel)

	def _getPileTypeAlphaBetaProperties(self) -> PileTypeOrientationAlphaBetaService_pb2.AlphaBetaProperties:
		request = PileTypeOrientationAlphaBetaService_pb2.GetAlphaBetaPropertiesRequest(
			session_id=self._client.sessionID, pile_type_id=self.pile_type_id)
		response = self._client.callFunction(self._stub.GetAlphaBetaProperties, request)
		return response.alpha_beta_props

	def _setPileTypeAlphaBetaProperties(self, alphaBetaProps: PileTypeOrientationAlphaBetaService_pb2.AlphaBetaProperties):
		request = PileTypeOrientationAlphaBetaService_pb2.SetAlphaBetaPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_type_id=self.pile_type_id, 
			alpha_beta_props=alphaBetaProps)
		self._client.callFunction(self._stub.SetAlphaBetaProperties, request)

	def getAlphaAngle(self) -> float:
		properties = self._getPileTypeAlphaBetaProperties()
		return properties.alpha_trend
	
	def setAlphaAngle(self, alphaAngle: float):
		properties = self._getPileTypeAlphaBetaProperties()
		properties.alpha_trend = alphaAngle
		self._setPileTypeAlphaBetaProperties(properties)

	def getBetaAngle(self) -> float:
		properties = self._getPileTypeAlphaBetaProperties()
		return properties.beta_plunge
	
	def setBetaAngle(self, betaAngle: float):
		properties = self._getPileTypeAlphaBetaProperties()
		properties.beta_plunge = betaAngle
		self._setPileTypeAlphaBetaProperties(properties)