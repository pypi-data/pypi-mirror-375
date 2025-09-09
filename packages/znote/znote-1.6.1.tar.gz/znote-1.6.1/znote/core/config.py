import os
import yaml
import impmagic

class Config:
    def __init__(self, path):
        self.path = os.path.expanduser(path)
        self.data = {}
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = yaml.safe_load(f) or {}
        else:
            self.data = {}

    def _save(self):
        directory = os.path.dirname(self.path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(self.path, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.data, f, default_flow_style=False, sort_keys=False)

    def _get_recursive(self, data, keys):
        if len(keys) == 1:
            return data.get(keys[0])
        if keys[0] in data:
            return self._get_recursive(data[keys[0]], keys[1:])
        return None

    def _set_recursive(self, data, keys, value):
        if len(keys) == 1:
            data[keys[0]] = value
            return data
        if keys[0] not in data or not isinstance(data[keys[0]], dict):
            data[keys[0]] = {}
        data[keys[0]] = self._set_recursive(data[keys[0]], keys[1:], value)
        return data

    def get(self, dotted_key=None, default=None, auto_set=False):
        if not dotted_key:
            return self.data
        
        keys = dotted_key.split(".")
        result = self._get_recursive(self.data, keys)

        if result is not None:
            return result

        if auto_set:
            self.set(dotted_key, default)
            return default

        return default

    def set(self, dotted_key, value):
        keys = dotted_key.split(".")
        self.data = self._set_recursive(self.data, keys, value)
        self._save()

    def delete(self, dotted_key):
        keys = dotted_key.split(".")
        parent = self._get_recursive(self.data, keys[:-1])
        if parent and keys[-1] in parent:
            del parent[keys[-1]]
            # Nettoie récursivement si parent vide :
            while keys[:-1]:
                keys = keys[:-1]
                parent = self._get_recursive(self.data, keys[:-1])
                if parent and not parent.get(keys[-1]):
                    del parent[keys[-1]]
            self._save()

    def has(self, dotted_key):
        return self.get(dotted_key) is not None


@impmagic.loader(
    {'module':'__main__'},
    {'module':'zpp_args'},
    {'module':'sys'},
    {'module':'app.display', 'submodule': ['logs', 'print_nxs']},
    {'module':'shutil', 'submodule': ['copyfile']},
    {'module':'os', 'submodule': ['remove', 'name']}
)
def config_znote():
    parse = zpp_args.parser(sys.argv[1:])
    parse.command = "nxs config"
    parse.set_description("Affichage/Modification de la configuration de nexus")
    parse.set_argument(longname="disable", description="Désactive le paramètre", default=False)
    parse.set_argument(longname="enable", description="Active le paramètre masqué", default=False)
    parse.disable_check()
    parameter, argument = parse.load()

    if parameter!=None:
        #data = __main__.settings.config.load(section='')
        if len(parameter)==0:
            for cat, cat_info in __main__.settings.config.get().items():
                print_nxs(f"\n#{cat}", color='dark_gray')
                for key, value in cat_info.items():
                    print_nxs(f"{key}: ", nojump=True)
                    print_nxs(value, color='yellow')

        else:
            parameter[0] = parameter[0].lower()
            if __main__.settings.config.get(parameter[0])!=None:
                if isinstance(__main__.settings.config.get(parameter[0]), bool):
                    if __main__.settings.config.get(parameter[0])==True:
                        __main__.settings.config.set(parameter[0], False)
                        logs(f"Passage de {parameter[0]} à False", force=True)  
                    else:
                        __main__.settings.config.set(parameter[0], True)
                        logs(f"Passage de {parameter[0]} à True", force=True)
                else:
                    if len(parameter)>1:
                        if isinstance(__main__.settings.config.get(parameter[0]), int):
                            parameter[1] = int(parameter[1])
                        elif isinstance(__main__.settings.config.get(parameter[0]), float):
                            parameter[1] = float(parameter[1])

                        __main__.settings.config.set(parameter[0], parameter[1])
                        logs(f"Passage de {parameter[0]} à {parameter[1]}", force=True)
                    else:
                        logs(f"Valeur manquante pour {parameter[0]}", "error", force=True)  
            else:
                logs(f"Paramètre {parameter[0]} introuvable", "error", force=True)  

