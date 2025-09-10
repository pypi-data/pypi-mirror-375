import requests
from . import fsOperations as fso
from multiprocessing import shared_memory, Pool
from . import mem
from . import sub
from . import pub

url = "localhost"
urlStorage = "localhost"
chunk_size = 1048576
workers = 1

def loadRes(path, s = False, load_to_memory = True):
	mem.remove_shm_from_resource_tracker()
	metadata = fso.getMetadata(path)
	segments = []
	for index, resource in enumerate(metadata["resources"]): # GENERA LOS ESPACIOS DE MEMEORIA
		try: # SI YA EXISTEN SE AGREGA UN CAMPO 'local' CON VALOR 'True'
			shm = shared_memory.SharedMemory(name = resource['hash'], create = False)
			metadata["resources"][index]['local'] = True
			shm.close()
		except FileNotFoundError: # SI NO EXISTEN SE AGREGA UN CAMPO 'local' CON VALOR 'False'
			if (load_to_memory):
				mem.createLocalSharedMemorySpace(resource['hash'], resource['size'])
			metadata["resources"][index]['local'] = False
		except Exception as e:
			return
	for file in metadata["resources"]: # OBTENER LOS SEGMENTOS DE LOS ARCHIVOS QUE NO ESTÁN EN MEMORIA
		if(file['local'] == False or file['local'] == True):
			segments+=fso.array_of_segments(file['size'], file["path"], file['hash'], chunk_size)

	if (load_to_memory):
		with Pool(processes = workers) as p: # CARGARLOS EN MEMORIA A TRAVÉS DE TRABAJADORES
			p.map(mem.loadToLocalSharedMemory, segments)
	
	for index, resource in enumerate(metadata["resources"]):
		if(resource['local'] == False):
			metadata["resources"][index]['local'] = True
	if s:
		return metadata, segments
	else: 
		return metadata

def loadAndUploadToCloud(path, res = False, segments = False):
	if (not res and not segments):
		res, segments = loadRes(path, True)
	else:
		mem.remove_shm_from_resource_tracker()
	for index, resource in enumerate(res["resources"]):
		verification = verify(resource['hash'])
		print(verification)
		if (verification):
			if (verification['file']['state']=="reserving"):
				sub.subToTopic(resource['hash'])
				verification['file']['state']="ready"
				res['resources'][index] = verification['file']
			elif (verification['file']['state']=="ready"):
				res['resources'][index] = verification['file']
				pass
			else:
				return False
		else:
			resource.pop("local")
			resource['state'] = "reserving"
			register = registry(resource)
			pub.pubTopic(resource['hash'], "loading")
			if (register["created"]):
				response_reserve = requests.post(f"{urlStorage}/reserve", json={"name":resource['hash'], "size": resource['size']})
				segments_res = list(filter(lambda x : f"{x['segment']}" == resource['hash'], segments))
				for segment in segments_res:
					
					print(segment)
					data = None
					with open(segment['origin'], "rb") as file:
						file.seek(segment['start_position'])
						data = file.read(segment['chunk_size'])
					files = {"files": data}
					segment['segment'] = f"{segment['segment']}" #REMOVER DESPUES DE EXPERMIMENTACIÓN
					response_fill = requests.post(f"{urlStorage}/fill", files = files, data = segment)
				resUpdateState = update(resource['hash'], "ready")
				pub.pubTopic(resource['hash'], "ready")
	return res

def uploadToCloud(path, res = False, segments = False):
	if (not res and not segments):
		res, segments = loadRes(path, True, False)
	else:
		mem.remove_shm_from_resource_tracker()
	for index, resource in enumerate(res["resources"]):
		el_hash = f"{resource['hash']}"
		verification = verify(el_hash)
		if (verification):
			if (verification['file']['state']=="reserving"):
				print("Cargando archivo al servidor")
				sub.subToTopic(el_hash)
				verification['file']['state']="ready"
				res['resources'][index] = verification['file']
			elif (verification['file']['state']=="ready"):
				res['resources'][index] = verification['file']
				print("Archivo listo para consumo")
				pass
			else:
				return False
		else:
			if 'local' in resource: resource.pop("local")
			resource['state'] = "reserving"
			register = registry(resource)
			pub.pubTopic(el_hash, "loading")
			if (register["created"]):
				response_reserve = requests.post(f"{urlStorage}/reserve", json={"name":el_hash, "size": resource['size']})
				segments_res = list(filter(lambda x : f"{x['segment']}" == el_hash, segments))
				for segment in segments_res:
					data = None
					data = mem.getChunk(segment['segment'], segment['start_position'], segment['end_position'])
					files = {"files": data}
					segment['segment'] = f"{segment['segment']}"
					response_fill = requests.post(f"{urlStorage}/fill", files = files, data = segment)
				resUpdateState = update(el_hash, "ready")
				pub.pubTopic(el_hash, "ready")
	return res

def uploadToCloudFromDisk(path):
	res, segments = loadRes(path, True, False)
	for index, resource in enumerate(res["resources"]):
		el_hash = f"{resource['hash']}"
		verification = verify(el_hash)
		if (verification):
			if (verification['file']['state']=="reserving"):
				sub.subToTopic(el_hash)
				verification['file']['state']="ready"
				res['resources'][index] = verification['file']
			elif (verification['file']['state']=="ready"):
				res['resources'][index] = verification['file']
				pass
			else:
				return False
		else:
			if 'local' in resource: resource.pop("local")
			resource['state'] = "reserving"
			resource['hash'] = el_hash
			register = registry(resource)
			pub.pubTopic(el_hash, "loading")
			if (register["created"]):
				response_reserve = requests.post(f"{urlStorage}/reserve", json={"name":el_hash, "size": resource['size']})
				segments_res = list(filter(lambda x : f"{x['segment']}" == el_hash, segments))
				for segment in segments_res:
					data = None
					with open(segment['origin'], "rb") as file:
						file.seek(segment['start_position'])
						data = file.read(segment['chunk_size'])
					files = {"files": data}
					segment['segment'] = f"{segment['segment']}"
					response_fill = requests.post(f"{urlStorage}/fill", files = files, data = segment)
				resUpdateState = update(el_hash, "ready")
				pub.pubTopic(el_hash, "ready")
	return res

def downloadFromCloud(hash):
	mem.remove_shm_from_resource_tracker()
	md = verify(hash)
	md = md['file']
	original_hash = md['hash']
	hash_aux = md['hash']
	mem.createLocalSharedMemorySpace(md['hash'], md['size'])
	segments_to_get = fso.array_of_segments_for_server_file(md['size'], original_hash, chunk_size)
	for segment in segments_to_get:
		response = requests.post(f"{urlStorage}/chunk", data = segment)
		mem.loadDowloadedToLocalSharedMemory(md['hash'], segment['start_position'], segment['end_position'], response.content)
	return {"message": True}

def verify(hash):
	try:
		response = requests.post(f"{url}/hash", json = {"hash": hash})
		if response.json()['registered']:
			return response.json()
		else: 
			return False
	except requests.exceptions.RequestException as err:
		return {"message": "Error"}

def update(hash, state):
	try:
		response = requests.post(f"{url}/update-file-state", json = {"hash": hash, "state": state})
		if response.json():
			return response.json()
		else: 
			return False
	except requests.exceptions.RequestException as err:
		return {"message": "Error"}

def registry(rmd):
	try:
		response = requests.post(f"{url}/register-file", json=rmd)
		return response.json()
	except requests.exceptions.RequestException as err:
		pass

def removeShm(shm_name):
	mem.removeShm(shm_name)

def getRes(file):
	return mem.getData(file)

def saveFile(path, data, name):
	fso.saveFile(path, data, name)

def setWorkers(w):
	global workers 
	workers = w

def setChunkSize(cs):
	global chunk_size
	chunk_size = cs

def setUrl(u):
	global url
	url = u

def setStorageUrl(u):
	global urlStorage
	urlStorage = u

def getWorkers():
	return workers

def getChunkSize():
	return chunk_size

def getUrl():
	return url

def getStorageUrl():
	return urlStorage

def setBrokerUrl(url):
	pub.setBrokerUrl(url)
	sub.setBrokerUrl(url)

def setBrokerPort(p):
	pub.setBrokerPort(p)
	sub.setBrokerPort(p)