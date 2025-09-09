import impmagic

class Settings:
    @impmagic.loader(
        {'module': '__main__'},
        {'module': 're'},
        {'module': 'os'},
        {'module': 'pyotp'},
        {'module': 'app.display', 'submodule': ['logs']},
        {'module': 'core.config', 'submodule': ['Config']},
    )
    def __init__(self, config_file=None):
        if not config_file:
            config_dir = os.path.abspath(os.path.expanduser('~/.config/znote'))
            config_file = os.path.join(config_dir, "config.yml")

        if not os.path.exists(os.path.dirname(config_file)):
            os.makedirs(os.path.dirname(config_file), exist_ok=True)

        self.config = Config(config_file)

        self.verbose = self.config.get('server.verbose', default=True, auto_set=True)
        
        self.host = self.config.get('server.host', default="127.0.0.1", auto_set=True)
        self.port = self.config.get('server.port', default=40017, auto_set=True)
        self.key_size = self.config.get('server.key_size', default=2048, auto_set=True)
        self.key_otp = self.config.get('server.key_otp', default='JBSWY3DPEHPK3PXP', auto_set=True)
        self.config_dir = self.config.get('server.working_dir', default=os.path.abspath(os.path.expanduser('~/.config/znote')), auto_set=True)

        #Initialisation de l'OTP pour la connexion initiale
        if not re.match(r'^[A-Z0-9]{16}$', self.key_otp):
            print("Clé OTP invalide. Passage sur la clé par défaut", "warning")
            self.key_otp = 'JBSWY3DPEHPK3PXP'
        self.totp = pyotp.TOTP(self.key_otp)

        self.data_dir = self.config.get('server.data_dir', default=None, auto_set=False)

        if self.data_dir:
            self.data_dir = os.path.join(self.config_dir, self.data_dir)
        else:
            self.data_dir = os.path.join(self.config_dir, "znote.db")


    @impmagic.loader(
        {'module': '__main__'},
        {'module': 'os'},
        {'module': 'hashlib'},
        {'module': 'Crypto.PublicKey', 'submodule': ['RSA']},
        {'module': 'Crypto', 'submodule': ['Random']},
        {'module': 'app.display', 'submodule': ['logs']},
    )
    def load_key(self):
        privkey_path = os.path.join(self.config_dir, "server.key")
        pubkey_path = os.path.join(self.config_dir, "server.pem")

        if not os.path.exists(privkey_path) or not os.path.exists(pubkey_path):
            try:
                #Génération de la paire de clé pour les échanges avec le client
                logs("Création de la paire de clé", "info")
                rng = Random.new().read
                rsa_key = RSA.generate(self.key_size, rng)
                rsa_priv = rsa_key.exportKey("PEM")

                self.PrivKey = rsa_key.exportKey('PEM', pkcs=1)

                with open(privkey_path, "wb") as f:
                    f.write(self.PrivKey)

                key_pub = rsa_key.publickey()
                self.PubKey = key_pub.exportKey("PEM")
                
                with open(pubkey_path, "wb") as f:
                    f.write(self.PubKey)
                
                logs("Paire de clé créée", "success")

            except Exception as err:
                logs(f"Erreur lors de la création de la paire de clé: {err}", "error")
                exit()

        else:
            try:
                logs("Chargement de la paire de clé", "info")
                
                with open(privkey_path, "rb") as f:
                    self.PrivKey = f.read()
                
                with open(pubkey_path, "rb") as f:
                    self.PubKey = f.read()
                
                logs("Paire de clé chargée", "success")

            except Exception as err:
                logs(f"Erreur lors du chargement de la paire de clé: {err}", "error")
                exit()

        #Calcul du hash de la clé du client
        self.serverhash = hashlib.sha256(self.PubKey).hexdigest()


    @impmagic.loader(
        {'module': '__main__'},
        {'module': 'os'},
        {'module': 'model', 'submodule': ['models']},
        {'module': 'sqlalchemy', 'submodule': ['create_engine']},
        {'module': 'sqlalchemy.orm', 'submodule': ['sessionmaker']},
        {'module': 'app.display', 'submodule': ['logs']},
    )
    def load_db(self):
        try:
            engine = create_engine(f'sqlite:///{self.data_dir}')
            models.Base.metadata.create_all(engine)
            Session = sessionmaker(bind=engine)
            __main__.Session = Session

            logs("Base de données initialisée", "success")

        except Exception as err:
            logs(f"Erreur lors de l'initialisation de la base de données: {err}", "error")
            exit()


    @impmagic.loader(
        {'module': 'zpp_color', 'submodule': ['fg', 'attr']},
    )
    def init_settings(self):
        host = input(f"{fg('dark_gray')}host [{fg('cyan')}{self.host}{fg('dark_gray')}]: ")
        port = input(f"{fg('dark_gray')}port [{fg('cyan')}{self.port}{fg('dark_gray')}]: ")
        key_size = input(f"{fg('dark_gray')}key_size [{fg('cyan')}{self.key_size}{fg('dark_gray')}]: ")
        key_otp = input(f"{fg('dark_gray')}key_otp [{fg('cyan')}{self.key_otp}{fg('dark_gray')}]: ")
        data_dir = input(f"{fg('dark_gray')}data_dir [{fg('cyan')}{self.data_dir}{fg('dark_gray')}]: ")
        working_dir = input(f"{fg('dark_gray')}working_dir [{fg('cyan')}{self.working_dir}{fg('dark_gray')}]: ")
        verbose = input(f"{fg('dark_gray')}verbose [{fg('cyan')}{self.verbose}{fg('dark_gray')}]: ")

        if host:
            self.config.set('server.host', host)

        if port and isinstance(port, int):
            self.config.set('server.port', int(port))

        if key_size and isinstance(key_size, int): 
            self.config.set('server.key_size', int(key_size))
        
        if key_otp:
            self.config.set('server.key_otp', key_otp)
        
        if data_dir:
            self.config.set('server.data_dir', data_dir)
        
        if working_dir:
            self.config.set('server.working_dir', working_dir)
        
        if verbose:
            self.config.set('server.verbose', verbose)
