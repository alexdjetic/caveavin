from personne import Personne
from pydantic import Field
from connexiondb import Connexdb


class Proprietaire(Personne):
    """
    A class to represent a property owner inheriting from Personne.

    Attributes
    ----------
    cave : list of str
        A list representing the caves owned by the property owner.

    Methods
    -------
    auth(login: str, password: str) -> dict
        Authenticates the property owner with the provided login and password.
    """

    cave: list[str] = Field(default=[])

    def create(self) -> dict:
        """
        Creates the user in the database.

        Returns
        -------
        dict
            A dictionary containing a message and status code.
        """
        if self.config_db == {}:
            return {
                "message": "Donner la configuration pour la base de donnée mangodb",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)
        data_user: dict = {
            "id": self.id,
            "perm": self.perm,
            "login": self.login,
            "password": self.password,
            "nom": self.nom,
            "prenom": self.prenom,
            "email": self.email,
            "bouteille_reserver": self.bouteille_reserver if len(self.bouteille_reserver) != 0 else [],
            "cave": self.cave if len(self.cave) != 0 else [],
        }

        # Check user does not already exist
        exist_status = connex.exist(self.collections, {"login": self.login})
        if exist_status.get("status") == 200 and exist_status.get("message") == "User exists":
            return {
                "message": "l'utilisateur éxiste déja dans la base de donnée",
                "status": 500
            }

        # Insert user into the database
        rstatus: dict = connex.insert_data_into_collection(self.collections, data_user)
        if rstatus.get("status") != 200:
            return {
                "message": "La création d'un nouveau utilisateur à échouer !",
                "status": rstatus.get("status")
            }

        return rstatus

    def update(self, query: dict, data: dict) -> dict:
        """
        Updates the user in the database.

        Parameters
        ----------
        query : dict
            The query to match the document to update.
        data : dict
            The new data to set in the matched document.

        Returns
        -------
        dict
            A dictionary containing a message and status code.
        """
        if self.config_db == {}:
            return {
                "message": "Donner la configuration pour la base de donnée mangodb",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)
        rstatus: dict = connex.update_data_from_collection(self.collections, query, data)
        if rstatus.get("status") != 200:
            return {
                "message": "La mise à jour de l'utilisateur a échoué !",
                "status": rstatus.get("status")
            }

        return rstatus

    def delete(self, query: dict) -> dict:
        """
        Deletes the user from the database.

        Parameters
        ----------
        query : dict
            The query to match the document to delete.

        Returns
        -------
        dict
            A dictionary containing a message and status code.
        """
        if self.config_db == {}:
            return {
                "message": "Donner la configuration pour la base de donnée mangodb",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)
        rstatus: dict = connex.delete_data_from_collection(self.collections, query)
        if rstatus.get("status") != 200:
            return {
                "message": "La suppression de l'utilisateur a échoué !",
                "status": rstatus.get("status")
            }

        return rstatus

    def get(self, query: dict) -> dict:
        """
        Fetches the user from the database.

        Parameters
        ----------
        query : dict
            The query to match the document to fetch.

        Returns
        -------
        dict
            A dictionary containing a message, status code, and data.
        """
        if self.config_db == {}:
            return {
                "message": "Donner la configuration pour la base de donnée mangodb",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)
        rstatus: dict = connex.get_all_data_from_collection(self.collections)
        if rstatus.get("status") != 200:
            return {
                "message": "La récupération de l'utilisateur a échoué !",
                "status": rstatus.get("status")
            }

        users = rstatus.get("data")
        for user in users:
            if query.items() <= user.items():
                return {
                    "message": "Utilisateur trouvé",
                    "status": 200,
                    "data": user
                }

        return {
            "message": "Utilisateur non trouvé",
            "status": 500
        }


if __name__ == '__main__':
    config_db = {
        "host": 'localhost',
        "port": 27018,
        "username": "root",
        "password": "wm7ze*2b"
    }

    user = Proprietaire(
        id=1,
        perm="admin",
        login="adminUser",
        password="securePassword123",
        nom="John",
        prenom="Doe",
        email="johndoe@example.com",
        cave=["cave1"],
        config_db=config_db
    )

    print(f"User creation: {user.create()}")
    print(f"User update: {user.update({'login': 'adminUser'}, {'nom': 'UpdatedName'})}")
    print(f"User fetch: {user.get({'login': 'adminUser'})}")
    print(f"User delete: {user.delete({'login': 'adminUser'})}")
