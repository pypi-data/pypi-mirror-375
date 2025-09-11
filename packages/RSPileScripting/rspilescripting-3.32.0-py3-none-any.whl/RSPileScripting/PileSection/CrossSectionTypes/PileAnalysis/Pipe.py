from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.PileAnalysisCrossSectionPipeService_pb2 as PileAnalysisCrossSectionPipeService_pb2
import RSPileScripting.generated_python_files.pile_section_services.PileAnalysisCrossSectionPipeService_pb2_grpc as PileAnalysisCrossSectionPipeService_pb2_grpc

class Pipe:
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = PileAnalysisCrossSectionPipeService_pb2_grpc.PileAnalysisCrossSectionPipeServiceStub(self._client.channel)

	def _getPipeProperties(self) -> PileAnalysisCrossSectionPipeService_pb2.PipeProperties:
		request = PileAnalysisCrossSectionPipeService_pb2.GetPipePropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetPipeProperties, request)
		return response.pipe_props

	def _setPipeProperties(self, pipeProps: PileAnalysisCrossSectionPipeService_pb2.PipeProperties):
		request = PileAnalysisCrossSectionPipeService_pb2.SetPipePropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			pipe_props=pipeProps)
		self._client.callFunction(self._stub.SetPipeProperties, request)

	def getOutsideDiameter(self) -> float:
		properties = self._getPipeProperties()
		return properties.pipe_outside_diameter
	
	def setOutsideDiameter(self, diameter: float):
		properties = self._getPipeProperties()
		properties.pipe_outside_diameter = diameter
		self._setPipeProperties(properties)

	def getWallThickness(self) -> float:
		properties = self._getPipeProperties()
		return properties.pipe_wall_thickness
	
	def setWallThickness(self, thickness: float):
		properties = self._getPipeProperties()
		properties.pipe_wall_thickness = thickness
		self._setPipeProperties(properties)