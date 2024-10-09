from pydantic import BaseModel, Field
from connexiondb import Connexdb


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
    commentaire : list of str
        Comments about the wine.
    note : float
        The rating of the wine.
    moyen : float
        The average rating of the wine.
    photo : bytes
        The photo of the bottle in binary format.
    prix : float
        The price of the bottle.

    Methods
    -------
    consulter() -> dict
        Returns a dictionary with the bottle's details.
    supprimer() -> dict
        Raises NotImplementedError.
    archiver() -> dict
        Raises NotImplementedError.
    moyenne() -> dict
        Raises NotImplementedError.
    """

    id: int = Field(default=-1)
    nom: str = Field(default="bouteille")
    type: str = Field(default="inconnue")
    annee: int = Field(default=-1)
    region: str = Field(default="Russie")
    commentaire: list[str] = Field(default=[])
    note: float = Field(default=-1.0)
    moyen: float = Field(default=-1.0)
    photo: bytes = Field(default=b"")
    prix: float = Field(default=-1.0)
    num_etagere: int = Field(default=-1)
    config_db: dict = Field(default={})
    collections: str = Field(default="bouteille")

    def consulter(self) -> dict:
        """
        Returns a dictionary with the bottle's details.

        Returns
        -------
        dict
            A dictionary containing the bottle's details.
        """
        return {
            "nom": self.nom,
            "type": self.type,
            "annee": self.annee,
            "region": self.region,
            "commentaire": self.commentaire,
            "moyen": self.moyen,
            "photo": self.photo,
            "prix": self.prix,
        }

    def supprimer(self) -> dict:
        """
        Raises NotImplementedError.

        Returns
        -------
        dict
            A dictionary with an error message.
        """
        raise NotImplementedError("La méthode supprimer n'est pas encore implémentée !")

    def archiver(self) -> dict:
        """
        Raises NotImplementedError.

        Returns
        -------
        dict
            A dictionary with an error message.
        """
        raise NotImplementedError("La méthode archiver n'est pas encore implémentée !")

    def moyenne(self) -> dict:
        """
        Raises NotImplementedError.

        Returns
        -------
        dict
            A dictionary with an error message.
        """
        raise NotImplementedError("La méthode moyenne n'est pas encore implémentée !")

    def commenter(self, comment: str) -> dict:
        """
        Raises NotImplementedError.

        Returns
        -------
        dict
            A dictionary with an error message.
        """
        if not isinstance(comment, str):
            return {
                "message": "Le commentaire n'est pas une chaîne de caractères !",
                "status": 501
            }

        raise NotImplementedError("La méthode commenter n'est pas encore implémentée !")

    def noter(self, note: float) -> dict:
        """
        Raises NotImplementedError.

        Returns
        -------
        dict
            A dictionary with an error message.
        """
        if not isinstance(note, float):
            return {
                "message": "La note n'est pas un nombre à virgule !",
                "status": 501
            }

        raise NotImplementedError("La méthode noter n'est pas encore implémentée !")

    def create(self) -> dict:
        """
        Creates the bottle in the database.

        Returns
        -------
        dict
            A dictionary containing a message and status code.
        """
        if not self.config_db:
            return {
                "message": "Donnez la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)
        data_bouteille: dict = self.consulter()

        # Check if the bottle already exists
        exist_status = connex.exist(self.collections, {"nom": self.nom})
        if exist_status.get("status") == 200 and \
                exist_status.get("message") == "Bouteille exists":
            return {
                "message": "La bouteille existe déjà dans la base de données",
                "status": 500,
            }

        # Insert bottle into the database
        rstatus: dict = connex.insert_data_into_collection(self.collections, data_bouteille)
        if rstatus.get("status") != 200:
            return {
                "message": "La création de la nouvelle bouteille a échoué !",
                "status": rstatus.get("status"),
            }

        return rstatus

    def get(self, query: dict) -> dict:
        """
        Fetches a bottle from the database based on a query.

        Parameters
        ----------
        query : dict
            The query to fetch the bottle data.

        Returns
        -------
        dict
            A dictionary containing the fetched data.
        """
        if not self.config_db:
            return {
                "message": "Donnez la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)
        result = connex.get_all_data_from_collection(self.collections)
        for bouteille in result['data']:
            if all(query.get(k) == bouteille.get(k) for k in query):
                return {"status": 200, "message": "Bouteille trouvée", "data": bouteille}

        return {"status": 404, "message": "Bouteille non trouvée"}

    def update(self, query: dict, data: dict) -> dict:
        """
        Updates a bottle in the database.

        Parameters
        ----------
        query : dict
            The query to match the document to update.
        data : dict
            The new data to update.

        Returns
        -------
        dict
            The result of the update operation.
        """
        if not self.config_db:
            return {
                "message": "Donnez la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)
        rstatus: dict = connex.update_data_from_collection(self.collections, query, data)

        if rstatus.get("status") != 200:
            return {
                "message": "La mise à jour de la bouteille a échoué !",
                "status": rstatus.get("status"),
            }

        return rstatus

    def delete(self, query: dict) -> dict:
        """
        Deletes a bottle from the database.

        Parameters
        ----------
        query : dict
            The query to match the document to delete.

        Returns
        -------
        dict
            The result of the deletion operation.
        """
        if not self.config_db:
            return {
                "message": "Donnez la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)
        rstatus: dict = connex.delete_data_from_collection(self.collections, query)

        if rstatus.get("status") != 200:
            return {
                "message": "La suppression de la bouteille a échoué !",
                "status": rstatus.get("status"),
            }

        return rstatus


if __name__ == '__main__':
    # Example usage
    # Configure the database connection
    config_db = {
        "host": 'localhost',
        "port": 27018,
        "username": "root",
        "password": "wm7ze*2b"
    }

    # Create a Bouteille instance
    bouteille = Bouteille(
        id=1,
        nom="Chateau Margaux",
        type="Rouge",
        annee=2015,
        region="France",
        commentaire=["Excellent wine", "Rich in flavor"],
        note=95.0,
        moyen=94.5,
        photo=b'binarydatahere',
        prix=150.0,
        config_db=config_db
    )

    # Create (insert) a new bottle in the database
    create_result = bouteille.create()
    print(f"Create result: {create_result}")

    # Get the bottle data from the database
    get_result = bouteille.get({"nom": "Chateau Margaux"})
    print(f"Get result: {get_result}")

    # Update the bottle data
    update_result = bouteille.update({"nom": "Chateau Margaux"}, {"prix": 200.0})
    print(f"Update result: {update_result}")

    # Delete the bottle
    delete_result = bouteille.delete({"nom": "Chateau Margaux"})
    print(f"Delete result: {delete_result}")
