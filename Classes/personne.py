from pydantic import BaseModel, EmailStr, Field
from Classes.connexiondb import Connexdb
from typing import Optional, List, Dict, Any
from bson import ObjectId



class Personne(BaseModel):
    """
    A class to represent a person with authentication functionality.

    Attributes
    ----------
    id : Optional[int]
        The unique identifier for the person.
    perm : Optional[str]
        The permission level of the person.
    login : Optional[str]
        The login username of the person.
    password : Optional[str]
        The password of the person.
    nom : Optional[str]
        The last name of the person.
    prenom : Optional[str]
        The first name of the person.
    email : Optional[EmailStr]
        The email address of the person.
    photo : Optional[bytes]
        The photo of the person in binary format.
    bouteille_reserver : Optional[List[int]]
        The list of reserved bottles for the person.
    config_db : Optional[Dict[str, Any]]
        The database configuration for the person.
    collections : Optional[str]
        The collection name in the database.

    Methods
    -------
    create() -> dict
        Creates a user in the database.
    update(query: dict, data: dict) -> dict
        Updates the user in the database.
    delete(query: dict) -> dict
        Deletes the user from the database.
    get(query: dict) -> dict
        Retrieves the user from the database.
    auth(login: str, password: str) -> dict
        Authenticates the person with the provided login and password.
    get_user_reserved_bottles() -> dict
        Retrieves the reserved bottles for the user based on their login.
    add_bottle(bottle_id: str) -> dict
        Adds a bottle to the user's bouteille_reserver list.
    """

    id: Optional[int] = Field(default=None)
    perm: Optional[str] = Field(default=None)
    login: Optional[str] = Field(default=None)
    password: Optional[str] = Field(default=None)
    nom: Optional[str] = Field(default=None)
    prenom: Optional[str] = Field(default=None)
    email: Optional[EmailStr] = Field(default=None)
    photo: Optional[bytes] = Field(default=None)
    bouteille_reserver: Optional[List[int]] = Field(default_factory=list)
    config_db: Optional[Dict[str, Any]] = Field(default_factory=dict)
    collections: Optional[str] = Field(default=None)
    caves: Optional[List[str]] = Field(default_factory=list)

    def create(self) -> dict:
        """Creates a user in the database."""
        if not self.config_db:
            return {
                "message": "Please provide the MongoDB database configuration.",
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
            "bouteille_reserver": self.bouteille_reserver if self.bouteille_reserver else [],
        }

        # Check if the user already exists
        exist_status = connex.exist(self.collections, {"login": self.login})
        if exist_status.get("status") == 200 and exist_status.get("message") == "User exists":
            return {
                "message": "The user already exists in the database.",
                "status": 500
            }

        # Insert the user into the database
        rstatus: dict = connex.insert_data_into_collection(self.collections, data_user)

        if rstatus.get("status") != 200:
            return {
                "message": rstatus.get("message"),
                "status": rstatus.get("status")
            }

        return rstatus

    def update(self, data: dict) -> dict:
        """Updates the user in the database."""
        if not self.config_db:
            return {
                "message": "Please provide the MongoDB database configuration.",
                "status": 500,
            }

        query: dict = {"login": self.login}
        connex: Connexdb = Connexdb(**self.config_db)
        
        # Check if we're updating the caves field
        if "caves" in data:
            # Use $addToSet to add the cave if it doesn't exist
            update_data = {"$addToSet": {"caves": {"$each": data["caves"]}}}
        else:
            update_data = {"$set": data}
        
        rstatus: dict = connex.update_data_from_collection(self.collections, query, update_data)
        if rstatus.get("status") != 200:
            return {
                "message": "Failed to update the user!",
                "status": rstatus.get("status")
            }

        return rstatus

    def update_user_info(self) -> dict:
        """Updates the user in the database."""

        query: dict = {"login": self.login}
        update_data = {
            "nom": self.nom,
            "prenom": self.prenom,
            "email": self.email,
            "perm": self.perm
        }
        connex: Connexdb = Connexdb(**self.config_db)

        rstatus: dict = connex.update_data_from_collection(self.collections, query, update_data)
        if rstatus.get("status") != 200:
            return rstatus

        return rstatus

    def delete(self) -> dict:
        """Deletes the user from the database."""
        if not self.config_db:
            return {
                "message": "Please provide the MongoDB database configuration.",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)
        query: dict = {"login": self.login}
        rstatus: dict = connex.delete_data_from_collection(self.collections, query)
        if rstatus.get("status") != 200:
            return {
                "message": "Failed to delete the user!",
                "status": rstatus.get("status")
            }

        # supprimer les bouteilles qu'utilisateur à aussi A FAIRE

        rstatus: dict = connex.delete_data_from_collection(self.collections, query)
        return rstatus

    def get(self) -> dict:
        """Retrieves the user from the database."""
        if not self.config_db:
            return {
                "message": "Please provide the MongoDB database configuration.",
                "status": 500,
            }

        query_search: dict = {"login": self.login}
        connex: Connexdb = Connexdb(**self.config_db)
        rstatus: dict = connex.get_data_from_collection(self.collections, query_search)

        if rstatus.get("status") != 200:
            return {
                "message": "Failed to retrieve users for authentication!",
                "status": rstatus.get("status"),
                "data": []
            }

        return {
            "message": "User found",
            "status": 200,
            "data": rstatus.get("data")
        }

    def auth(self) -> Dict[str, Any]:
        """Authenticates the person with the provided login and password."""
        # Check if the database configuration is provided
        if not self.config_db:
            return {
                "message": "Please provide the MongoDB database configuration.",
                "status": 500,
            }

        # Create a database connection
        connex = Connexdb(**self.config_db)

        # Prepare the query to search for the user
        query_search: dict = {
            "login": self.login,
            "password": self.password
        }

        # Execute the query to fetch user data
        rstatus: dict = connex.get_data_from_collection(self.collections, query_search)

        # Check if any user was found
        if not rstatus.get("data"):
            return {
                "message": "Aucun utilisateur trouvé avec les informations fournies.",
                "status": 404
            }

        # Return success message and user data if found
        return {
            "message": "L'utilisateur a été authentifié avec succès !",
            "status": 200,
            "user_data": rstatus.get("data")[0]
        }

    def get_bottles(self) -> dict:
        """
        Retrieves the reserved bottles for the user based on their login.

        Returns
        -------
        dict
            A dictionary containing the status, message, and list of reserved bottles.
        """
        connex: Connexdb = Connexdb(**self.config_db)

        # Fetch user data by login
        user_data_result = connex.get_data_from_collection(self.collections, {"login": self.login})

        print(user_data_result)

        if user_data_result.get("status") != 200 or not user_data_result.get("data"):
            return {
                "status": 401,
                "message": "Identifiant ou mot de passe invalide",
                "data": []
            }

        user_data = user_data_result.get("data")[0]
        reserved_bottles = user_data.get("bouteille_reserver", [])

        # check qu'aucune bouteille est disponible
        if not reserved_bottles:
            return {
                "status": 200,
                "message": "L'utilisateur ne possède aucune bouteille",
                "data": [] # arret de cette fonction avec un tableau vide
            }

        # Consolidate bottle information
        bottles = {}
        for bottle_name in reserved_bottles:
            bottle_info = connex.get_data_from_collection("bouteille", {"nom": bottle_name})

            if bottle_info.get("status") == 200 and bottle_info.get("data"):
                bottle_data = bottle_info["data"][0]
                if bottle_name in bottles:
                    bottles[bottle_name]["number"] += 1
                else:
                    bottle_data["number"] = 1
                    bottles[bottle_name] = bottle_data

        return {
            "status": 200,
            "message": "Toutes les bouteilles ont été récupérées",
            "data": bottles
        }

    def get_caves(self) -> dict:
        """
        Retrieves the caves associated with the user based on their login.
        """
        connex: Connexdb = Connexdb(**self.config_db)

        # Fetch user data by login
        user_data_result = connex.get_data_from_collection(self.collections, {"login": self.login})

        if user_data_result.get("status") != 200 or not user_data_result.get("data"):
            return {
                "status": 401,
                "message": "Identifiant ou mot de passe invalide",
                "data": []
            }

        user_data = user_data_result.get("data")[0]
        user_caves = user_data.get("caves", [])

        # Print for debugging
        print(f"User caves: {user_caves}")

        # Check if the user has no caves available
        if not user_caves:
            return {
                "status": 200,
                "message": "L'utilisateur ne possède aucune cave",
                "data": {}
            }

        # Fetch cave information for each cave associated with the user
        caves = {}
        for cave_name in user_caves:
            cave_info = connex.get_data_from_collection("caves", {"nom": cave_name})
            if cave_info.get("status") == 200 and cave_info.get("data"):
                caves[cave_name] = cave_info["data"][0]

        return {
            "status": 200,
            "message": "Toutes les caves ont été récupérées",
            "data": caves
        }

    def add_bottle(self, bottle_name: str) -> dict:
        """
        Adds a bottle to the user's bouteille_reserver list.

        Parameters
        ----------
        bottle_name : str
            The name of the bottle to be added.

        Returns
        -------
        dict
            A dictionary containing the status and message of the operation.
        """
        if not self.config_db:
            return {
                "message": "Please provide the MongoDB database configuration.",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)

        # Fetch the current user's data to get the existing bouteille_reserver list
        user_data_result = connex.get_data_from_collection(self.collections, {"login": self.login})

        if user_data_result.get("status") != 200 or not user_data_result.get("data"):
            return {
                "status": 401,
                "message": "User not found or invalid login."
            }

        # Get the current bouteille_reserver list
        user_data = user_data_result.get("data")[0]
        current_bottles = user_data.get("bouteille_reserver", [])

        # Append the new bottle name to the list
        if bottle_name not in current_bottles:
            current_bottles.append(bottle_name)

        # Update the user's bouteille_reserver list in the database
        update_result = connex.update_data_from_collection(
            self.collections,
            {"login": self.login},
            {"bouteille_reserver": current_bottles}
        )

        print(update_result)

        if update_result.get("status") != 200:
            return {
                "status": 500,
                "message": update_result.get("message")
            }

        return {
            "status": 200,
            "message": "Bottle added successfully to user's collection"
        }


if __name__ == '__main__':
    config_db: dict = {
        "host": 'localhost',
        "port": 27018,
        "username": "root",
        "password": "wm7ze*2b"
    }

    user = Personne(
        login="alexandre",
        password="wm7ze*2b",
        config_db=config_db,
        collections="user"
    )

    user.create()
    print("Before update:")
    print(user.get())

    # print("\nUpdating caves:")
    # print(user.update({"caves": ["cave2"]}))

    #print("\nAfter update:")
    # print(user.get())

    # Test add_bottle method
    # print("\nAdding a bottle:")
    # bottle_id = "test"
    # print(user.add_bottle(bottle_id))

    # print("\nAfter adding bottle:")
    # print(user.get())




