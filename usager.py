from personne import Personne
from pydantic import EmailStr, Field


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
    photo: bytes
        The photo of the user in binary format (inherited).

    Methods
    -------
    auth(login: str, password: str) -> dict
        Authenticates the user with the provided login and password.
    """

    id: int = Field(default=-1)
    perm: str = Field(default="nobody")
    login: str = Field(default="nobody")
    password: str = Field(default="default password")
    nom: str = Field(default="Jhon")
    prenom: str = Field(default="Smith")
    email: EmailStr = Field(default="<EMAIL>")


if __name__ == '__main__':
    user = Usager(
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
