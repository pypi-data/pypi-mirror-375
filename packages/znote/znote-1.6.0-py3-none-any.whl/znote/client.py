import __main__
import impmagic
import threading


@impmagic.loader(
    {'module': 'chardet'},
)
def decode(message):
    if chardet.detect(message)['encoding']!=None:
        return message.decode(chardet.detect(message)['encoding'])
    else:
        return message.decode()


class Client():
    def __init__(self, conn):
        threading.Thread.__init__(self)
        self.connexion = conn
        self.killed = False
        self.well_come = False

    @impmagic.loader(
        {'module': 'Crypto.Cipher', 'submodule': ['PKCS1_OAEP']},
        {'module': 'cryptography.hazmat.backends', 'submodule': ['default_backend']},
        {'module': 'cryptography.hazmat.primitives.ciphers', 'submodule': ['Cipher', 'algorithms', 'modes']}
    )
    def decrypt_data(self, message):
        iv = message[:16]
        sym_key_encrypted = message[16:272]  # Taille de la clé RSA (2048 bits) / 8
        ciphertext = message[272:]

        # Déchiffrement de la clé symétrique avec RSA
        decryptor = PKCS1_OAEP.new(__main__.settings.key)
        sym_key = decryptor.decrypt(sym_key_encrypted)

        # Déchiffrement du fichier avec AES en mode CFB
        cipher = Cipher(algorithms.AES(sym_key), modes.CFB(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        return plaintext


    #Réception des données
    @impmagic.loader(
        {'module': 'select'},
        {'module': 'time'}
    )
    def receive(self):
        data = b""

        #Boucle pour récupérer l'ensemble des chunk d'un message
        while True:
            #Pour éviter les exceptions avec le socket non 
            #A voir si ça crash pas si on reçoit de gros fichiers
            ready_to_read, _, _ = select.select([self.connexion], [], [], 1)
            if ready_to_read:
                chunk = self.connexion.recv(2048)

                if len(chunk):
                    if not chunk.endswith(b'EOF'):
                        data += chunk
                    else:
                        return data+chunk[:-3]
                else:
                    time.sleep(0.2)
                """
                if chunk:
                    print(chunk)
                if chunk and len(chunk)<2048:
                    return data+chunk

                if not chunk:
                    return data

                data += chunk
                """


    @impmagic.loader(
        {'module': 'os'},
        {'module': 'core.gen', 'submodule': ['gen_password']},
        {'module': 'Crypto.Cipher', 'submodule': ['PKCS1_OAEP']},
        {'module': 'cryptography.hazmat.backends', 'submodule': ['default_backend']},
        {'module': 'cryptography.hazmat.primitives.ciphers', 'submodule': ['Cipher', 'algorithms', 'modes']}
    )
    def send(self, message):
        if not isinstance(message, bytes):
            message = message.encode()

        # Génération de la clé symétrique (AES) et de l'IV
        #sym_key = os.urandom(32)  # 256 bits
        sym_key = gen_password(32)  # 256 bits
        iv = os.urandom(16)  # IV de 128 bits pour AES

        # Chiffrement du fichier avec AES en mode CFB
        plaintext = message

        cipher = Cipher(algorithms.AES(sym_key), modes.CFB(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        ciphertext = encryptor.update(plaintext) + encryptor.finalize()

        # Chiffrement de la clé symétrique avec RSA
        encryptor = PKCS1_OAEP.new(__main__.settings.keyC)
        sym_key_encrypted = encryptor.encrypt(sym_key)

        # Sauvegarde du IV, de la clé symétrique chiffrée et du fichier chiffré
        message_cipher = iv + sym_key_encrypted + ciphertext

        self.connexion.send(message_cipher + b'EOF')


    #Premier appel avec le serveur
    @impmagic.loader(
        {'module': 'hashlib'},
        {'module': 'app.display', 'submodule': ['logs', 'notify']},
        {'module': 'core.client.connect', 'submodule': ['encrypt', 'decrypt']},
        {'module': 'Crypto.PublicKey', 'submodule': ['RSA']},
    )
    def welcome(self):
        if __main__.settings.token:
            payload = {'method': 'welcome', 'token': __main__.settings.token, 'serverhash': __main__.settings.serverhash, 'clienthash': __main__.settings.clienthash}
            logs("Envoi du welcome au serveur", component="client")

        else:
            payload = {'method': 'sendKey', 'content': __main__.settings.PubKey.decode()}
            logs("Envoi de la clé public au serveur", component="client")

        self.connexion.send(encrypt(json.dumps(payload).encode()) + b'EOF')

        try:
            message_recu = self.receive()

        except:
            if self.killed:
                logs(f"Arrêt du thread demandé", component="client")
            else:
                logs(f"Erreur avec le client. Arret de la connexion", "error", component="client")

        if message_recu!=b'':
            msg = decrypt(decode(message_recu))
            msg = json.loads(msg)

            if msg['method']=="sendKey":
                __main__.settings.PubServ = msg['content'].encode()
                try:
                    #print("Connexion réussi")
                    __main__.settings.keyC = RSA.importKey(__main__.settings.PubServ)

                    #Enregistrement de la clé public du serveur
                    pubkey_path = os.path.join(__main__.settings.config_dir, "server.pub")
                    with open(pubkey_path, "wb") as f:
                        f.write(__main__.settings.PubServ)

                    #Calcul du hash de la clé du serveur
                    __main__.settings.serverhash = hashlib.sha256(__main__.settings.PubServ).hexdigest()

                    __main__.settings.pubserv_set = True

                except Exception as err:
                    __main__.settings.PubServ=None
                    __main__.settings.pubserv_set = False
            
            elif msg['method']=="welcome":
                if 'message' in msg:
                    notify(msg['message'], "error")

                if 'status' in msg:
                    if msg['status']==0:
                        __main__.settings.pubserv_set = False
                        #self.welcome()
                    
                    elif msg['status']==2:
                        if os.path.exists(__main__.settings.token_file):
                            os.remove(__main__.settings.token_file)
                        exit()


    @impmagic.loader(
        {'module': '__main__'},
        {'module': 'app.input', 'submodule': ['getpass']},
        {'module': 'app.display', 'submodule': ['notify']},
    )
    def get_note_content(self, note, payload=None):
        if payload:
            command = payload

        else:
            command = {
                'method': 'note',
                'action': 'get',
                'note': note,
                'token': __main__.settings.token
            }

        message = self.call_server(command)

        if message['method']=="note":
            if 'content' in message:
                return message['content']

        elif message['method']=="password_required":
            password = getpass("Password: ")
            command['password_hash'] = hashlib.sha256(password.encode()).hexdigest()
            
            return self.get_note_content(note, payload=command)

        elif message['method']=="notify":
            if 'message' in message and 'status_code' in message:
                notify(message['message'], message['status_code'])


        return ""

    @impmagic.loader(
        {'module': '__main__'},
    )
    def verify_hash_file(self, channel_name, filename, hash_file):
        command = {
            'method': 'channel',
            'action': 'check_hash',
            'channel_name': channel_name,
            'name': filename,
            'hash_file': hash_file,
            'token': __main__.settings.token
        }

        message = self.call_server(command)

        if message['method']=="channel":
            if 'success' in message:
                return message['success']

        return False


    @impmagic.loader(
        {'module': '__main__'},
        {'module': 'hashlib'},
        {'module': 'app.display', 'submodule': ['logs']},
    )
    def publish_file(self, file, expanded_path, channel_name):
        if expanded_path:
            filename = os.path.relpath(file, expanded_path)
        else:
            filename = os.path.basename(file)

        logs(f"Envoi de {filename}")
        with open(file, 'rb') as f:
            content = f.read()
            content_hash = hashlib.sha256(content).hexdigest()

            if not self.verify_hash_file(channel_name, filename, content_hash):
                command = {
                    'method': 'channel',
                    'action': 'publish',
                    'channel_name': channel_name,
                    'name': filename,
                    'content': content,
                    'hash': content_hash,
                    'token': __main__.settings.token
                }

                message = self.call_server(command)
                if message['method']=="notify":
                    if 'message' in message and 'status_code' in message:
                        logs(message['message'], lvl=message['status_code'])

            else:
                logs(f"{filename} déjà à jour", "info")


    #Envoie une commande au serveur et attends une réponse
    @impmagic.loader(
        {'module': '__main__'},
        {'module': 'app.display', 'submodule': ['logs']},
        {'module': 'core.pack', 'submodule': ['pack', 'unpack']},
    )
    def call_server(self, command):
        if not self.well_come:
            self.welcome()
            self.well_come = True

        message = None
        #if not __main__.settings.pubserv_set:
        #if not __main__.settings.serverhash:

        if not __main__.settings.pubserv_set:
            return None
        #exit()
        #try:
        self.send(pack(command, __main__.settings.key))

        try:
            message_recu = self.receive()
            
        except:
            if self.killed:
                logs(f"Arrêt du thread demandé", component="client")
            else:
                logs(f"Erreur avec le client. Arret de la connexion", "error", component="client")
            exit()

        if message_recu!=b'':
            message = self.decrypt_data(message_recu)
            message = unpack(message, __main__.settings.keyC)

        return message
        

    @impmagic.loader(
        {'module': '__main__'},
        {'module': 'json'},
        {'module': 'os'},
        {'module': 'hashlib'},
        {'module': 'glob', 'submodule': ['glob']},
        {'module': 'core.editor', 'submodule': ['Editor']},
        {'module': 'app.display', 'submodule': ['logs', 'notify', 'print_nxs', 'SaveScreen', 'RestoreScreen']},
        {'module': 'core.pack', 'submodule': ['pack']},
        {'module': 'zpp_color', 'submodule': ['fg', 'attr']},
        {'module': 'app.input', 'submodule': ['getpass']},
        {'module': 'zpp_ManagedFile', 'submodule': ['ManagedFile']}
    )
    def run(self, argument, parameter):
        command = None

        if argument!=None and len(parameter):
            instruction = parameter[0]

            if instruction=="login":
                username = input("Username: ")
                password = getpass("Password: ")

                command = {
                    'method': 'authentication',
                    'username': username,
                    'password': password
                }

                __main__.settings.token = None
                if os.path.exists(__main__.settings.token_file):
                    os.remove(__main__.settings.token_file)

            elif instruction=="status":
                command = {
                    'method': 'status',
                    'token': __main__.settings.token
                }

            elif instruction=="logout":
                command = {
                    'method': 'logout',
                    'token': __main__.settings.token
                }

                if os.path.exists(__main__.settings.token_file):
                    os.remove(__main__.settings.token_file)

            elif instruction=="workspace":
                command = {
                    'method': 'workspace',
                    'token': __main__.settings.token
                }

                if len(parameter)>1:
                    command['workspace'] = parameter[1]

                    if argument.create:
                        command['action'] = 'create'
                    
                    elif argument.remove:
                        command['action'] = 'remove'
            
            elif instruction=="add" or instruction=="edit":
                if len(parameter)>1:
                    command = {
                        'method': 'note',
                        'action': instruction,
                        'note': parameter[1],
                        'token': __main__.settings.token
                    }

                    try:
                        file = ManagedFile(mode='a', typefile='stringio')

                        if instruction=="edit":
                            file.write(self.get_note_content(parameter[1]))
                            file.seek(0)

                        SaveScreen()
                        editor = Editor(filename=parameter[1], file=file)
                        editor.app.run()
                        RestoreScreen()
                        file.seek(0)

                        command['content'] = file.read()

                    except Exception as e:
                        command = None
                        logs(f"An unexpected error occurred: {e}", "error")

            elif instruction=="view" or instruction=="pull":
                if len(parameter)>1:
                    content_note = self.get_note_content(parameter[1])

                    if instruction=="view":
                        print(content_note)

                    elif instruction=="pull":
                        if len(parameter)>2:
                            filename = parameter[2]

                            if os.path.exists(filename):
                                notify(f"Le fichier {filename} existe déjà", "error")

                            with open(filename, "w") as f:
                                f.write(content_note)
            
            elif instruction=="push":
                if len(parameter)>1:
                    filename = parameter[1]

                    if os.path.exists(filename):
                        with open(filename, "r") as f:
                            content_note = f.read()

                        if len(parameter)>2:
                            note_name = parameter[2]
                        else:
                            note_name = os.path.basename(filename)


                        command = {
                            'method': 'note',
                            'action': "add",
                            'note': note_name,
                            'content': content_note,
                            'token': __main__.settings.token
                        }

            elif instruction=="remove":
                if len(parameter)>1:
                    command = {
                            'method': 'note',
                            'action': "remove",
                            'note': parameter[1],
                            'token': __main__.settings.token
                        }

            elif instruction=="list":
                command = {
                    'method': 'note',
                    'action': 'list',
                    'note': '',
                    'token': __main__.settings.token
                }

            elif instruction=="info":
                if len(parameter)>1:
                    command = {
                            'method': 'note',
                            'action': 'info',
                            'note': parameter[1],
                            'token': __main__.settings.token
                        }

            elif instruction=="find":
                if len(parameter)>1:
                    command = {
                            'method': 'note',
                            'action': 'find',
                            'pattern': parameter[1],
                            'token': __main__.settings.token
                        }

            elif instruction=="protect":
                if len(parameter)>1:
                    password = getpass("Password: ")
                    note_password = hashlib.sha256(password.encode()).hexdigest()

                    command = {
                            'method': 'note',
                            'action': 'protect',
                            'note': parameter[1],
                            'password_hash': note_password,
                            'token': __main__.settings.token
                        }

            elif instruction=="channel":
                command = {
                    'method': 'channel',
                    'action': 'list',
                    'token': __main__.settings.token
                }

                if len(parameter)>1:
                    if argument.detail:
                        command['action'] = 'info'
                    
                    elif argument.tree:
                        command['action'] = 'tree'

                    command['channel_name'] = parameter[1]

            elif instruction=="fetch":
                if len(parameter)>1:
                    command = {
                        'method': 'channel',
                        'action': 'fetch',
                        'channel_name': parameter[1],
                        'token': __main__.settings.token
                    }

                    if len(parameter)>2:
                        command['path'] = parameter[2]

                    if argument.force:
                        command['force'] = True
                    else:
                        command['force'] = False

                    if argument.purge:
                        command['purge'] = True
                    else:
                        command['purge'] = False

                    if argument.file:
                        command['file'] = argument.file

            elif instruction=="diff":
                if len(parameter)>1:
                    command = {
                        'method': 'channel',
                        'action': 'diff',
                        'channel_name': parameter[1],
                        'token': __main__.settings.token
                    }

                    if len(parameter)>2:
                        command['path'] = parameter[2]

            elif instruction=="unpublish":
                if len(parameter)>1:
                    command = {
                        'method': 'channel',
                        'action': 'unpublish',
                        'channel_name': parameter[1],
                        'token': __main__.settings.token
                    }

            elif instruction=="publish":
                channel_name = parameter[1]
                path = parameter[2]

                expanded_path = os.path.expanduser(path)

                if not os.path.exists(expanded_path):
                    logs("La source n'existe pas", "error")

                if os.path.isdir(expanded_path):
                    files = glob(f"{expanded_path}/**/*", recursive=True)
                    #files = [os.path.relpath(p, expanded_path) for p in results]
                else:
                    files = [expanded_path]
                    expanded_path = None

                push_file = []

                exclude_dir = __main__.settings.exclude_dir.split(",")

                if argument.exclude:
                    exclude_file = argument.exclude.split(",")
                else:
                    exclude_file = []

                for file in files:
                    if os.path.basename(os.path.dirname(file)) not in exclude_dir and os.path.relpath(file, expanded_path) not in exclude_file:
                        if os.path.isfile(file):
                            push_file.append(os.path.relpath(file, expanded_path))
                            self.publish_file(file, expanded_path, channel_name)

                if argument.purge:
                    logs("Purge du channel", "info")
                    command = {
                        'method': 'channel',
                        'action': 'purge',
                        'channel_name': parameter[1],
                        'list_files': push_file,
                        'token': __main__.settings.token
                    }

        if command:
            self.send_and_response(command)


    @impmagic.loader(
        {'module': '__main__'},
        {'module': 'core.client.fetch', 'submodule': ['remove_unlisted_files', 'build_diff_tree']},
        {'module': 'core.client.metafile', 'submodule': ['read_metafile', 'write_metafile']},
        {'module': 'app.display', 'submodule': ['logs', 'notify', 'print_nxs', 'build_tree', 'print_tree']},
        {'module': 'core.pack', 'submodule': ['pack']},
        {'module': 'core.structure', 'submodule': ['path_reg']},
        {'module': 'core.client.token', 'submodule': ['set_token']},
        {'module': 'app.input', 'submodule': ['getpass']},
    )
    def send_and_response(self, command):
        message = self.call_server(command)

        if message['method']=="setToken":
            if 'content' in message:
                __main__.settings.token = message['content']
                set_token(__main__.settings.token)
                logs(f"Reception du token", component="client")
                notify("Connecté", "success")
            else:
                logs("Token invalide", "error")
        
        elif message['method']=="workspace":
            if 'content' in message:
                for element in message['content']:
                    if 'active' in message and element==message['active']:
                        print(f"* {element}")
                    else:
                        print(f"  {element}")

        elif message['method']=="status":
            for element in ['connected', 'workspace', 'notes']:
                if element in message:
                    print_nxs(f"{element}: ", color='dark_gray',nojump=True)

                    if isinstance(message[element], bool):
                        if message[element]==True:
                            print_nxs(message[element], color="green")
                        else:
                            print_nxs(message[element], color="light_red")

                    else:
                        print_nxs(message[element])
        
        elif message['method']=="list":
            if 'notes' in message:
                for note in message['notes']:
                    print(f" - {note}")
        
        elif message['method']=="info":
            if 'note' in message:
                for key, value in message['note'].items():
                    print_nxs(f"{key}: ", color='dark_gray',nojump=True)
                    print_nxs(value)

        elif message['method']=="find":
            if 'content' in message:
                for note in message['content']:
                    print(f" - {note}")

        elif message['method']=="notify":
            if 'message' in message and 'status_code' in message:
                notify(message['message'], message['status_code'])
        
        elif message['method']=="password_required" and 'payload' in message:
            password = getpass("Password: ")
            payload = message['payload']

            payload['password_hash'] = hashlib.sha256(password.encode()).hexdigest()
            
            self.send_and_response(payload)
        
        elif message['method']=="channel":
            if 'action' in message and message['action']=="fetch":
                if 'tree' in message:
                    list_files = []
                    for file in message['tree']:
                        #Spécifie le chemin de destination
                        if 'path' in message:
                            if 'file' in message:
                                file_path = message['path']
                            else:
                                file_path = os.path.join(message['path'], file['name'])
                        else:
                            file_path = file['name']

                        file_path = path_reg(file_path)

                        list_files.append(file['name'])

                        #Forcer la mise à jour du contenu
                        if 'force' in message:
                            force = message['force']
                        else:
                            force = False

                        #Supprimer les fichiers non présent dans le channel
                        if 'purge' in message:
                            purge = message['purge']
                        else:
                            purge = False

                        if 'file' not in message and not os.path.exists(os.path.dirname(file_path)):
                            os.makedirs(os.path.dirname(file_path), exist_ok=True)

                        content_hash = None
                        if os.path.exists(file_path):
                            with open(file_path, 'rb') as f:
                                content_hash = hashlib.sha256(f.read()).hexdigest()

                        if content_hash and content_hash==file['content_hash'] and not force:
                            pass
                        else:
                            with open(path_reg(file_path), 'wb') as f:
                                f.write(file['content'])
                                if content_hash:
                                    logs(f"{file['name']} mis à jour", "success", force=True)
                                else:
                                    logs(f"{file['name']} récupéré", "success", force=True)

                    if purge:
                        if 'path' in message:
                            file_path = message['path']
                        else:
                            file_path = "."
                        #expanded_path = os.path.expanduser(file_path)
                        list_files = [p.replace('\\', '/') for p in list_files]

                        remove_unlisted_files(file_path, list_files)

                """
                if 'channel_hash' in message:
                    if 'path' in message:
                        file_path = os.path.join(message['path'], '.znote')
                    else:
                        file_path = ".znote"

                    content = {
                        "channel_name": message['channel_name'],
                        "channel_hash": message['channel_hash'],
                    }

                    write_metafile(content, file_path)
                """

            elif 'action' in message and message['action']=="diff":
                if 'tree' in message:
                    if 'path' in message:
                        file_path = message['path']
                    else:
                        file_path = "."

                    diff_output = build_diff_tree(file_path, message["tree"])
                    print_tree(diff_output)
            

            elif 'action' in message and message['action']=="list":
                if 'channel_list' in message:
                    for channel_name in message['channel_list']:
                        print_nxs("  - ", color='dark_gray',nojump=True)
                        print_nxs(channel_name)

            elif 'action' in message and message['action']=="info":
                if 'channel_info' in message:
                    for element in ['name', 'description', 'hash', 'updated_at', 'total_files']:
                        if element in message['channel_info'] and message['channel_info'][element]:
                            print_nxs(f"{element}: ", color='dark_gray',nojump=True)
                            print_nxs(message['channel_info'][element])

            elif 'action' in message and message['action']=="tree":
                if 'list_files' in message:
                    tree = build_tree(message['list_files'])
                    print_tree(tree)
            
        else:
            print(message)

        self.send(pack({'method': 'endSession'}, __main__.settings.key))
        """
        except Exception as err:
            logs(err, "error", component="client")

        finally:
            self.connexion.close()
        """


    #Récupération de l'id du thread en cours
    def get_id(self):
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id


    #Permet l'arrêt du thread en cours
    @impmagic.loader(
        {'module': 'ctypes'},
        {'module': 'app.display', 'submodule': ['logs']},
    )
    def kill_thread(self):
        logs("Requête d'arrêt reçue", "info")
        self.killed = True
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            #print('Exception raise failure')
        self.connexion.close()
        #th_E.kill_thread()


@impmagic.loader(
    {'module': '__main__'},
    {'module': 'sys'},
    {'module': 'zpp_args'},
    {'module': 'app.display', 'submodule': ['logs']},
    {'module': 'core.config', 'submodule': ['config_znote']},
    {'module': 'core.client.settings', 'submodule': ['Settings']},
    {'module': 'core.client.connect', 'submodule': ['connect_server']},
)
def run_client():
    parse = zpp_args.parser()
    parse.set_description("znote")
    parse.set_argument(longname="config", description="Spécifier le chemin du fichier de config", store="value", default=None)
    parse.set_argument(longname="init", description="Initialiser les paramètres de l'application", default=None)
    parse.set_argument(longname="create", description="Création d'un workspace", default=False, category="workspace")
    parse.set_argument(longname="remove", description="Suppression d'un workspace", default=False, category="workspace")
    parse.set_argument(longname="info", description="Afficher les informations de connexion", default=False)
    parse.set_argument(longname="purge", description="Purger le channel durant le publication ou durant le fetch", default=False, category="channel")
    parse.set_argument(longname="force", description="Forcer le changement avec fetch", default=False, category="channel")
    parse.set_argument(longname="file", description="Récupérer le fichier spécifié avec fetch", default=False, category="channel", store="value")
    parse.set_argument(longname="detail", description="Afficher les informations du channel", default=False, category="channel")
    parse.set_argument(longname="tree", description="Afficher l'arborescence du channel", default=False, category="channel")
    parse.set_argument(longname="exclude", description="Exclure les chemins spécifiés du publish", default=False, category="channel", store="value")
    #parse.set_parameter("command", description="commande à lancer")
    parse.set_parameter("config", "Affichage/Modification de la configuration")
    parse.set_parameter("login", "Connexion à un serveur de note")
    parse.set_parameter("logout", "Déconnexion d'un serveur de note")
    parse.set_parameter("status", "Affichage du statut de l'application")
    parse.set_parameter("workspace", "Création/Suppression/Changement de workspace")
    parse.set_parameter("add", "Ajouter une note")
    parse.set_parameter("edit", "Editer une note")
    parse.set_parameter("view", "Voir une note")
    parse.set_parameter("pull", "Récupérer une note")
    parse.set_parameter("push", "Envoyer une note")
    parse.set_parameter("remove", "Supprimer une note")
    parse.set_parameter("list", "Lister les notes")
    parse.set_parameter("info", "Afficher les informations d'une note")
    parse.set_parameter("find", "Rechercher un contenu dans les notes")
    parse.set_parameter("protect", "Protéger une note par mot de passe")
    parse.set_parameter("publish", "Publier du contenu sur un channel")
    parse.set_parameter("unpublish", "Supprimer un channel")
    parse.set_parameter("fetch", "Récupérer le contenu sur un channel")
    parse.set_parameter("channel", "Afficher les informations sur les channels")
    parse.disable_check()
    parameter, argument = parse.load()

    if argument!=None:
        __main__.settings = Settings(argument.config)

        if argument.init:
            __main__.settings.init_settings()

        elif argument.info:
            logs(f"{__main__.settings.host}:{__main__.settings.port}", force=True)

        else:
            if len(sys.argv)>1:
                match sys.argv[1]:
                    case "config":
                        config_znote()
                        return

            __main__.settings.load_key()
            connexion = connect_server()
            
            if connexion==0:
                logs("Impossible d'accéder au serveur", "error", force=True)
            else:
                __main__.th_R = Client(connexion)
                __main__.th_R.run(argument, parameter)


if __name__ == "__main__":
    run_client()
