from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_section_services.ReinforcedConcreteDesignerIBeamService_pb2 as ReinforcedConcreteDesignerIBeamService_pb2
import RSPileScripting.generated_python_files.pile_section_services.ReinforcedConcreteDesignerIBeamService_pb2_grpc as ReinforcedConcreteDesignerIBeamService_pb2_grpc
from RSPileScripting.PileSection.ConcreteDesigner.IBeamEnums import AmericanIBeamTypes, CanadianIBeamTypes

class IBeam:
	"""
	Examples:
	:ref:`pile sections pile analysis`
	"""
	def __init__(self, model_id: str, pile_id: str, client: Client):
		self._model_id = model_id
		self._pile_id = pile_id
		self._client = client
		self._stub = ReinforcedConcreteDesignerIBeamService_pb2_grpc.ReinforcedConcreteDesignerIBeamServiceStub(self._client.channel)

	def _getIBeamProperties(self) -> ReinforcedConcreteDesignerIBeamService_pb2.IBeamProperties:
		request = ReinforcedConcreteDesignerIBeamService_pb2.GetIBeamPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id)
		response = self._client.callFunction(self._stub.GetIBeamProperties, request)
		return response.ibeam_props

	def _setIBeamProperties(self, IBeamProps: ReinforcedConcreteDesignerIBeamService_pb2.IBeamProperties):
		request = ReinforcedConcreteDesignerIBeamService_pb2.SetIBeamPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_id=self._pile_id, 
			ibeam_props=IBeamProps)
		self._client.callFunction(self._stub.SetIBeamProperties, request)

	def getUseIBeam(self) -> bool:
		properties = self._getIBeamProperties()
		return properties.has_ibeam

	def setUseIBeam(self, useIBeam: bool):
		properties = self._getIBeamProperties()
		properties.has_ibeam = useIBeam
		self._setIBeamProperties(properties)

	def getYieldStress(self) -> float:
		properties = self._getIBeamProperties()
		return properties.yield_stress_of_beam
	
	def setYieldStress(self, yieldStress: float):
		properties = self._getIBeamProperties()
		properties.yield_stress_of_beam = yieldStress
		self._setIBeamProperties(properties)

	def getElasticModulus(self) -> float:
		properties = self._getIBeamProperties()
		return properties.elastic_modulus_of_beam
	
	def setElasticModulus(self, elasticModulus: float):
		properties = self._getIBeamProperties()
		properties.elastic_modulus_of_beam = elasticModulus
		self._setIBeamProperties(properties)

	def getIBeamType(self) -> AmericanIBeamTypes | CanadianIBeamTypes:
		properties = self._getIBeamProperties()
		ibeam_name = properties.ibeam_type
		if(ibeam_name == "Nothing"):
			self._client.logger.warning("No IBeam Type is Set")
			return None
		if properties.is_canadian_steel:
			for ibeam in CanadianIBeamTypes:
				if ibeam.value == ibeam_name:
					return ibeam
		else:
			for ibeam in AmericanIBeamTypes:
				if ibeam.value == ibeam_name:
					return ibeam
		raise ValueError("The IBeam Type set in RSPile is Not Available in the Python Scripting Library")

	def setIBeamType(self, ibeamType: AmericanIBeamTypes | CanadianIBeamTypes):
		properties = self._getIBeamProperties()
		properties.ibeam_type = ibeamType.value
		if ibeamType in CanadianIBeamTypes:
			properties.is_canadian_steel = True
		elif ibeamType in AmericanIBeamTypes:
			properties.is_canadian_steel = False
		else:
			raise ValueError("Invalid IBeam Type")
		self._setIBeamProperties(properties)