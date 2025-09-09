import yaml

def read_metafile(path):
	if os.path.exists(path):
		with open(path, 'r') as file:
			content = yaml.safe_load(file)
			return content
	return {}

def write_metafile(content, path):
	with open(path, 'w') as file:
		yaml.dump(content, file)
