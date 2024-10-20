from pydantic import BaseModel, Field
from Classes.connexiondb import Connexdb
from route.dependencies import effectuer_operation_db

class Bouteille(BaseModel):
    """
    Représente une bouteille de vin avec diverses informations telles que son nom, type, année, etc.

    Attributs
    ---------
    id : int
        Identifiant unique de la bouteille.
    nom : str
        Nom de la bouteille.
    type : str
        Type de vin (rouge, blanc, etc.).
    annee : int
        Année de production de la bouteille.
    region : str
        Région où le vin a été produit.
    commentaires : list[str]
        Liste des commentaires associés à la bouteille.
    notes : float
        Note actuelle de la bouteille.
    moyen : float
        Moyenne des notes attribuées à la bouteille.
    photo : bytes
        Photo de la bouteille au format binaire.
    prix : float
        Prix de la bouteille.
    num_etagere : int
        Numéro d'étagère où la bouteille est stockée.
    config_db : dict
        Configuration de la base de données pour la connexion MongoDB.
    collections : str
        Nom de la collection MongoDB où les données sont stockées.
    numbers : int
        Nombre de bouteilles du même type.

    Méthodes
    --------
    consulter() -> dict
        Retourne un dictionnaire avec les détails de la bouteille.
    archiver() -> dict
        Archive la bouteille dans la base de données et la supprime de la collection actuelle.
    moyenne() -> dict
        Calcule et retourne la moyenne des notes de la bouteille.
    """

    id: int = Field(default=-1)
    nom: str = Field(default="bouteille")
    type: str = Field(default="inconnue")
    annee: int = Field(default=-1)
    region: str = Field(default="Russie")
    commentaires: list[str] = Field(default=[])
    notes: float = Field(default=-1.0)
    moyen: float = Field(default=-1.0)
    photo: bytes = Field(default=b"")
    prix: float = Field(default=-1.0)
    num_etagere: int = Field(default=-1)
    config_db: dict = Field(default={})
    collections: str = Field(default="bouteille")
    numbers: int = Field(default=1)

    def consulter(self) -> dict:
        """
        Retourne un dictionnaire contenant les détails de la bouteille.

        Returns
        -------
        dict
            Un dictionnaire avec les informations de la bouteille.
        """
        return {
            "nom": self.nom,
            "type": self.type,
            "annee": self.annee,
            "region": self.region,
            "commentaires": self.commentaires,
            "notes": self.notes,
            "moyen": self.moyen,
            "photo": self.photo,
            "prix": self.prix,
            "num_etagere": self.num_etagere
        }

    def archiver(self) -> dict:
        """
        Archive la bouteille dans une collection MongoDB dédiée, puis la supprime.

        Returns
        -------
        dict
            Un dictionnaire contenant le résultat de l'opération d'archivage.
        """
        if not self.config_db:
            return {
                "message": "Donnez la configuration pour la base de données MongoDB",
                "status": 500,
            }

        # Récupération des informations complètes de la bouteille
        all_info_result = self.get_all_information()

        if all_info_result.get("status") != 200:
            return all_info_result  # Si la récupération échoue, retourne l'erreur

        archive_data = all_info_result['data']

        # Connexion à la base de données
        connex: Connexdb = Connexdb(**self.config_db)

        # Insertion dans la collection archive
        archive_status = connex.insert_data_into_collection("archive", archive_data)

        if archive_status.get("status") != 200:
            return {
                "message": "L'archivage de la bouteille a échoué !",
                "status": archive_status.get("status"),
            }

        # Si l'archivage réussit, on tente la suppression de la bouteille
        delete_status = self.delete()

        if delete_status.get("status") != 200:
            return {
                "message": "L'archivage a réussi, mais la suppression a échoué !",
                "status": delete_status.get("status"),
            }

        return {
            "message": "Bouteille archivée et supprimée avec succès.",
            "status": 200,
        }

    def get_all_information(self) -> dict:
        """
        Récupère toutes les informations de la bouteille depuis la base de données, y compris les commentaires et les notes.

        Returns
        -------
        dict
            Un dictionnaire contenant toutes les informations de la bouteille.
        """
        print(f"Fetching information for bottle: {self.nom}")

        # Recherche les détails de la bouteille dans la base de données
        bottle_query: dict = {"nom": self.nom}
        bottle_info_result: dict = effectuer_operation_db(self.config_db, "bouteille", "get", query=bottle_query)

        if bottle_info_result.get("status") != 200 or not bottle_info_result.get("data"):
            return {
                "status": 404,
                "message": "Bouteille non trouvée.",
                "data": []
            }

        bottle_info = bottle_info_result["data"][0]

        # Récupération des commentaires
        comments_result = effectuer_operation_db(self.config_db, "commentaire", "get", {})
        tmp_commentaires = [comment for comment in comments_result.get("data", []) if comment.get("nom_bouteille") == self.nom]

        bottle_info["commentaires"] = tmp_commentaires

        # Récupération des notes
        ratings_result = effectuer_operation_db(self.config_db, "note", "get", {})
        tmp_notes = [note for note in ratings_result.get("data", []) if note.get("nom_bouteille") == self.nom]

        bottle_info["notes"] = tmp_notes

        # Calcul de la moyenne des notes
        average_result = self.moyenne()
        bottle_info["moyen"] = average_result["average"] if average_result.get("status") == 200 else None

        return {
            "message": "Bouteille récupérée avec succès !",
            "status": 200,
            "data": bottle_info
        }

    def moyenne(self) -> dict:
        """
        Calcule la moyenne des notes attribuées à la bouteille.

        Returns
        -------
        dict
            Un dictionnaire contenant la moyenne des notes et l'état de l'opération.
        """
        if not self.config_db:
            return {
                "message": "Donnez la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)

        # Recherche des notes associées à la bouteille
        query: dict = {"nom_bouteille": self.nom}
        notes_result: dict = connex.get_data_from_collection("note", query)

        if notes_result.get("status") != 200:
            return {
                "message": "Échec de la récupération des notes.",
                "status": notes_result.get("status"),
            }

        notes = [note['note'] for note in notes_result['data'] if 'note' in note]

        if not notes:
            return {
                "message": "Aucune note trouvée pour cette bouteille.",
                "status": 404,
            }

        average_value = sum(notes) / len(notes)

        return {
            "message": "Moyenne calculée avec succès.",
            "average": average_value,
            "status": 200,
        }

    def create(self) -> dict:
        """
        Crée une nouvelle bouteille dans la base de données, ou incrémente le champ 'numbers' si elle existe déjà.

        Returns
        -------
        dict
            Un dictionnaire contenant le résultat de l'opération.
        """
        if not self.config_db:
            return {
                "message": "Donnez la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)

        # Vérification si la bouteille existe déjà
        existing_bottle_result = self.exist()

        if existing_bottle_result.get("status") != 200:
            return existing_bottle_result

        if existing_bottle_result['data']:
            return self.increment_bouteille(existing_bottle_result['data'][0])

        return self.create_bouteille()

    def create_bouteille(self) -> dict:
        """
        Crée une nouvelle bouteille dans la collection MongoDB.

        Returns
        -------
        dict
            Un dictionnaire contenant le résultat de l'opération de création.
        """
        bottle_data = {
            "nom": self.nom,
            "type": self.type,
            "annee": self.annee,
            "region": self.region,
            "commentaires": self.commentaires,
            "notes": self.notes,
            "moyen": self.moyen,
            "photo": self.photo,
            "prix": self.prix,
            "num_etagere": self.num_etagere,
            "numbers": self.numbers
        }

        connex: Connexdb = Connexdb(**self.config_db)

        # Insertion dans la collection 'bouteille'
        insert_result: dict = connex.insert_data_into_collection("bouteille", bottle_data)

        if insert_result.get("status") != 200:
            return {
                "message": "Échec de la création de la bouteille.",
                "status": insert_result.get("status"),
            }

        return {
            "message": "Bouteille créée avec succès.",
            "status": 200,
        }

    def increment_bouteille(self, existing_bottle: dict) -> dict:
        """
        Incrémente le nombre de bouteilles existantes dans la base de données.

        Parameters
        ----------
        existing_bottle : dict
            Un dictionnaire représentant la bouteille existante.

        Returns
        -------
        dict
            Un dictionnaire contenant le résultat de l'opération d'incrémentation.
        """
        connex: Connexdb = Connexdb(**self.config_db)

        existing_bottle['numbers'] += self.numbers

        # Mise à jour de la bouteille avec le nouveau nombre
        update_result: dict = connex.update_data_from_collection("bouteille", existing_bottle)

        if update_result.get("status") != 200:
            return {
                "message": "Échec de l'incrémentation du nombre de bouteilles.",
                "status": update_result.get("status"),
            }

        return {
            "message": "Nombre de bouteilles incrémenté avec succès.",
            "status": 200,
        }

    def delete(self) -> dict:
        """
        Supprime la bouteille de la collection MongoDB.

        Returns
        -------
        dict
            Un dictionnaire contenant le résultat de l'opération de suppression.
        """
        connex: Connexdb = Connexdb(**self.config_db)

        delete_result: dict = connex.delete_data_from_collection("bouteille", {"nom": self.nom})

        if delete_result.get("status") != 200:
            return {
                "message": "Échec de la suppression de la bouteille.",
                "status": delete_result.get("status"),
            }

        return {
            "message": "Bouteille supprimée avec succès.",
            "status": 200,
        }

    def exist(self) -> dict:
        """
        Vérifie si une bouteille existe déjà dans la base de données.

        Returns
        -------
        dict
            Un dictionnaire contenant le résultat de la vérification.
        """
        connex: Connexdb = Connexdb(**self.config_db)

        query: dict = {"nom": self.nom, "annee": self.annee}
        result: dict = connex.get_data_from_collection(self.collections, query)

        return {
            "message": "Bouteille déjà existante." if result["data"] else "Bouteille inexistante.",
            "status": 200,
            "data": result["data"],
        }
