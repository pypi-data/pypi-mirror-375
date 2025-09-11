import RSPileScripting.generated_python_files.pile_section_services.CommonReinforcementPattern_pb2 as CommonReinforcementPattern_pb2
from RSPileScripting._client import Client
from RSPileScripting.PileSection.ConcreteDesigner.RectangleReinforcementPattern import RectangleReinforcementPattern as Rectangle
from RSPileScripting.PileSection.ConcreteDesigner.RadialReinforcementPattern import RadialReinforcementPattern as Radial
from RSPileScripting.PileSection.ConcreteDesigner.CustomReinforcementPattern import CustomReinforcementPattern as Custom
from abc import ABC, abstractmethod
from enum import Enum

class ReinforcementPatternType(Enum):
	RADIAL = CommonReinforcementPattern_pb2.PatternType.RPATTERN_RADIAL
	RECTANGULAR = CommonReinforcementPattern_pb2.PatternType.RPATTERN_RECTANGULAR
	CUSTOM = CommonReinforcementPattern_pb2.PatternType.RPATTERN_CUSTOM

class ReinforcementPatternBaseClass(ABC):
	"""
	Examples:
	:ref:`prestressed concrete section`
	"""
	def __init__(self, model_id: str, pattern_id: str, client: Client):
		self._model_id = model_id
		self._pattern_id = pattern_id
		self._client = client
		self._stub = self._create_stub()
		self.Rectangle = Rectangle(self._model_id, self._pattern_id, self._client)
		self.Radial = Radial(self._model_id, self._pattern_id, self._client)
		self.Custom = Custom(self._model_id, self._pattern_id, self._client)

	@abstractmethod
	def _create_stub(self):
		pass
	
	@abstractmethod
	def _getReinforcementPatternProperties(self):
		pass

	def _setReinforcementPatternProperties(self, soilProps):
		pass

	def getName(self):
		properties = self._getReinforcementPatternProperties()
		return properties.name

	def setName(self, name):
		properties = self._getReinforcementPatternProperties()
		properties.name = name
		self._setReinforcementPatternProperties(properties)

	def getReinforcementPatternType(self) -> ReinforcementPatternType:
		properties = self._getReinforcementPatternProperties()
		return ReinforcementPatternType(properties.pattern_type)
	
	def setReinforcementPatternType(self, reinforcementPatternType: ReinforcementPatternType):
		properties = self._getReinforcementPatternProperties()
		properties.pattern_type = reinforcementPatternType.value
		self._setReinforcementPatternProperties(properties)

	def getUseBundledBars(self) -> bool:
		properties = self._getReinforcementPatternProperties()
		return properties.bundled_bars

	def setUseBundledBars(self, bundledBars: bool):
		properties = self._getReinforcementPatternProperties()
		properties.bundled_bars = bundledBars
		self._setReinforcementPatternProperties(properties)

	def getNumberOfBundledBars(self) -> int:
		properties = self._getReinforcementPatternProperties()
		return properties.num_bundled

	def setNumberOfBundledBars(self, numBundled: int):
		properties = self._getReinforcementPatternProperties()
		properties.num_bundled = numBundled
		self._setReinforcementPatternProperties(properties)
