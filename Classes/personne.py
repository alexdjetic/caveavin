from pydantic import BaseModel, EmailStr, Field
from Classes.connexiondb import Connexdb
from typing import Optional, List, Dict, Any

class Personne(BaseModel):
    """
    Classe représentant une personne, avec des fonctionnalités d'authentification et de gestion des données utilisateur.

    Attributs
    ---------
    id : Optional[int]
        Identifiant unique de la personne.
    perm : Optional[str]
        Niveau de permission de la personne.
    login : Optional[str]
        Nom d'utilisateur de connexion.
    password : Optional[str]
        Mot de passe de la personne.
    nom : Optional[str]
        Nom de famille de la personne.
    prenom : Optional[str]
        Prénom de la personne.
    email : Optional[EmailStr]
        Adresse e-mail de la personne.
    photo : Optional[bytes]
        Photo de la personne (en format binaire).
    bouteille_reserver : Optional[List[int]]
        Liste des bouteilles réservées par la personne.
    config_db : Optional[Dict[str, Any]]
        Configuration de la base de données MongoDB.
    collections : Optional[str]
        Nom de la collection où sont stockées les données utilisateur.
    caves : Optional[List[str]]
        Liste des caves associées à la personne.

    Méthodes
    --------
    create() -> dict
        Crée un utilisateur dans la base de données.
    update(data: dict) -> dict
        Met à jour les informations d'un utilisateur dans la base de données.
    delete() -> dict
        Supprime un utilisateur de la base de données.
    get() -> dict
        Récupère un utilisateur depuis la base de données.
    auth() -> dict
        Authentifie un utilisateur avec le login et le mot de passe fournis.
    get_bottles() -> dict
        Récupère la liste des bouteilles réservées par l'utilisateur.
    get_caves() -> dict
        Récupère les caves associées à l'utilisateur.
    add_bottle(bottle_name: str) -> dict
        Ajoute une bouteille à la liste des bouteilles réservées par l'utilisateur.
    """

    id: Optional[int] = Field(default=None)
    perm: Optional[str] = Field(default=None)
    login: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)
    nom: Optional[str] = Field(default=None)
    prenom: Optional[str] = Field(default=None)
    email: Optional[EmailStr] = Field(default=None)
    photo: Optional[bytes] = Field(default=None)
    bouteille_reserver: Optional[List[int]] = Field(default_factory=list)
    config_db: Optional[Dict[str, Any]] = Field(default_factory=dict)
    collections: Optional[str] = Field(default="user")
    caves: Optional[List[str]] = Field(default_factory=list)

    def create(self) -> dict:
        """
        Crée un utilisateur dans la base de données.

        Cette méthode insère les informations de l'utilisateur dans la collection spécifiée.
        Si l'utilisateur existe déjà, elle renvoie un message d'erreur.

        Returns
        -------
        dict
            Un dictionnaire contenant un message de succès ou d'échec ainsi qu'un statut.
        """
        if not self.config_db:
            return {
                "message": "Veuillez fournir la configuration de la base de données MongoDB.",
                "status": 500,
            }

        # Connexion à la base de données
        connex = Connexdb(**self.config_db)

        # Données de l'utilisateur à insérer dans la base
        data_user = {
            "id": self.id,
            "perm": self.perm,
            "login": self.login,
            "password": self.password,
            "nom": self.nom,
            "prenom": self.prenom,
            "email": self.email,
            "bouteille_reserver": self.bouteille_reserver if self.bouteille_reserver else [],
        }

        # Vérifie si l'utilisateur existe déjà
        exist_status = connex.exist(self.collections, {"login": self.login})
        if exist_status.get("status") == 200 and exist_status.get("message") == "User exists":
            return {
                "message": "L'utilisateur existe déjà dans la base de données.",
                "status": 500
            }

        # Insertion de l'utilisateur dans la base
        rstatus = connex.insert_data_into_collection(self.collections, data_user)
        if rstatus.get("status") != 200:
            return {
                "message": rstatus.get("message"),
                "status": rstatus.get("status")
            }

        return rstatus

    def update(self, data: dict) -> dict:
        """
        Met à jour les informations de l'utilisateur dans la base de données.

        Si le champ 'caves' est fourni dans les données, les nouvelles caves sont ajoutées
        à la liste des caves existantes sans duplication.

        Parameters
        ----------
        data : dict
            Les nouvelles données à mettre à jour pour l'utilisateur.

        Returns
        -------
        dict
            Un dictionnaire contenant le statut et un message de succès ou d'échec.
        """
        if not self.config_db:
            return {
                "message": "Veuillez fournir la configuration de la base de données MongoDB.",
                "status": 500,
            }

        query = {"login": self.login}
        connex = Connexdb(**self.config_db)

        # Si les caves sont mises à jour, ajouter à la liste actuelle sans doublons
        if "caves" in data:
            update_data = {"$addToSet": {"caves": {"$each": data["caves"]}}}
        else:
            update_data = {"$set": data}

        rstatus = connex.update_data_from_collection(self.collections, query, update_data)
        if rstatus.get("status") != 200:
            return {
                "message": "Échec de la mise à jour de l'utilisateur.",
                "status": rstatus.get("status")
            }

        return rstatus

    def delete(self) -> dict:
        """
        Supprime l'utilisateur de la base de données.

        Cette méthode supprime l'utilisateur de la base de données en fonction du login.

        Returns
        -------
        dict
            Un dictionnaire contenant le statut et un message indiquant si l'opération a réussi.
        """
        if not self.config_db:
            return {
                "message": "Veuillez fournir la configuration de la base de données MongoDB.",
                "status": 500,
            }

        connex = Connexdb(**self.config_db)
        query = {"login": self.login}

        # Supprime l'utilisateur de la collection
        rstatus = connex.delete_data_from_collection(self.collections, query)
        if rstatus.get("status") != 200:
            return {
                "message": "Échec de la suppression de l'utilisateur.",
                "status": rstatus.get("status")
            }

        return rstatus

    def get(self) -> dict:
        """
        Récupère les informations de l'utilisateur à partir de la base de données.

        Returns
        -------
        dict
            Un dictionnaire contenant les informations de l'utilisateur, le statut et un message.
        """
        if not self.config_db:
            return {
                "message": "Veuillez fournir la configuration de la base de données MongoDB.",
                "status": 500,
            }

        query_search = {"login": self.login}
        connex = Connexdb(**self.config_db)
        rstatus = connex.get_data_from_collection(self.collections, query_search)

        if rstatus.get("status") != 200:
            return {
                "message": "Impossible de récupérer l'utilisateur.",
                "status": rstatus.get("status"),
                "data": []
            }

        return {
            "message": "Utilisateur trouvé.",
            "status": 200,
            "data": rstatus.get("data")
        }

    def auth(self) -> Dict[str, Any]:
        """
        Authentifie l'utilisateur avec le login et le mot de passe fournis.

        Returns
        -------
        dict
            Un dictionnaire contenant un message, le statut et les données de l'utilisateur si l'authentification est réussie.
        """
        if not self.config_db:
            return {
                "message": "Veuillez fournir la configuration de la base de données MongoDB.",
                "status": 500,
            }

        connex = Connexdb(**self.config_db)
        query_search = {"login": self.login, "password": self.password}

        # Recherche l'utilisateur dans la base
        rstatus = connex.get_data_from_collection(self.collections, query_search)

        if not rstatus.get("data"):
            return {
                "message": "Aucun utilisateur trouvé avec les informations fournies.",
                "status": 404
            }

        return {
            "message": "Authentification réussie.",
            "status": 200,
            "user_data": rstatus.get("data")[0]
        }

    def get_bottles(self) -> dict:
        """
        Récupère la liste des bouteilles réservées par l'utilisateur.

        Returns
        -------
        dict
            Un dictionnaire contenant le statut, le message et les informations sur les bouteilles réservées.
        """
        connex = Connexdb(**self.config_db)

        # Récupère les données utilisateur
        user_data_result = connex.get_data_from_collection(self.collections, {"login": self.login})

        if user_data_result.get("status") != 200 or not user_data_result.get("data"):
            return {
                "message": "Utilisateur introuvable.",
                "status": 404
            }

        user_data = user_data_result.get("data")[0]
        bottles = user_data.get("bouteille_reserver", [])

        return {
            "message": "Bouteilles récupérées avec succès.",
            "status": 200,
            "bottles": bottles
        }

    def get_caves(self) -> dict:
        """
        Récupère les caves associées à l'utilisateur.

        Returns
        -------
        dict
            Un dictionnaire contenant les caves associées à l'utilisateur.
        """
        connex = Connexdb(**self.config_db)
        user_data_result = connex.get_data_from_collection(self.collections, {"login": self.login})

        if user_data_result.get("status") != 200 or not user_data_result.get("data"):
            return {
                "message": "Utilisateur introuvable.",
                "status": 404
            }

        user_data = user_data_result.get("data")[0]
        caves = user_data.get("caves", [])

        return {
            "message": "Caves récupérées avec succès.",
            "status": 200,
            "caves": caves
        }

    def add_bottle(self, bottle_name: str) -> dict:
        """
        Ajoute une bouteille à la liste des bouteilles réservées de l'utilisateur.

        Parameters
        ----------
        bottle_name : str
            Le nom de la bouteille à ajouter.

        Returns
        -------
        dict
            Un dictionnaire contenant le message, le statut et la liste mise à jour des bouteilles réservées.
        """
        connex = Connexdb(**self.config_db)

        # Ajoute la bouteille à la liste en évitant les doublons
        update_result = connex.update_data_from_collection(
            self.collections,
            {"login": self.login},
            {"$addToSet": {"bouteille_reserver": bottle_name}}
        )

        if update_result.get("status") != 200:
            return {
                "message": "Erreur lors de l'ajout de la bouteille.",
                "status": update_result.get("status")
            }

        return self.get_bottles()
