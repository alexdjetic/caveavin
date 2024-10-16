from pydantic import BaseModel, Field
from Classes.connexiondb import Connexdb
from route.dependencies import effectuer_operation_db

class Bouteille(BaseModel):
    """
    A class to represent a bottle of wine.

    Attributes
    ----------
    id : int
        The unique identifier for the bottle.
    nom : str
        The name of the bottle.
    type : str
        The type of wine.
    annee : int
        The year of production.
    region : str
        The region where the wine was produced.
    commentaires : list of str
        Comments about the wine.
    notes : float
        The rating of the wine.
    moyen : float
        The average rating of the wine.
    photo : bytes
        The photo of the bottle in binary format.
    prix : float
        The price of the bottle.
    num_etagere : int
        The shelf number where the bottle is stored.
    config_db : dict
        The database configuration.
    collections : str
        The name of the collection in the database.
    numbers : int
        The number of bottles.

    Methods
    -------
    consulter() -> dict
        Returns a dictionary with the bottle's details.
    supprimer() -> dict
        Raises NotImplementedError.
    archiver() -> dict
        Archives the bottle in the database.
    moyenne() -> dict
        Calculates the average rating of the wine.
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
        Returns a dictionary with the bottle's details.

        Returns
        -------
        dict
            A dictionary containing the bottle's attributes.
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
        Archives the bottle in the database.

        Returns
        -------
        dict
            A dictionary indicating the result of the archiving operation.
        """
        if not self.config_db:
            return {
                "message": "Donnez la configuration pour la base de données MongoDB",
                "status": 500,
            }

        # Get all information about the bottle
        all_info_result = self.get_all_information()

        if all_info_result.get("status") != 200:
            return all_info_result  # Return the error response if fetching information failed

        # Prepare the data to archive
        archive_data = all_info_result['data']

        # Create a new connection to the database
        connex: Connexdb = Connexdb(**self.config_db)

        # Insert the data into the archive collection
        archive_status = connex.insert_data_into_collection("archive", archive_data)

        if archive_status.get("status") != 200:
            return {
                "message": "L'archivage de la bouteille a échoué !",
                "status": archive_status.get("status"),
            }

        # If archiving was successful, delete the bottle from the collection
        delete_status = self.delete()  # Assuming this method exists and is correctly implemented

        if delete_status.get("status") != 200:
            return {
                "message": "L'archivage a réussi, mais la suppression a échoué !",
                "status": delete_status.get("status"),
            }

        return {
            "message": "Bouteille archivée et supprimée avec succès.",
            "status": 200,
        }

    def get_commentaires(self) -> dict:
        """
        Fetches comments about the wine from the database.

        Returns
        -------
        dict
            A dictionary containing the fetched comments.
        """
        if not self.config_db:
            return {
                "message": "Donnez la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)

        # Query to get comments by name
        query = {"nom": self.nom}
        commentaires_result = connex.get_data_from_collection("commentaire", query)

        if commentaires_result.get("status") != 200:
            return {
                "message": "Échec de la récupération des commentaires.",
                "status": commentaires_result.get("status"),
            }

        return {
            "status": 200,
            "data": commentaires_result.get("data", [])
        }

    def get_notes(self) -> dict:
        """
        Fetches ratings for the wine from the database.

        Returns
        -------
        dict
            A dictionary containing the fetched ratings.
        """
        if not self.config_db:
            return {
                "message": "Donnez la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)

        # Query to get ratings by name
        query = {"nom": self.nom}
        commentaires_result = connex.get_data_from_collection("note", query)

        if commentaires_result.get("status") != 200:
            return {
                "message": "Échec de la récupération des notes.",
                "status": commentaires_result.get("status"),
            }

        return {
            "status": 200,
            "data": commentaires_result.get("data", [])
        }

    def get_all_information(self) -> dict:
        """
        Retrieves all information about the bottle, including its details, comments, and ratings.
        """
        print(f"Fetching information for bottle: {self.nom}")  # Debug print

        # Fetch the bottle information from the database
        bottle_query = {"nom": self.nom}
        bottle_info_result = effectuer_operation_db(self.config_db, "bouteille", "get", query=bottle_query)

        print(f"Bottle info result: {bottle_info_result}")  # Debug print

        if bottle_info_result.get("status") != 200 or not bottle_info_result.get("data"):
            return {
                "status": 404,
                "message": "Bouteille non trouvée.",
                "data": []
            }

        # Get the bottle information
        bottle_info = bottle_info_result["data"][0]

        # Fetch comments associated with the bottle
        comments_result = effectuer_operation_db(self.config_db, "commentaire", "get", {"nom_bouteille": self.nom})
        bottle_info["commentaires"] = comments_result.get("data", [])

        # Fetch ratings associated with the bottle
        ratings_result = effectuer_operation_db(self.config_db, "note", "get", {"nom_bouteille": self.nom})
        bottle_info["notes"] = ratings_result.get("data", [])

        print(f"Final bottle information: {bottle_info}")  # Debug print

        return {
            "message": "Bouteille récupérée avec succès !",
            "status": 200,
            "data": bottle_info
        }

    def moyenne(self) -> dict:
        """
        Calculates the average rating of the wine.

        Returns
        -------
        dict
            A dictionary containing the average rating and the operation status.
        """
        if not self.config_db:
            return {
                "message": "Donnez la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)

        # Query to filter ratings by name
        query = {"nom_bouteille": self.nom}  # Ensure the query matches the field in the database
        notes_result = connex.get_data_from_collection("note", query)

        if notes_result.get("status") != 200:
            return {
                "message": "Échec de la récupération des notes.",
                "status": notes_result.get("status"),
            }

        # Extract the values from the retrieved ratings
        notes = [note['value'] for note in notes_result['data'] if 'value' in note]  # Ensure 'value' exists

        if not notes:
            return {
                "message": "Aucune note trouvée pour cette bouteille.",
                "status": 404,
            }

        # Calculate the average
        average_value = sum(notes) / len(notes)

        return {
            "message": "Moyenne calculée avec succès.",
            "average": average_value,
            "status": 200,
        }

    def create(self) -> dict:
        """
        Creates a new bottle in the database or increments the numbers field
        if a bottle with the same name already exists.

        Returns
        -------
        dict
            A dictionary containing the operation result.
        """
        if not self.config_db:
            return {
                "message": "Donnez la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)

        # Check if the bottle already exists
        existing_bottle_result = self.exist()

        if existing_bottle_result.get("status") != 200:
            return existing_bottle_result  # Return error from exist method

        if existing_bottle_result['data']:
            # Bottle exists, increment the number of bottles
            return self.increment_bouteille(existing_bottle_result['data'][0])

        # Bottle does not exist, create a new entry
        return self.create_bouteille()  # No need to pass connex here

    def create_bouteille(self) -> dict:
        """
        Creates a new bottle in the database.

        Returns
        -------
        dict
            A dictionary containing the operation result.
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
        
        # Create an instance of Connexdb using the config_db
        connex: Connexdb = Connexdb(**self.config_db)

        # Insert the data into the collection
        create_result: dict = connex.insert_data_into_collection(self.collections, bottle_data)

        if create_result.get("status") != 200:
            return {
                "message": "Échec de la création de la bouteille.",
                "status": create_result.get("status"),
            }

        return {
            "message": "Bouteille créée avec succès.",
            "status": 200,
        }

    def exist(self) -> dict:
        """
        Checks if the bottle exists in the database.

        Parameters
        ----------
        connex : Connexdb
            The database connection instance.

        Returns
        -------
        dict
            A dictionary containing the existence check result.
        """
        connex: Connexdb = Connexdb(**self.config_db)
        query = {"nom": self.nom}
        existing_bottle_result = connex.get_data_from_collection(self.collections, query)

        if existing_bottle_result.get("status") != 200:
            return {
                "message": "Échec de la vérification de l'existence de la bouteille.",
                "status": existing_bottle_result.get("status"),
            }

        return existing_bottle_result

    def increment_bouteille(self, existing_bottle: dict) -> dict:
        """
        Increments the numbers field of an existing bottle.

        Parameters
        ----------
        existing_bottle : dict
            The existing bottle data.

        Returns
        -------
        dict
            A dictionary containing the operation result.
        """
        connex: Connexdb = Connexdb(**self.config_db)
        self.numbers = existing_bottle.get("numbers", 0) + 1

        # Update the number of bottles
        update_query = {"_id": existing_bottle["_id"]}
        update_data = {"numbers": self.numbers}

        update_result = connex.update_data_from_collection(self.collections, update_query, update_data)

        if update_result.get("status") != 200:
            return {
                "message": update_result.get("message"),
                "status": update_result.get("status"),
            }

        return {
            "message": "Bouteille existante mise à jour avec succès.",
            "status": 200,
        }

    def delete(self) -> dict:
        """
        Deletes the bottle from the database.

        Returns
        -------
        dict
            A dictionary containing the operation result.
        """
        if not self.config_db:
            return {
                "message": "Donnez la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)

        # Query to delete the bottle by name
        query = {"nom": self.nom}
        delete_result = connex.delete_data_from_collection(self.collections, query)

        if delete_result.get("status") != 200:
            return {
                "message": "Échec de la suppression de la bouteille.",
                "status": delete_result.get("status"),
            }

        return {
            "message": "Bouteille supprimée avec succès.",
            "status": 200,
        }

    def update(self, data: dict) -> dict:
        if not self.config_db:
            return {
                "message": "Donnez la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)
        update_query = {"nom": self.nom}
        update_result = connex.update_data_from_collection(self.collections, update_query, {"$set": data})

        print(update_result)

        if update_result.get("status") != 200:
            return {
                "message": "Échec de la mise à jour du nombre de bouteilles.",
                "status": update_result.get("status"),
            }

        return {
            "message": "Bouteille existante mise à jour avec succès.",
            "status": 200,
        }


if __name__ == "__main__":
    """
    Point d'entrée principal du programme.

    Cette section du code permet d'initialiser un objet Bouteille et de 
    démontrer certaines de ses fonctionnalités, comme la création et 
    l'archivage d'une bouteille.
    """

    # Configuration de la base de données (exemple)
    db_config = {
        "host": "localhost",
        "port": 27018,
        "username": "root",
        "password": "wm7ze*2b"
    }

    # Créer une instance de Bouteille
    bouteille = Bouteille(
        nom="Château Margaux",
        type="Rouge",
        annee=2015,
        region="Bordeaux",
        prix=150.0,
        num_etagere=3,
        config_db=db_config
    )

    # Créer une nouvelle bouteille dans la base de données
    create_result = bouteille.create()
    print(create_result)

    # Archiver la bouteille
    # archive_result = bouteille.archiver()
    # print(archive_result)

    # Consulter les détails de la bouteille
    # details = bouteille.consulter()
    # print(details)






