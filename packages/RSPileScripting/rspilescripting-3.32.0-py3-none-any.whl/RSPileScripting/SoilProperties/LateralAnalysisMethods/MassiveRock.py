from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.LateralMassiveRockService_pb2 as LateralMassiveRockService_pb2
import RSPileScripting.generated_python_files.soil_services.LateralMassiveRockService_pb2_grpc as LateralMassiveRockService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup
from RSPileScripting.SoilProperties.Datum import Datum
from enum import Enum

class LateralMassiveRockDatumProperties(Enum):
	UNIAXIAL_COMPRESSIVE_STRENGTH = "LAT_MASSROCK_UCS"
	INTACT_ROCK_MODULUS = "LAT_MASSROCK_EI"
	ROCK_MASS_MODULUS = "LAT_MASSROCK_ERM"
	POISSON_RATIO ="LAT_MASSROCK_POISSON"

class ModulusType(Enum):
	USE_INTACT_ROCK_MODULUS = 1
	USE_ROCK_MASS_MODULUS = 2

class MassiveRock:
	"""
	Examples:
	:ref:`soil properties lateral pile analysis`
	"""
	def __init__(self, model_id: str, soil_id: str, client: Client):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = LateralMassiveRockService_pb2_grpc.LateralMassiveRockServiceStub(self._client.channel)
		self.Datum: Datum[LateralMassiveRockDatumProperties] = Datum(
			model_id=self._model_id,
			soil_id=self._soil_id,
			client=self._client,
			datumGroup=eRSPileDatumGroup.LATERAL
		)

	def _getMassiveRockProperties(self) -> LateralMassiveRockService_pb2.MassiveRockProperties:
		request = LateralMassiveRockService_pb2.GetMassiveRockRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id)
		response = self._client.callFunction(self._stub.GetMassiveRockProperties, request)
		return response.massive_rock_props

	def _setMassiveRockProperties(self, massiveRockProps: LateralMassiveRockService_pb2.MassiveRockProperties):
		request = LateralMassiveRockService_pb2.SetMassiveRockRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, massive_rock_props=massiveRockProps)
		self._client.callFunction(self._stub.SetMassiveRockProperties, request)

	def getModulusType(self) -> ModulusType:
		properties = self._getMassiveRockProperties()
		if properties.use_Erm_MassRock:
			return ModulusType.USE_ROCK_MASS_MODULUS
		else:
			return ModulusType.USE_INTACT_ROCK_MODULUS
	
	def setModulusType(self, modulusType: ModulusType):
		properties = self._getMassiveRockProperties()
		if modulusType == ModulusType.USE_INTACT_ROCK_MODULUS:
			useErm = False
		elif modulusType == ModulusType.USE_ROCK_MASS_MODULUS:
			useErm = True
		else:
			raise ValueError("Invalid modulus type")
		properties.use_Erm_MassRock = useErm
		self._setMassiveRockProperties(properties)

	def getIntactRockConstant(self) -> float:
		properties = self._getMassiveRockProperties()
		return properties.mi_MassRock

	def setIntactRockConstant(self, intactRockConstant: float):
		properties = self._getMassiveRockProperties()
		properties.mi_MassRock = intactRockConstant
		self._setMassiveRockProperties(properties)

	def getGeologicalStrengthIndex(self) -> float:
		properties = self._getMassiveRockProperties()
		return properties.GSI_MassRock

	def setGeologicalStrengthIndex(self, geologicalStrengthIndex: float):
		properties = self._getMassiveRockProperties()
		properties.GSI_MassRock = geologicalStrengthIndex
		self._setMassiveRockProperties(properties)

	def getUniaxialCompressiveStrength(self) -> float:
		properties = self._getMassiveRockProperties()
		return properties.UCS_MassRock

	def setUniaxialCompressiveStrength(self, uniaxialCompressiveStrength: float):
		properties = self._getMassiveRockProperties()
		properties.UCS_MassRock = uniaxialCompressiveStrength
		self._setMassiveRockProperties(properties)

	def getIntactRockModulus(self) -> float:
		properties = self._getMassiveRockProperties()
		return properties.Ei_MassRock

	def setIntactRockModulus(self, intactRockModulus: float):
		properties = self._getMassiveRockProperties()
		properties.Ei_MassRock = intactRockModulus
		self._setMassiveRockProperties(properties)

	def getRockMassModulus(self) -> float:
		properties = self._getMassiveRockProperties()
		return properties.Erm_MassRock

	def setRockMassModulus(self, rockMassModulus: float):
		properties = self._getMassiveRockProperties()
		properties.Erm_MassRock = rockMassModulus
		self._setMassiveRockProperties(properties)

	def getPoissonRatio(self) -> float:
		properties = self._getMassiveRockProperties()
		return properties.poisson_ratio_MassRock

	def setPoissonRatio(self, poissonRatio: float):
		properties = self._getMassiveRockProperties()
		properties.poisson_ratio_MassRock = poissonRatio
		self._setMassiveRockProperties(properties)