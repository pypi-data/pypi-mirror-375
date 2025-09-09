# znote : Client de prise de notes sécurisé

znote est une application de prise de notes en ligne de commande fonctionnant sur un modèle client-serveur. L'accent est mis sur la sécurité, avec un chiffrement de bout-en-bout des communications et des données, garantissant que seul l'utilisateur peut accéder au contenu de ses notes.


## Fonctionnalités

- **Sécurité Renforcée** : Chiffrement de bout-en-bout (E2EE) avec une architecture hybride RSA-4096/AES-256.
- **Signatures Numériques** : Chaque message est signé pour garantir son intégrité et son authenticité.
- **Gestion Complète des Notes** : Créez, éditez, consultez, listez et supprimez des notes.
- **Éditeur Intégré** : Un éditeur de texte simple est intégré directement dans le terminal pour une expérience fluide.
- **Workspaces (Espaces de travail)** : Organisez vos notes dans des espaces de travail distincts.
- **Synchronisation de Fichiers** : Envoyez (`push`) un fichier local pour créer une note, ou téléchargez (`pull`) une note dans un fichier.
- **Channels de Diffusion** : Partagez et synchronisez des fichiers sur plusieurs postes via des "channels".
- **Protection par Mot de Passe** : Protégez l'accès à des notes spécifiques avec un mot de passe.
- **Recherche** : Retrouvez du contenu rapidement grâce à une fonction de recherche dans toutes vos notes.
- **Stockage en base** : Pour l'instant les notes sont stockées en clair dans la base. A voir pour rajouter le support du chiffrement côté serveur.

## Installation

Assurez-vous d'avoir Python et `pip` installés. Le projet est disponible sur Pypi.

```bash
pip install zpp_note
```

## Côté serveur

Le serveur est le cœur de l'application. Il gère les comptes utilisateurs, stocke les données chiffrées et répond aux requêtes des clients.

### Premier Lancement

1.  **Initialiser le serveur** : Cette commande vous guidera pour créer le fichier de configuration `config.toml`.
    ```bash
    znote_server --init
    ```

2.  **Créer un utilisateur** :
    ```bash
    znote_server --create_user --username mon_user --password "mon_mot_de_passe"
    ```

3.  **Lancer le serveur** :
    ```bash
    znote_server
    ```

### Utilisation du Serveur

**Lancement du serveur :**
Pour démarrer le serveur en mode normal, exécutez simplement :
```bash
znote_server
```
Le serveur tournera en arrière-plan, en attente de connexions.

### Options de Lancement du Serveur

| Option              | Description                                                                                             | Exemple d'utilisation                                                 |
| ------------------- | ------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `--init`            | Lance un assistant interactif pour configurer le fichier `config.toml` du serveur.                      | `znote_server --init`                                                      |
| `--config <chemin>` | Spécifie un chemin personnalisé pour le fichier de configuration.                                       | `znote_server --config /etc/znote/server.toml`                         |
| `--create_user`     | Un drapeau pour activer la création d'un nouvel utilisateur. Doit être utilisé avec `username` et `password`. | `znote_server --create_user --username admin --password "secret"`      |
| `--username <nom>`  | Spécifie le nom d'utilisateur pour la création.                                                         | `... --username admin`                                                 |
| `--password <mdp>`  | Spécifie le mot de passe pour la création.                                                              | `... --password "un_mot_de_passe_solide"`                              |
| `config <config_key> <config_value>`               | Afficher ou modifier la configuration.                                                                            | `znote_server config client.host 127.0.0.1`                                         |

### Détail du fichier de config

```ini
server:
  verbose: true               #Afficher les logs
  host: 127.0.0.1             #Ip d'écoute
  port: 40017                 #Port d'écoute
  key_size: 2048              #Taille de la clé RSA
  key_otp: JFSWY3DPEHPK3PXP   #Clé OTP pour le démarrage
  data_dir:                   #Chemin vers la base SQLite
  working_dir:                #Emplacement des fichiers de l'application
```

## Côté client

Le client est l'interface en ligne de commande pour interagir avec vos notes.

### Premier Lancement

1.  **Initialiser le client** (dans un autre terminal) :
    ```bash
    znote --init
    ```
    Assurez-vous que les informations du serveur (host, port) correspondent.

2.  **Connectez-vous** :
    ```bash
    znote login
    ```

### Options Générales du Client

| Option              | Description                                                                    | Exemple d'utilisation                         |
| ------------------- | ------------------------------------------------------------------------------ | -------------------------------------------- |
| `--init`            | Lance un assistant interactif pour configurer le `config.toml` du client.      | `znote --init`                               |
| `--config <chemin>` | Spécifie un chemin personnalisé pour le fichier de configuration.              | `znote --config ~/.znote_perso.toml`         |
| `--info`            | Affiche les informations de connexion de base (host, port) sans se connecter.  | `znote --info`                               |

### Commandes du Client

La syntaxe générale est `znote <commande> [arguments...]`.

| Commande                       | Description                                                                                                                            | Exemple d'utilisation                                                  |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `login`                        | Ouvre une session sécurisée avec le serveur. Demande le nom d'utilisateur et le mot de passe.                                          | `znote login`                                                          |
| `logout`                       | Met fin à la session actuelle et invalide le token.                                                                                    | `znote logout`                                                         |
| `status`                       | Affiche l'état de la connexion, le workspace actif et le nombre de notes.                                                              | `znote status`                                                         |
| `list`                         | Liste toutes les notes dans le workspace actuel.                                                                                       | `znote list`                                                           |
| `add <nom_note>`               | Crée une nouvelle note et ouvre l'éditeur de texte intégré.                                                                            | `znote add "Ma première note"`                                         |
| `edit <nom_note>`              | Ouvre une note existante dans l'éditeur de texte.                                                                                      | `znote edit "Ma première note"`                                        |
| `view <nom_note>`              | Affiche le contenu d'une note directement dans le terminal.                                                                            | `znote view "Courses à faire"`                                         |
| `remove <nom_note>`            | Supprime une note de manière permanente.                                                                                               | `znote remove "Vieille note"`                                          |
| `info <nom_note>`              | Affiche les métadonnées d'une note (date de création/modification, créateur, etc.).                                                    | `znote info "Ma première note"`                                        |
| `find "<pattern>"`             | Recherche un mot ou une phrase dans le contenu de toutes les notes du workspace.                                                       | `znote find "réunion importante"`                                      |
| `protect <nom_note>`           | Définit un mot de passe pour une note spécifique. L'accès à la note nécessitera ce mot de passe.                                        | `znote protect`                                              |
| `pull <nom_note> [fichier]`    | Télécharge le contenu d'une note et le sauvegarde dans un fichier local. Si le nom de fichier n'est pas donné, il est déduit du titre. | `znote pull "Rapport" rapport.txt`                                     |
| `push <fichier> [nom_note]`    | Envoie le contenu d'un fichier local pour créer une nouvelle note. Si le nom de la note n'est pas donné, il est déduit du nom de fichier. | `znote push rapport_final.md "Rapport Final"`                          |
| `workspace`                    | Affiche la liste des workspaces disponibles et indique celui qui est actif.                                                            | `znote workspace`                                                      |
| `workspace <nom_ws>`           | Change le workspace actif.                                                                                                             | `znote workspace "Projets"`                                            |
| `workspace <nom_ws> --create`  | Crée un nouveau workspace.                                                                                                             | `znote workspace "Archives" --create`                                  |
| `workspace <nom_ws> --remove`  | Supprime un workspace.                                                                                                                 | `znote workspace "Archives" --remove`                                  |
| `config <config_key> <config_value>`               | Afficher ou modifier la configuration.                                                                            | `znote config client.host 127.0.0.1`                                         |


### Commandes des Channels

La fonctionnalité de "channel" permet de synchroniser des fichiers entre plusieurs postes.

| Commande                       | Description                                                                                                                            | Exemple d’utilisation                                                  |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `channel`                      | Liste tous les channels disponibles sur le serveur.                                                                                    | `znote channel`                                                        |
| `channel <nom> --detail`       | Affiche les informations détaillées d'un channel (hash, date de modification...).                                                      | `znote channel mon-canal --detail`                                     |
| `channel <nom> --tree`         | Affiche l'arborescence et la liste des fichiers contenus dans le channel.                                                              | `znote channel mon-canal --tree`                                       |
| `publish <channel> <fichier>`  | Publie un fichier sur un channel. Si le fichier existe déjà, il est mis à jour.                                                        | `znote publish mon-canal ./rapport.pdf`                                |
| `publish <channel> <fichier>`  | Publie un fichier sur un channel. Si le fichier existe déjà, il est mis à jour.                                                        | `znote publish mon-canal ./rapport.pdf`                                |
| `publish <channel> --exclude <file_path`    | Spécifier les fichiers à exclure du publish.                                                | `znote publish mon-canal --exclude test.db`                                      |
| `unpublish <channel>`  | Supprime un channel.                                                         | `znote unpublish mon-canal`                                |
| `fetch <channel> (<path>)`              | Récupère (télécharge) tous les fichiers d'un channel dans le répertoire local.                                                         | `znote fetch mon-canal`                                                |
| `fetch <channel> --force`      | Force le téléchargement et l'écrasement des fichiers locaux même s'ils existent déjà.                                                    | `znote fetch mon-canal --force`                                        |
| `fetch <channel> --purge`      | Supprime les fichiers locaux qui ne sont pas présent dans le channel.                                                    | `znote fetch mon-canal --purge`                                        |
| `fetch <channel> --file <file_path>`      | Récupérer un fichier spécifique dans le channel.                                                    | `znote fetch mon-canal --file mon-fichier`                                        |
| `diff <channel>`               | Compare le répertoire local avec le contenu du channel et affiche les différences (fichiers nouveaux, modifiés ou à supprimer).          | `znote diff mon-canal`                                                 |


### Détail du fichier de config

```ini
client:
  verbose: true               #Afficher les logs
  host: 127.0.0.1             #Ip du serveur
  port: 40017                 #Port du serveur
  key_size: 2048              #Taille de la clé RSA
  key_otp: JFSWY3DPEHPK3PXP   #Clé OTP pour le démarrage
  working_dir:                #Emplacement des fichiers de l'application
  exclude_dir:                #Nom des répertoires à exclure
```