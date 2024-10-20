from .etageres import Etagere
from Classes.bouteille import Bouteille
from pydantic import BaseModel, Field
from Classes.connexiondb import Connexdb


class Cave(BaseModel):
    """
    Représente une cave à vin avec des étagères.

    Attributs
    ----------
    nom : str
        Nom de la cave.
    nb_emplacement : int
        Nombre d'emplacements disponibles (total des places sur toutes les étagères).
    etageres : list[Etagere]
        Étagères de la cave, indexées par leur numéro.
    config_db : dict
        Configuration de la base de données.
    collections : str
        Nom de la collection dans la base de données.

    Méthodes
    -------
    add_etagere(etagere: Etagere) -> dict
        Ajoute une étagère à la cave et met à jour le nombre d'emplacements.
    del_etagere(etagere: Etagere) -> dict
        Enlève une étagère de la cave et met à jour le nombre d'emplacements.
    update_cave() -> dict
        Met à jour la cave dans la base de données.
    get_cave() -> dict
        Récupère les informations de la cave depuis la base de données.
    create_cave(login_user: str) -> dict
        Crée une nouvelle cave et associe l'utilisateur.
    delete_cave(login_user: str) -> dict
        Supprime la cave de la base de données.
    get_etageres() -> dict
        Récupère les étagères associées à la cave depuis la base de données.
    update_user_caves(login_user: str, cave_name: str, connex: Connexdb, add: bool) -> dict
        Met à jour l'utilisateur pour l'association de la cave.
    """

    nom: str = Field(default="caveX")
    nb_emplacement: int = Field(default=0)
    etageres: list[Etagere] = Field(default_factory=list)  # List of Etagere objects
    config_db: dict = Field(default_factory=dict)
    collections: str = Field(default="caves")

    def get_etageres(self) -> dict:
        """Récupère les étagères associées à la cave depuis la base de données."""
        if not self.config_db:
            return {"message": "Configuration de la base de données requise.", "status": 500}

        connex = Connexdb(**self.config_db)

        # Query to get all etageres related to this cave
        etageres_result = connex.get_data_from_collection("etagere", {"caves": self.nom})

        print("Etageres Result:", etageres_result)  # Debug print

        if etageres_result.get("status") != 200:
            return {"message": "Étagères non trouvées.", "status": 404}

        # Prepare the etageres data
        etageres_data = []
        for etagere in etageres_result['data']:
            etageres_data.append({
                "num_etagere": etagere.get("num"),
                "data": etagere  # Use the etagere data directly
            })

        return {
            "status": 200,
            "etageres_data": etageres_data  # Include the list of etageres
        }

    def add_etagere(self, etagere: Etagere) -> dict:
        """Ajoute une étagère à la cave et met à jour le nombre d'emplacements."""
        if etagere in self.etageres:
            return {"message": "Une étagère avec ce numéro existe déjà.", "status": 400}

        self.etageres.append(etagere)  # Append the Etagere object
        self.nb_emplacement += etagere.nb_place  # Update total available places

        etagere_creation_result: dict = etagere.create_etageres()
        if etagere_creation_result.get("status") != 200:
            return {
                "message": "Échec de la création de l'étagère dans la base de données.",
                "status": etagere_creation_result.get("status", 500)
            }

        rstatus: dict = self.update_cave()
        if rstatus.get("status") != 200:
            return {
                "message": "ajout de l'étagère à la cave a échoué !",
                "status": 500
            }

        return {
            "message": "Étagère ajoutée avec succès.",
            "status": 200,
            "num_etagere": etagere.num
        }

    def del_etagere(self, etagere: Etagere) -> dict:
        """Enlève une étagère de la cave et met à jour le nombre d'emplacements."""
        if etagere not in self.etageres:
            return {"message": "Aucune étagère trouvée.", "status": 404}

        self.nb_emplacement -= etagere.nb_place  # Decrease total available places
        self.etageres.remove(etagere)  # Remove the Etagere object

        rstatus: dict = self.update_cave()
        if rstatus.get("status") != 200:
            return {
                "message": "Échec de la mise à jour de la cave après suppression de l'étagère.",
                "status": 500
            }

        return {"message": "Étagère supprimée avec succès.", "status": 200}

    def update_cave(self) -> dict:
        """Met à jour la cave dans la base de données en s'assurant que les données sont à jour."""
        if not self.config_db:
            return {"message": "Configuration de la base de données requise.", "status": 500}

        connex: Connexdb = Connexdb(**self.config_db)

        # Fetch the current data from the database
        current_data_result = connex.get_data_from_collection(self.collections, {"nom": self.nom})
        if current_data_result.get("status") != 200 or not current_data_result['data']:
            return {"message": "Échec de la récupération des données actuelles de la cave.", "status": 404}

        current_data = current_data_result['data'][0]

        # Update the cave attributes based on the current data
        self.nb_emplacement = current_data.get("nb_emplacement", 0)
        self.etageres = current_data.get("etageres", [])

        # Prepare the update data
        update_status: dict = connex.update_data_from_collection(
            self.collections,
            {"nom": self.nom},
            {
                "nom": self.nom,
                "nb_emplacement": self.nb_emplacement,  # Keep the updated number of placements
                "etageres": [etagere.get("num")for etagere in self.etageres]  # Store only the num of each Etagere
            }
        )

        return {
            "message": "Mise à jour réussie." if update_status.get("status") == 200 else "Échec de la mise à jour de la cave.",
            "status": update_status.get("status", 500)
        }

    def get_cave(self) -> dict:
        """Récupère les informations de la cave depuis la base de données."""
        if not self.config_db:
            return {"message": "Configuration de la base de données requise.", "status": 500}

        connex = Connexdb(**self.config_db)
        cave_result = connex.get_data_from_collection(self.collections, {"nom": self.nom})

        if cave_result.get("status") != 200 or not cave_result['data']:
            return {"message": "Cave non trouvée.", "status": 404}

        # Extract the cave data
        cave_data = cave_result['data'][0]
        
        # Get the etageres data
        etageres_response = self.get_etageres()

        # Return the cave data in the desired format
        return {
            "status": 200,
            "data": {
                "_id": str(cave_data['_id']),  # Convert ObjectId to string
                "nom": cave_data['nom'],
                "nb_emplacement": cave_data['nb_emplacement'],
                "etageres": [etagere.num for etagere in self.etageres],  # Store only the num of each Etagere
                "etagere_data": etageres_response.get("etageres_data", [])  # Add the etageres data
            }
        }

    def create_cave(self, login_user: str) -> dict:
        """Crée une nouvelle cave et associe l'utilisateur."""
        if not self.config_db:
            return {"message": "Configuration de la base de données requise.", "status": 500}

        connex = Connexdb(**self.config_db)
        cave_data = {"nom": self.nom, "nb_emplacement": self.nb_emplacement, "etageres": []}

        # Check if the cave already exists
        existing_cave = connex.get_data_from_collection(self.collections, {"nom": self.nom})
        if existing_cave.get("status") == 200 and existing_cave.get("data"):
            return {"message": "Une cave avec ce nom existe déjà.", "status": 400}

        # Insert the cave into the database
        insert_status = connex.insert_data_into_collection(self.collections, cave_data)
        if insert_status.get("status") != 200:
            return {"message": "Échec de la création de la cave.", "status": insert_status.get("status")}

        # Mise à jour de l'utilisateur
        user_update_status = self.update_user_caves(login_user, self.nom, connex, add=True)
        return {
            "message": "Cave créée et utilisateur mis à jour." if user_update_status.get("status") == 200
            else "Cave créée, mais échec de la mise à jour de l'utilisateur.",
            "status": user_update_status.get("status", 200)
        }

    def delete_cave(self, login_user: str) -> dict:
        """Supprime la cave et met à jour l'utilisateur."""
        if not self.config_db:
            return {"message": "Configuration de la base de données requise.", "status": 500}

        connex = Connexdb(**self.config_db)
        
        # Delete the cave from the caves collection
        delete_status = connex.delete_data_from_collection(self.collections, {"nom": self.nom})
        
        if delete_status.get("status") != 200:
            return {"message": "Échec de la suppression de la cave.", "status": delete_status.get("status")}

        # Update the user's caves list
        user_update_status = self.update_user_caves(login_user, self.nom, connex, add=False)
        
        if user_update_status.get("status") != 200:
            return {"message": "Cave supprimée, mais échec de la mise à jour de l'utilisateur.", "status": user_update_status.get("status")}

        return {"message": "Cave supprimée et utilisateur mis à jour avec succès.", "status": 200}

    def update_user_caves(self, login_user: str, cave_name: str, connex: Connexdb, add: bool) -> dict:
        """Met à jour l'utilisateur pour l'association de la cave."""
        if not connex:
            return {"message": "Connexion à la base de données requise.", "status": 500}

        user_update_data = connex.get_data_from_collection("user", {"login": login_user})

        if user_update_data.get("status") != 200 or not user_update_data['data']:
            return {"message": "Utilisateur non trouvé.", "status": 404}

        user = user_update_data['data'][0]
        caves = user.get("caves", [])

        if add:
            if cave_name in caves:
                return {"message": "La cave est déjà associée.", "status": 400}
            caves.append(cave_name)
        else:
            if cave_name not in caves:
                return {"message": "La cave n'est pas associée.", "status": 400}
            caves.remove(cave_name)

        update_status = connex.update_data_from_collection("user", {"login": login_user}, {"caves": caves})

        return {
            "message": "Mise à jour réussie." if update_status.get("status") == 200
            else "Échec de la mise à jour de l'utilisateur.",
            "status": update_status.get("status", 500)
        }


if __name__ == "__main__":
    config_db = {
        "host": 'localhost',
        "port": 27018,
        "username": "root",
        "password": "wm7ze*2b"
    }
    login_user = "alexggh"  # Remplacez par le login de l'utilisateur
    
    # Exemple de création et de manipulation d'une cave
    cave = Cave(config_db=config_db, nom="cave2", nb_emplacement=10)
    print(cave.create_cave("alexggh"))
    # Assuming you have an Etagere instance to add
    etagere = Etagere(num=1, nb_place=10, cave="cave2", config_db=config_db)
    print(cave.add_etagere(etagere))  # Ajout d'une étagère
    print(cave.get_cave())  # Consultation des informations de la cave
    print(cave.del_etagere(etagere))  # Enlève l'étagère
    print(cave.delete_cave(login_user))  # Supprime la cave

