from enum import Enum
from typing import Type, TypeVar, Generic
from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.soil_services.DatumService_pb2 as DatumService_pb2
import RSPileScripting.generated_python_files.soil_services.DatumService_pb2_grpc as DatumService_pb2_grpc
from RSPileScripting.SoilProperties.CommonDatumEnums import eRSPileDatumGroup

T = TypeVar("T", bound=Enum)
class Datum(Generic[T]):
	def __init__(self, model_id: str, soil_id: int, client: Client, datumGroup: eRSPileDatumGroup):
		self._model_id = model_id
		self._soil_id = soil_id
		self._client = client
		self._stub = DatumService_pb2_grpc.DatumServiceStub(self._client.channel)
		self._datum_group = datumGroup
		
	def _getDatumProperty(self, propertyEnum : T) -> float:
		datum_props = DatumService_pb2.DatumProperties(datum_group_enum=self._datum_group.value, datum_property_enum=propertyEnum.value)
		request = DatumService_pb2.GetDatumRequest(
			session_id=self._client.sessionID, soil_id=self._soil_id, datum_props=datum_props)
		datumBottomVal = self._client.callFunction(self._stub.GetDatumProperty, request)
		return datumBottomVal
	
	def getDatum(self, propertyEnum: T) -> float:
		properties = self._getDatumProperty(propertyEnum)
		return properties.datum_bottom_val

	def setDatum(self, propertyEnum: T, valueForBottomOfLayer : float):
		datum_props = DatumService_pb2.DatumProperties(datum_group_enum=self._datum_group.value, datum_property_enum=propertyEnum.value)
		request = DatumService_pb2.SetDatumRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, datum_props=datum_props, datum_bottom_val=valueForBottomOfLayer)
		self._client.callFunction(self._stub.SetDatumProperty, request)
		
	def removeDatum(self, propertyEnum: T):
		datum_props = DatumService_pb2.DatumProperties(datum_group_enum=self._datum_group.value, datum_property_enum=propertyEnum.value)
		request = DatumService_pb2.RemoveDatumRequest(
			session_id=self._client.sessionID, model_id=self._model_id, soil_id=self._soil_id, datum_props=datum_props)
		self._client.callFunction(self._stub.RemoveDatumProperty, request)