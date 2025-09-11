import pandas as pd
from RSPileScripting.GraphingOptionsEnums import GraphingOptions

class ResultsTable(pd.DataFrame):
	"""
		Examples:
		:ref:`pile analysis results`
	"""
	def _constructor(self, rows_data):
		return ResultsTable(
			rows_data=rows_data,
			pile_id=self.attrs.get("pile_id"),
			enum_to_header_str_map=self.attrs.get("enum_to_header_str_map"),
		)

	def __init__(self, rows_data, pile_id: str, enum_to_header_str_map: dict[GraphingOptions, str]):
		super().__init__(rows_data)
		self.attrs["pile_id"] = pile_id
		self.attrs["enum_to_header_str_map"] = enum_to_header_str_map

	def getMaximumValue(self, column_enum: GraphingOptions):
		"""
		Looks at all values of the column specified and returns the max value.
		"""
		enum_to_header_str_map = self.attrs.get("enum_to_header_str_map")
		column_name = enum_to_header_str_map.get(column_enum)
		
		if column_name in self.columns:
			max_idx = self[column_name].idxmax()
			max_val = self[column_name].iloc[max_idx]
			return max_val
		else:
			raise KeyError(f"Column '{column_name}' not found.")

	def getMinimumValue(self, column_enum: GraphingOptions) -> float:
		"""
		Looks at all values of the column specified and returns the minimum value.
		"""
		enum_to_header_str_map : dict = self.attrs.get("enum_to_header_str_map")
		column_name = enum_to_header_str_map.get(column_enum)
		
		if column_name in self.columns:
			min_idx = self[column_name].idxmin()
			min_val = self[column_name].iloc[min_idx]
			return min_val
		else:
			raise KeyError(f"Column '{column_name}' not found.")
		
	def getColumnName(self, column_enum: GraphingOptions) -> str:
		"""
		Examples:
		:ref:`pile analysis results`
		"""
		enum_to_header_str_map : dict = self.attrs.get("enum_to_header_str_map")
		return enum_to_header_str_map.get(column_enum)

	def selectColumns(self, *column_enums: GraphingOptions) -> "ResultsTable":
		column_names = [self.getColumnName(column) for column in column_enums]
		selected_data = self[column_names]
		return self._constructor(selected_data)