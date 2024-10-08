from personne import Personne
from pydantic import Field


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


if __name__ == '__main__':
    user = Proprietaire(
        id=1,
        perm="admin",
        login="adminUser",
        password="securePassword123",
        nom="John",
        prenom="Doe",
        email="johndoe@example.com",
        cave=["cave1"]
    )

    print(f"Authentication successful: {user.auth('adminUser', 'securePassword123')}")
    print(f"Authentication failed: {user.auth('adminUser', 'wrongPassword')}")
