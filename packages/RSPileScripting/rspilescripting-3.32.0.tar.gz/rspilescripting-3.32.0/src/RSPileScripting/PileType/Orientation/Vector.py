from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_type_services.PileTypeOrientationVectorService_pb2 as PileTypeOrientationVectorService_pb2
import RSPileScripting.generated_python_files.pile_type_services.PileTypeOrientationVectorService_pb2_grpc as PileTypeOrientationVectorService_pb2_grpc

class Vector:
	"""
		Examples:
		:ref:`pile types pile analysis`
	"""
	def __init__(self, model_id: str, pile_type_id: str, client: Client):
		self.pile_type_id = pile_type_id
		self._client = client
		self._model_id = model_id
		self._stub = PileTypeOrientationVectorService_pb2_grpc.PileTypeOrientationVectorServiceStub(self._client.channel)

	def _getPileTypeVectorProperties(self) -> PileTypeOrientationVectorService_pb2.VectorProperties:
		request = PileTypeOrientationVectorService_pb2.GetVectorPropertiesRequest(
			session_id=self._client.sessionID, pile_type_id=self.pile_type_id)
		response = self._client.callFunction(self._stub.GetVectorProperties, request)
		return response.vector_props

	def _setPileTypeVectorProperties(self, vectorProps: PileTypeOrientationVectorService_pb2.VectorProperties):
		request = PileTypeOrientationVectorService_pb2.SetVectorPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_type_id=self.pile_type_id, 
			vector_props=vectorProps)
		self._client.callFunction(self._stub.SetVectorProperties, request)

	def setVector(self, vector: list[3]):
		"""Sets the orientation vector of the pile type. Vector will be converted to a unit vector

		Args:
			vector (list[3]): A list of 3 floats representing the x, y, and z components of the vector.
		"""
		properties = self._getPileTypeVectorProperties()
		vector3d = PileTypeOrientationVectorService_pb2.Vector3D(x=vector[0], y=vector[1], z=vector[2])
		properties.vector.CopyFrom(vector3d)
		self._setPileTypeVectorProperties(properties)

	def getVector(self) -> list[3]:
		"""Gets the orientation vector of the pile type. The returned vector is a unit vector.

		Returns:
			list[3]: A list of 3 floats representing the x, y, and z components of the vector.
		"""
		properties = self._getPileTypeVectorProperties()
		vector3d = properties.vector
		return [vector3d.x, vector3d.y, vector3d.z]