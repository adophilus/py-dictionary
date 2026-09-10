import json

def unjsonize(json_data, *args, **kwargs):
	return json.loads(json_data, *args, **kwargs)

def jsonize(dict_object, *args, **kwargs):
	return json.dumps(dict_object, *args, **kwargs)

def loadJson (path, *args, **kwargs):
	with open(path, "r") as file:
		return unjsonize(file.read(), *args, **kwargs)

def saveJson (path, data, *args, **kwargs):
	with open(path, "w") as file:
		file.write(jsonize(data, *args, **kwargs))

def putContentIn (filePath, data):
	with open(filePath, "w") as file:
		file.write(data)

def getContentOf (filePath):
	with open(filePath, "r") as file:
		return file.read()

def getContentOfBinary (filePath):
	with open(filePath, "rb") as file:
		return file.read()

def sendTrue (data):
	return jsonize({"data": data, "status": True})

def sendFalse (data):
	return jsonize({"error": data, "status": False})

def getIpAddress ():
	return ""
