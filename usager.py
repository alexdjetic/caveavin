from pydantic import BaseModel, EmailStr, Field
from connexiondb import Connexdb
from personne import Personne


class Usager(Personne):
    """
    A class to represent a user inheriting from Personne.

    Attributes
    ----------
    id : int
        The unique identifier for the user.
    perm : str
        The permission level of the user.
    login : str
        The login username of the user.
    password : str
        The password of the user.
    nom : str
        The last name of the user.
    prenom : str
        The first name of the user.
    email : EmailStr
        The email address of the user.
    photo : bytes
        The photo of the user in binary format.
    bouteille_reserver : list of int
        The list of reserved bottles for the user.
    cave : list of int
        The list of caves for the user.
    config_db : dict
        The database configuration for the user.
    collections : str
        The name of the collection in the database.

    Methods
    -------
    create() -> dict
        Creates the user in the database.
    update(data: dict) -> dict
        Updates the user in the database.
    delete(query: dict) -> dict
        Deletes the user from the database.
    get(query: dict) -> dict
        Fetches the user from the database.
    """
    cave: list[int] = Field(default=[])

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

    user = Usager(
        id=1,
        perm="admin",
        login="adminUser",
        password="securePassword123",
        nom="John",
        prenom="Doe",
        email="johndoe@example.com",
        config_db=config_db
    )

    print(f"User creation: {user.create()}")
    print(f"User update: {user.update({'login': 'adminUser'}, {'nom': 'UpdatedName'})}")
    print(f"User fetch: {user.get({'login': 'adminUser'})}")
    print(f"User delete: {user.delete({'login': 'adminUser'})}")
