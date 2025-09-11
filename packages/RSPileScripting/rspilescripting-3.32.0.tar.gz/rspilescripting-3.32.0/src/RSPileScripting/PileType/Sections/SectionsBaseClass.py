from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_type_services.PileTypeSectionsService_pb2 as PileTypeSectionsService_pb2
import RSPileScripting.generated_python_files.pile_type_services.PileTypeSectionsService_pb2_grpc as PileTypeSectionsService_pb2_grpc
from enum import Enum
from abc import ABC, abstractmethod

class PileAnalysisPileTypeCrossSection(Enum):
	UNIFORM = PileTypeSectionsService_pb2.CrossSectionType.E_CROSS_SECTION_UNIFORM
	TAPERED = PileTypeSectionsService_pb2.CrossSectionType.E_CROSS_SECTION_TAPERED
	BELL = PileTypeSectionsService_pb2.CrossSectionType.E_CROSS_SECTION_BELL

class SectionsBaseClass(ABC):
	def __init__(self, model_id: str, pile_type_id: str, client: Client):
		self._pile_type_id = pile_type_id
		self._client = client
		self._model_id = model_id
		self._stub = PileTypeSectionsService_pb2_grpc.PileTypeSectionsServiceStub(self._client.channel)

	def _getPileTypeSectionsProperties(self) -> PileTypeSectionsService_pb2.SectionsProperties:
		request = PileTypeSectionsService_pb2.GetSectionsPropertiesRequest(
			session_id=self._client.sessionID, pile_type_id=self._pile_type_id)
		response = self._client.callFunction(self._stub.GetSectionsProperties, request)
		return response.sections_props

	def _setPileTypeSectionsProperties(self, sectionsProps: PileTypeSectionsService_pb2.SectionsProperties):
		request = PileTypeSectionsService_pb2.SetSectionsPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_type_id=self._pile_type_id, 
			sections_props=sectionsProps)
		self._client.callFunction(self._stub.SetSectionsProperties, request)

	def _getPileSegmentsByLength(self) -> PileTypeSectionsService_pb2.PileSegmentsByLengthProperties:
		request = PileTypeSectionsService_pb2.GetPileSegmentsByLengthRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_type_id=self._pile_type_id)
		response = self._client.callFunction(self._stub.GetPileSegmentsByLength, request)
		return response.segment_props	

	def _setPileSegmentsByLength(self, segmentProps: PileTypeSectionsService_pb2.PileSegmentsByLengthProperties):
		request = PileTypeSectionsService_pb2.SetPileSegmentsByLengthRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_type_id=self._pile_type_id,
			segment_props=segmentProps)
		self._client.callFunction(self._stub.SetPileSegmentsByLength, request)

	def _getPileSegmentsByBottomElevation(self) -> PileTypeSectionsService_pb2.PileSegmentsByBottomElevationProperties:
		request = PileTypeSectionsService_pb2.GetPileSegmentsByBottomElevationRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_type_id=self._pile_type_id)
		response = self._client.callFunction(self._stub.GetPileSegmentsByBottomElevation, request)
		return response.segment_props

	def _setPileSegmentsByBottomElevation(self, segmentProps: PileTypeSectionsService_pb2.PileSegmentsByBottomElevationProperties):
		request = PileTypeSectionsService_pb2.SetPileSegmentsByBottomElevationRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_type_id=self._pile_type_id, 
			segment_props=segmentProps)
		self._client.callFunction(self._stub.SetPileSegmentsByBottomElevation, request)

	@abstractmethod
	def getCrossSectionType(self):
		pass
	
	@abstractmethod
	def setCrossSectionType(self, crossSectionType):
		pass

	def setPileSegmentsByLength(self, pileHeadElevation: float, segments: list[tuple[str, float]]):
		"""
			sections: list of tuples, each tuple containing a segment's name and its length
			Note: Do not include the bell in this list (if applicable)
			
			Examples:
			:ref:`pile types pile analysis`
		"""
		properties = self._getPileSegmentsByLength()
		properties.ClearField("segment_list")
		for segment_name, length in segments:
			segment = properties.segment_list.add()
			segment.segment_name = segment_name
			segment.m_length = length
		properties.m_pile_head_elevation = pileHeadElevation
		self._setPileSegmentsByLength(properties)

	def getPileSegmentsByLength(self) -> tuple[float, list[tuple[str, float]]]:
		"""
			returns the pile head elevation followed and a list of tuples, each tuple containing a segment's name and its length
			
			Examples:
			:ref:`pile types pile analysis`
		"""
		properties = self._getPileSegmentsByLength()
		segment_list = [[segment.segment_name, segment.m_length] for segment in properties.segment_list]
		return properties.m_pile_head_elevation, segment_list
	
	def setPileSegmentsByBottomElevation(self, pileHeadElevation : float, segments: list[tuple[str, float]]):
		"""
			segments: list of tuples, each tuple containing a segment's name and its bottom elevation
			Note: Do not include the bell in this list (if applicable)

			Examples:
			:ref:`pile types pile analysis`
		"""
		properties = self._getPileSegmentsByBottomElevation()
		properties.ClearField("segment_list")
		for segment_name, bottom_elevation in segments:
			segment = properties.segment_list.add()
			segment.segment_name = segment_name
			segment.m_bottom_elevation = bottom_elevation
		properties.m_pile_head_elevation = pileHeadElevation
		self._setPileSegmentsByBottomElevation(properties)
	
	def getPileSegmentsByBottomElevation(self) -> tuple[float, list[tuple[str, float]]]:
		"""
			returns the pile head elevation followed and a list of tuples, each tuple containing a segment's name and its bottom elevation
			
			Examples:
			:ref:`pile types pile analysis`
		"""
		properties = self._getPileSegmentsByBottomElevation()
		segment_list = [[segment.segment_name, segment.m_bottom_elevation] for segment in properties.segment_list]
		return properties.m_pile_head_elevation, segment_list