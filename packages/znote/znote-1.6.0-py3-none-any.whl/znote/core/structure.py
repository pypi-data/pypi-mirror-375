import impmagic


#Calcul du chemin d'un fichier
@impmagic.loader(
	{'module':'os'},
	{'module':'os.path', 'submodule':['isabs','abspath']}
)
def path_reg(arg):
	if os.name=='nt':
		path_rep = ["/","\\"]
	else:
		path_rep = ["\\","/"]

	return arg.replace(path_rep[0], path_rep[1])
	"""
	if isabs(arg):
		return arg
	return abspath(arg)
	"""
