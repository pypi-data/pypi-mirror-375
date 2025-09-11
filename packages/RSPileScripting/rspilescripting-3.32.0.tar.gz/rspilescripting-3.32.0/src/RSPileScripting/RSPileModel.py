from RSPileScripting._client import Client
import os
from RSPileScripting.SoilProperties.SoilProperty import SoilProperty
from RSPileScripting.PileSection.PileSection import PileSection
from RSPileScripting.PileType.PileType import PileType
from RSPileScripting.GraphingOptionsEnums import GraphingOptions
from RSPileScripting.ResultsTable import ResultsTable
from RSPileScripting.PileResults import PileResults
from RSPileScripting.ProjectSettings.ProjectSettings import ProjectSettings
import RSPileScripting.generated_python_files.ModelService_pb2 as ModelService_pb2
import RSPileScripting.generated_python_files.ModelService_pb2_grpc as ModelService_pb2_grpc

class RSPileModel():
	def __init__(self, client : Client, model_id : str, file_name : str):
		self._model_id = model_id
		self._client = client
		self.file_name = file_name
		self._stub = ModelService_pb2_grpc.ModelServiceStub(self._client.channel)
		self.ProjectSettings = ProjectSettings(self._client, self._model_id)

	def getSoilProperties(self) -> list[SoilProperty]:
		"""
		Examples:
		:ref:`Model Example`
		"""
		getSoilPropertiesResponse : ModelService_pb2.GetNumberOfActiveSoilPropertiesResponse = \
			self._client.callFunction(self._stub.GetNumberOfActiveSoilProperties, ModelService_pb2.GetNumberOfActiveSoilPropertiesRequest(session_id = self._client.sessionID, model_id=self._model_id))
		soilPropList = []
		for index in range(0,getSoilPropertiesResponse.number_of_soil_props):
			response = self._client.callFunction(self._stub.GetSoilProperty, ModelService_pb2.GetSoilPropertyRequest(session_id = self._client.sessionID, model_id=self._model_id, soil_index=index))
			soilPropList.append(SoilProperty(model_id=self._model_id, soil_id=response.soil_id, client=self._client))
		return soilPropList
	
	def getPileSections(self) -> list[PileSection]:
		"""
		Examples:
		:ref:`Model Example`
		"""
		getPilePropertiesResponse: ModelService_pb2.GetNumberOfActivePilePropertiesResponse = \
			self._client.callFunction(self._stub.GetNumberOfActivePileProperties, ModelService_pb2.GetNumberOfActivePilePropertiesRequest(session_id=self._client.sessionID, model_id=self._model_id))
		pileSectionList = []
		for index in range(0, getPilePropertiesResponse.number_of_pile_props):
			response = self._client.callFunction(self._stub.GetPileProperty, ModelService_pb2.GetPilePropertyRequest(session_id=self._client.sessionID, model_id=self._model_id, pile_index=index))
			pileSectionList.append(PileSection(model_id=self._model_id, pile_id=response.pile_id, client=self._client))
		return pileSectionList
	
	def getPileTypes(self) -> list[PileType]:
		"""
		Examples:
		:ref:`Model Example`
		"""
		getPileTypesResponse: ModelService_pb2.GetNumberOfActivePileTypesResponse = \
			self._client.callFunction(self._stub.GetNumberOfActivePileTypes, ModelService_pb2.GetNumberOfActivePileTypesRequest(session_id=self._client.sessionID, model_id=self._model_id))
		pileTypeList = []
		for index in range(0, getPileTypesResponse.number_of_pile_types):
			response = self._client.callFunction(self._stub.GetPileType, ModelService_pb2.GetPileTypeRequest(session_id=self._client.sessionID, model_id=self._model_id, pile_type_index=index))
			pileTypeList.append(PileType(model_id=self._model_id, pile_type_id=response.pile_type_id, client=self._client))
		return pileTypeList

	def compute(self) -> ModelService_pb2.ComputeResponse:
		"""
		Examples:
		:ref:`Model Example`
		"""
		return self._client.callFunction(self._stub.Compute, ModelService_pb2.ComputeRequest(session_id = self._client.sessionID, model_id=self._model_id))

	def getPileResultsTables(self, *args: GraphingOptions) -> PileResults:
		"""
		This function returns a PileResults object which holds a list of ResultsTable objects.
		If GraphingOptions arguments are passed in, only that the arguments passed in will be included in the tables.
		If no arguments are passed in, all GraphingOptions will be included.
		If invalid arguments are passed in, they will be automatically removed from the tables.

		Examples:
		:ref:`pile analysis results`
		"""
		response = self._client.callFunction(
			self._stub.GetPileResultsTables,
			ModelService_pb2.GetPileResultsTablesRequest(
				session_id=self._client.sessionID,
				model_id=self._model_id,
				var_list=[arg.value for arg in args]
			),
		)

		enum_to_header_str_map = {}
		for key, value in dict(response.enum_to_header).items():
				enum_to_header_str_map[GraphingOptions(key)] = value

		tables = response.tables
		pile_results = PileResults(enum_to_header_str_map=enum_to_header_str_map)  # PileResults will hold ResultsTable objects
		
		for index, grpc_table in enumerate(tables):
			# convert grpc rows to a list of dicts
			rows_data = []
			for row in grpc_table.rows:
				rows_data.append(dict(row.data))

			# Convert the data to a class that inherits from df
			python_table_df = ResultsTable(rows_data, pile_id=grpc_table.pile_id, enum_to_header_str_map=enum_to_header_str_map)

			pile_results[grpc_table.pile_id] = python_table_df

		return pile_results

	def save(self, fileName : str = None):
		"""
		Examples:
		:ref:`Model Example`
		"""
		if fileName is None:
			fileName = self.file_name
		absPath = os.path.abspath(fileName)
		directory = os.path.dirname(absPath)
		if os.path.isdir(directory):
			saveFileRequest = ModelService_pb2.SaveRequest(session_id = self._client.sessionID, model_id=self._model_id,file_name=absPath)
			self._client.callFunction(self._stub.Save, saveFileRequest)
		else:
			self._client.logger.error("Invalid Directory Path: %s", absPath)
			raise FileNotFoundError(f"The directory path '{fileName}' is invalid.")

	def close(self, saveChanges = True):
		"""
		Examples:
		:ref:`Model Example`
		"""
		if saveChanges:
			self.save()
		return self._client.callFunction(self._stub.Close, 
				ModelService_pb2.CloseRequest(session_id=self._client.sessionID, model_id=self._model_id))