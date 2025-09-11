from typing import Dict
from RSPileScripting.GraphingOptionsEnums import GraphingOptions
from RSPileScripting.ResultsTable import ResultsTable

class PileResults(Dict[str, ResultsTable]):
	"""
		Examples:
		:ref:`pile analysis results`
	"""
	def __init__(self, enum_to_header_str_map: Dict[GraphingOptions, str]):
		super().__init__()
		self.enum_to_header_str_map = enum_to_header_str_map

	def getMaximumValue(self, column_enum: GraphingOptions):
		"""
		Looks at all values of the column specified for each Pile and returns the max value and pile name.
		"""
		max_value = None
		max_pile_name = None

		for pile_name, results_table in self.items():
			current_max = results_table.getMaximumValue(column_enum)

			if max_value is None or current_max > max_value:
				max_value = current_max
				max_pile_name = pile_name

		return max_pile_name, max_value

	def getMinimumValue(self, column_enum: GraphingOptions):
		"""
		Looks at all values of the column specified for each Pile and returns the minimum value and pile name.
		"""
		minimum_value = None
		minimum_pile_name = None

		for pile_name, results_table in self.items():
			current_minimum = results_table.getMinimumValue(column_enum)

			if minimum_value is None or current_minimum < minimum_value:
				minimum_value = current_minimum
				minimum_pile_name = pile_name

		return minimum_pile_name, minimum_value
