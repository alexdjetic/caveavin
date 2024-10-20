from pymongo import MongoClient
from pymongo.errors import PyMongoError

class Connexdb:
    """
    Classe pour gérer les connexions et opérations avec MongoDB.

    Attributs
    ---------
    host : str
        Le nom d'hôte du serveur MongoDB.
    port : int
        Le numéro de port du serveur MongoDB.
    username : str
        Le nom d'utilisateur pour se connecter à MongoDB.
    password : str
        Le mot de passe pour se connecter à MongoDB.
    client : MongoClient
        L'instance du client MongoDB.
    db : Database
        L'instance de la base de données MongoDB.

    Méthodes
    --------
    get_all_collection_name() -> dict
        Récupère tous les noms de collections de la base de données.
    get_all_data_from_collection(collection: str) -> dict
        Récupère toutes les données d'une collection spécifiée.
    delete_data_from_collection(collection: str, query: dict) -> dict
        Supprime des données d'une collection spécifiée en fonction d'une requête.
    update_data_from_collection(collection: str, query: dict, new_data: dict) -> dict
        Met à jour des données dans une collection spécifiée en fonction d'une requête.
    insert_data_into_collection(collection: str, data: dict) -> dict
        Insère des données dans une collection spécifiée.
    exist(collection: str, query: dict) -> dict
        Vérifie si un document existe dans une collection spécifiée en fonction d'une requête.
    close() -> dict
        Ferme la connexion à MongoDB.
    """

    def __init__(self, host='localhost', port=27018, username=None, password=None):
        """
        Initialise la classe Connexdb avec les détails du serveur MongoDB fournis.

        Paramètres
        ----------
        host : str, optionnel
            Le nom d'hôte du serveur MongoDB (par défaut 'localhost').
        port : int, optionnel
            Le numéro de port du serveur MongoDB (par défaut 27018).
        username : str, optionnel
            Le nom d'utilisateur pour se connecter à MongoDB (par défaut None).
        password : str, optionnel
            Le mot de passe pour se connecter à MongoDB (par défaut None).
        """
        if username and password:
            self.client = MongoClient(f"mongodb://{username}:{password}@{host}:{port}/")
        else:
            self.client = MongoClient(host=host, port=port)

        self.db = self.client.caveavin  # Connexion à la base de données 'caveavin'

    def get_all_collection_name(self) -> dict:
        """
        Récupère tous les noms de collections de la base de données.

        Retourne
        --------
        dict
            Un dictionnaire contenant le statut, un message et les noms des collections.
        """
        try:
            collections = self.db.list_collection_names()
            return {"status": 200, "message": "Collections récupérées avec succès", "data": collections}
        except PyMongoError as e:
            return {"status": 500, "message": f"Erreur lors de la récupération des collections : {e}"}

    def get_all_data_from_collection(self, collection: str) -> dict:
        """
        Récupère toutes les données d'une collection spécifiée.

        Paramètres
        ----------
        collection : str
            Le nom de la collection à partir de laquelle récupérer les données.

        Retourne
        --------
        dict
            Un dictionnaire contenant le statut, un message et les documents de la collection.
        """
        try:
            data = list(self.db[collection].find())
            return {"status": 200, "message": "Données récupérées avec succès", "data": data}
        except PyMongoError as e:
            return {"status": 500, "message": f"Erreur lors de la récupération des données de la collection '{collection}' : {e}", "data": []}

    def get_data_from_collection(self, collection: str, query: dict) -> dict:
        """
        Récupère des données d'une collection spécifiée en fonction d'une requête.

        Paramètres
        ----------
        collection : str
            Le nom de la collection à partir de laquelle récupérer les données.
        query : dict
            La requête pour filtrer les documents.

        Retourne
        --------
        dict
            Un dictionnaire contenant le statut, un message et les documents correspondants.
        """
        try:
            data = list(self.db[collection].find(query))
            return {"status": 200, "message": "Données récupérées avec succès", "data": data}
        except PyMongoError as e:
            return {"status": 500, "message": f"Erreur lors de la récupération des données de la collection '{collection}' : {e}", "data": []}

    def delete_data_from_collection(self, collection: str, query: dict) -> dict:
        """
        Supprime des données d'une collection spécifiée en fonction d'une requête.

        Paramètres
        ----------
        collection : str
            Le nom de la collection à partir de laquelle supprimer des données.
        query : dict
            La requête pour sélectionner le document à supprimer.

        Retourne
        --------
        dict
            Un dictionnaire contenant le statut et un message.
        """
        try:
            self.db[collection].delete_one(query)
            return {"status": 200, "message": "Données supprimées avec succès"}
        except PyMongoError as e:
            return {"status": 500, "message": f"Erreur lors de la suppression des données de la collection '{collection}' : {e}"}
        except TypeError as e:
            return {"status": 501, "message": f"Erreur de type : {e}"}

    def update_data_from_collection(self, collection_name: str, query: dict, data: dict) -> dict:
        """
        Met à jour des données dans une collection spécifiée en fonction d'une requête.

        Paramètres
        ----------
        collection_name : str
            Le nom de la collection à mettre à jour.
        query : dict
            La requête pour sélectionner le document à mettre à jour.
        data : dict
            Les nouvelles données à appliquer.

        Retourne
        --------
        dict
            Un dictionnaire contenant le statut et un message.
        """
        try:
            collection = self.db[collection_name]
            result = collection.update_one(query, {"$set": data})

            if result.modified_count == 0:
                return {"status": 404, "message": "Aucun document trouvé à mettre à jour"}

            return {"status": 200, "message": "Document mis à jour avec succès"}
        except PyMongoError as e:
            return {"status": 500, "message": f"Erreur lors de la mise à jour du document : {e}"}

    def insert_data_into_collection(self, collection: str, data: dict) -> dict:
        """
        Insère des données dans une collection spécifiée.

        Paramètres
        ----------
        collection : str
            Le nom de la collection dans laquelle insérer les données.
        data : dict
            Les données à insérer sous forme de document.

        Retourne
        --------
        dict
            Un dictionnaire contenant le statut et un message.
        """
        try:
            self.db[collection].insert_one(data)
            return {"status": 200, "message": "Données insérées avec succès"}
        except PyMongoError as e:
            return {"status": 500, "message": f"Erreur lors de l'insertion des données dans la collection '{collection}' : {e}"}
        except TypeError as e:
            return {"status": 501, "message": f"Erreur de type : {e}"}

    def exist(self, collection: str, query: dict) -> dict:
        """
        Vérifie si un document existe dans une collection spécifiée en fonction d'une requête.

        Paramètres
        ----------
        collection : str
            Le nom de la collection où vérifier l'existence du document.
        query : dict
            La requête pour identifier le document.

        Retourne
        --------
        dict
            Un dictionnaire contenant le statut et un message indiquant si le document existe ou non.
        """
        try:
            exists = self.db[collection].find_one(query) is not None
            return {"status": 200, "message": "Le document existe" if exists else "Le document n'existe pas"}
        except PyMongoError as e:
            return {"status": 500, "message": f"Erreur lors de la vérification de l'existence dans la collection '{collection}' : {e}"}
        except TypeError as e:
            return {"status": 501, "message": f"Erreur de type : {e}"}

    def close(self) -> dict:
        """
        Ferme la connexion MongoDB.

        Retourne
        --------
        dict
            Un dictionnaire contenant le statut et un message.
        """
        if self.client:
            self.client.close()
            return {"status": 200, "message": "Connexion fermée avec succès"}
        return {"status": 500, "message": "Erreur lors de la fermeture de la connexion"}
