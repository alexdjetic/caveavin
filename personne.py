from pydantic import BaseModel, EmailStr, Field


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
    photo: bytes
        The photo of the person in binary format.

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

    def auth(self, login: str, password: str) -> dict:
        """
        Authenticate the person with the provided login and password.

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
        if login == self.login and password != self.password:
            return {
                "message": "le mot de passe est invalide !",
                "status": 500
            }

        if login != self.login and password == self.password:
            return {
                "message": "le mot de passe ou login est invalide !",
                "status": 500
            }

        return {
            "message": "l'authentification est valide",
            "status": 200
        }


if __name__ == '__main__':
    user = Personne(
        id=1,
        perm="admin",
        login="adminUser",
        password="securePassword123",
        nom="John",
        prenom="Doe",
        email="johndoe@example.com"
    )

    print(f"Authentication successful: {user.auth('adminUser', 'securePassword123')}")
    print(f"Authentication failed: {user.auth('adminUser', 'wrongPassword')}")
