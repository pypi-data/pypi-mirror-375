from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.PileAnalysisCrossSectionUserDefinedService_pb2 as PileAnalysisCrossSectionUserDefinedService_pb2
import RSPileScripting.generated_python_files.pile_section_services.PileAnalysisCrossSectionUserDefinedService_pb2_grpc as PileAnalysisCrossSectionUserDefinedService_pb2_grpc

class UserDefined:
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = PileAnalysisCrossSectionUserDefinedService_pb2_grpc.PileAnalysisCrossSectionUserDefinedServiceStub(self._client.channel)

	def _getUserDefinedProperties(self) -> PileAnalysisCrossSectionUserDefinedService_pb2.UserDefinedProperties:
		request = PileAnalysisCrossSectionUserDefinedService_pb2.GetUserDefinedPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetUserDefinedProperties, request)
		return response.user_defined_props

	def _setUserDefinedProperties(self, userDefinedProps: PileAnalysisCrossSectionUserDefinedService_pb2.UserDefinedProperties):
		request = PileAnalysisCrossSectionUserDefinedService_pb2.SetUserDefinedPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			user_defined_props=userDefinedProps)
		self._client.callFunction(self._stub.SetUserDefinedProperties, request)

	def getDiameter(self) -> float:
		properties = self._getUserDefinedProperties()
		return properties.diameter
	
	def setDiameter(self, diameter: float):
		properties = self._getUserDefinedProperties()
		properties.diameter = diameter
		self._setUserDefinedProperties(properties)

	def getPerimeter(self) -> float:
		properties = self._getUserDefinedProperties()
		return properties.perimeter
	
	def setPerimeter(self, perimeter: float):
		properties = self._getUserDefinedProperties()
		properties.perimeter = perimeter
		self._setUserDefinedProperties(properties)

	def getArea(self) -> float:
		properties = self._getUserDefinedProperties()
		return properties.area
	
	def setArea(self, area: float):
		properties = self._getUserDefinedProperties()
		properties.area = area
		self._setUserDefinedProperties(properties)

	def getIy(self) -> float:
		properties = self._getUserDefinedProperties()
		return properties.Iy
	
	def setIy(self, Iy: float):
		properties = self._getUserDefinedProperties()
		properties.Iy = Iy
		self._setUserDefinedProperties(properties)

	def getIx(self) -> float:
		properties = self._getUserDefinedProperties()
		return properties.Iz
	
	def setIx(self, Ix: float):
		properties = self._getUserDefinedProperties()
		properties.Iz = Ix
		self._setUserDefinedProperties(properties)