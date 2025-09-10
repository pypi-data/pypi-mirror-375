from multiprocessing import shared_memory, Pool
from multiprocessing import resource_tracker

def createLocalSharedMemorySpace(name, size):
	# self.remove_shm_from_resource_tracker()
	shm = shared_memory.SharedMemory(create=True, size = size, name = name)
	resource_tracker.unregister(shm._name, 'shared_memory')
	shm.close()
	return shm.name

def loadToLocalSharedMemory(segment):
	shm = shared_memory.SharedMemory(name = segment['segment'], create=False)
	with open(segment['origin'], "rb") as file:
		file.seek(segment['start_position'])
		shm.buf[segment['start_position']:segment['end_position']] = file.read(segment['chunk_size'])
	shm.close()

def loadDowloadedToLocalSharedMemory(shm_name, start_position, end_position, data):
	shm = shared_memory.SharedMemory(name = shm_name, create=False)
	shm.buf[start_position:end_position] = data
	shm.close()

def getChunk(shm_name, start_position, end_position):
	shm = shared_memory.SharedMemory(name = shm_name, create=False)
	data = bytes(shm.buf[int(start_position):int(end_position)])
	shm.close()
	return data

def getData(file):
	shm = shared_memory.SharedMemory(name = file, create=False)
	data = bytes(shm.buf[:])
	shm.close()
	return data

def removeShm(shm_name):
	shm = shared_memory.SharedMemory(name = shm_name, create=False)
	shm.close()
	shm.unlink()

def remove_shm_from_resource_tracker():
	"""Monkey-patch multiprocessing.resource_tracker so SharedMemory won't be tracked

	More details at: https://bugs.python.org/issue38119
	"""

	def fix_register(name, rtype):
		if rtype == "shared_memory":
			return
		return resource_tracker._resource_tracker.register(self, name, rtype)
	resource_tracker.register = fix_register

	def fix_unregister(name, rtype):
		if rtype == "shared_memory":
			return
		return resource_tracker._resource_tracker.unregister(self, name, rtype)
	resource_tracker.unregister = fix_unregister

	if "shared_memory" in resource_tracker._CLEANUP_FUNCS:
		del resource_tracker._CLEANUP_FUNCS["shared_memory"]