from pydantic import BaseModel, EmailStr, Field
from connexiondb import Connexdb


class Personne(BaseModel):
    """
    A class to represent a person with authentication functionality.

    Attributes
    ----------
    id : int
        The unique identifier for the person.
    perm : str
        The permission level of the person.
    login : str
        The login username of the person.
    password : str
        The password of the person.
    nom : str
        The last name of the person.
    prenom : str
        The first name of the person.
    email : EmailStr
        The email address of the person.
    photo : bytes
        The photo of the person in binary format.
    bouteille_reserver : list of int
        The list of reserved bottles for the person.
    config_db : dict
        The database configuration for the person.

    Methods
    -------
    auth(login: str, password: str) -> dict
        Authenticates the person with the provided login and password.
    """

    id: int = Field(default=-1)
    perm: str = Field(default="nobody")
    login: str = Field(default="nobody")
    password: str = Field(default="default password")
    nom: str = Field(default="Jhon")
    prenom: str = Field(default="Smith")
    email: EmailStr = Field(default="<EMAIL>")
    photo: bytes = Field(default=b"")
    bouteille_reserver: list[int] = Field(default=[])
    config_db: dict = Field(default={})
    collections: str = Field(default="user")

    def auth(self, login: str, password: str) -> dict:
        """
        Authenticate the user with the provided login and password.

        Parameters
        ----------
        login : str
            The login username to authenticate with.
        password : str
            The password to authenticate with.

        Returns
        -------
        dict
            A dictionary containing a message and status code.
        """
        connex: Connexdb = Connexdb(**self.config_db)
        rstatus: dict = connex.get_all_data_from_collection(self.collections)

        if rstatus.get("status") != 200:
            return {
                "message": rstatus.get("message"),
                "status": rstatus.get("status")
            }

        for user in rstatus.get("data"):
            if login == user.get("login") and password == user.get("password"):
                return {
                    "message": "l'authentification est valide",
                    "status": 200
                }

            if login == user.get("login") and password != user.get("password"):
                return {
                    "message": "le mot de passe est invalide !",
                    "status": 500
                }

        return {
            "message": "le mot de passe ou login est invalide !",
            "status": 500
        }


if __name__ == '__main__':
    config_db: dict = {
        "host": 'localhost',
        "port": 27018,
        "username": "root",
        "password": "wm7ze*2b"
    }

    user = Personne(
        id=1,
        perm="admin",
        login="adminUser",
        password="securePassword123",
        nom="John",
        prenom="Doe",
        email="johndoe@example.com",
        config_db=config_db
    )

    print(f"Authentication successful: {user.auth('adminUser', 'securePassword123')}")
    print(f"Authentication failed: {user.auth('adminUser', 'wrongPassword')}")
