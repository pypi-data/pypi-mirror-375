from RSPileScripting._client import Client
import RSPileScripting.generated_python_files.pile_type_services.PileTypeSectionsHelicalService_pb2 as HelicalService_pb2
import RSPileScripting.generated_python_files.pile_type_services.PileTypeSectionsHelicalService_pb2_grpc as HelicalService_pb2_grpc

class Helices:
	"""
		Examples:
		:ref:`pile types helical`
	"""
	def __init__(self, model_id: str, pile_type_id: str, client: Client):
		self._pile_type_id = pile_type_id
		self._client = client
		self._model_id = model_id
		self._stub = HelicalService_pb2_grpc.PileTypeSectionsHelicalServiceStub(self._client.channel)

	def _getPileTypeHelixProperties(self) -> HelicalService_pb2.HelixProperties:
		request = HelicalService_pb2.GetHelixPropertiesRequest(
			session_id=self._client.sessionID, pile_type_id=self._pile_type_id)
		response = self._client.callFunction(self._stub.GetHelixProperties, request)
		return response.helix_props

	def _setPileTypeHelixProperties(self, helixProps: HelicalService_pb2.HelixProperties):
		request = HelicalService_pb2.SetHelixPropertiesRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_type_id=self._pile_type_id, 
			helix_props=helixProps)
		self._client.callFunction(self._stub.SetHelixProperties, request)

	def _getHelicesBySpacing(self) -> HelicalService_pb2.HelicesBySpacingProperties:
		request = HelicalService_pb2.GetHelicesBySpacingRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_type_id=self._pile_type_id)
		response = self._client.callFunction(self._stub.GetHelicesBySpacing, request)
		return response.helices_props	

	def _setHelicesBySpacing(self, helicesProps: HelicalService_pb2.HelicesBySpacingProperties):
		request = HelicalService_pb2.SetHelicesBySpacingRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_type_id=self._pile_type_id,
			helices_props=helicesProps)
		self._client.callFunction(self._stub.SetHelicesBySpacing, request)

	def _getHelicesByDepth(self) -> HelicalService_pb2.HelicesByDepthProperties:
		request = HelicalService_pb2.GetHelicesByDepthRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_type_id=self._pile_type_id)
		response = self._client.callFunction(self._stub.GetHelicesByDepth, request)
		return response.helices_props

	def _setHelicesByDepth(self, helicesProps: HelicalService_pb2.HelicesByDepthProperties):
		request = HelicalService_pb2.SetHelicesByDepthRequest(
			session_id=self._client.sessionID, model_id=self._model_id, pile_type_id=self._pile_type_id, 
			helices_props=helicesProps)
		self._client.callFunction(self._stub.SetHelicesByDepth, request)

	def setHelicesBySpacing(
		self,
		depthOfFirstHelixFromPileHead: float,
		first_helix: tuple[float, float],
		subsequent_helices: list[tuple[float, float, float]]
	):
		"""
		Sets helices properties based on provided specifications.

		Args:
			depthOfFirstHelixFromPileHead (float): Depth of the first helix below the pile head.
			first_helix (tuple): A tuple for the first helix, where:
				- First element (float): Diameter of the first helix.
				- Second element (float): Pitch of the first helix.
			subsequent_helices (list of tuples): A list of tuples for the remaining helices, where:
				- First element (float): Diameter of the helix.
				- Second element (float): Pitch of the helix.
				- Third element (float): Spacing between helices.
		"""
		properties = self._getHelicesBySpacing()
		properties.ClearField("helices_list")

		first_diameter, first_pitch = first_helix
		helix = properties.helices_list.add()
		helix.m_diameter = first_diameter
		helix.m_pitch = first_pitch
		helix.m_spacing = 0  # Enforce spacing as 0 for the first helix

		# Add the subsequent helices
		for diameter, pitch, spacing in subsequent_helices:
			helix = properties.helices_list.add()
			helix.m_diameter = diameter
			helix.m_pitch = pitch
			helix.m_spacing = spacing

		properties.m_helixEmbedmentDepth = depthOfFirstHelixFromPileHead
		self._setHelicesBySpacing(properties)

	def getHelicesBySpacing(self) -> tuple[float, list[tuple[float, float, float]]]:
		"""
			returns the depth of the first helix below the pile head. followed and a list of tuples, each tuple containing a helix's diameter, pitch and spacing
		"""
		properties = self._getHelicesBySpacing()
		helices_list = [[helix.m_diameter, helix.m_pitch, helix.m_spacing] for helix in properties.helices_list]
		return properties.m_helixEmbedmentDepth, helices_list
	
	def setHelicesByDepth(self, helices: list[tuple[float, float, float]]):
		"""
		helices: list of tuples, each tuple containing a helix's diameter, pitch and depth from pile head
		"""
		properties = self._getHelicesByDepth()
		properties.ClearField("helices_list")
		for diameter, pitch, depth in helices:
			helix = properties.helices_list.add()
			helix.m_diameter = diameter
			helix.m_pitch = pitch
			helix.m_depth_from_pile_head = depth
		self._setHelicesByDepth(properties)
	
	def getHelicesByDepth(self) -> list[tuple[float, float, float]]:
		"""
			returns a list of tuples, each tuple containing a helix's diameter, pitch and depth from pile head
		"""
		properties = self._getHelicesByDepth()
		helices_list = [[helix.m_diameter, helix.m_pitch, helix.m_depth_from_pile_head] for helix in properties.helices_list]
		return helices_list

	def getHeightReductionFactor(self) -> float:
		properties = self._getPileTypeHelixProperties()
		return properties.m_heightReductionFactor
	
	def setHeightReductionFactor(self, heightReductionFactor: float):
		properties = self._getPileTypeHelixProperties()
		properties.m_heightReductionFactor = heightReductionFactor
		self._setPileTypeHelixProperties(properties)