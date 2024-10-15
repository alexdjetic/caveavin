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
        Nombre d'emplacements disponibles.
    etageres : dict[int, Etagere]
        Étagères de la cave, indexées par leur numéro.
    config_db : dict
        Configuration de la base de données.
    collections : str
        Nom de la collection dans la base de données.

    Méthodes
    -------
    ajouter_etagere(num_eta: int) -> dict
        Ajoute une étagère à la cave.
    enlever_etagere(num_eta: int) -> dict
        Enlève une étagère de la cave.
    consulter(bouteille: Bouteille = None) -> dict
        Consulte les détails de la cave et des bouteilles.
    update_cave() -> dict
        Met à jour la cave dans la base de données.
    get_cave() -> dict
        Récupère les informations de la cave depuis la base de données.
    delete_cave(login_user: str) -> dict
        Supprime la cave de la base de données.
    create_cave(login_user: str) -> dict
        Crée une nouvelle cave et associe l'utilisateur.
    update_user_caves(login_user: str, cave_name: str, connex: Connexdb, add: bool) -> dict
        Met à jour l'utilisateur pour l'association de la cave.
    """

    nom: str = Field(default="caveX")
    nb_emplacement: int = Field(default=-1)
    etageres: dict[int, Etagere] = Field(default_factory=dict)
    config_db: dict = Field(default_factory=dict)
    collections: str = Field(default="caves")

    def ajouter_etagere(self, num_eta: int) -> dict:
        """Ajoute une étagère si elle n'existe pas et si la capacité le permet."""
        if num_eta in self.etageres:
            return {"message": "Cette étagère existe déjà.", "status": 400}

        if len(self.etageres) >= self.nb_emplacement > 0:
            return {"message": "Limite d'étagères atteinte.", "status": 400}

        # Création et ajout de la nouvelle étagère
        self.etageres[num_eta] = Etagere(num=num_eta)
        self.update_cave()
        return {"message": "Étagère ajoutée avec succès.", "status": 200}

    def enlever_etagere(self, num_eta: int) -> dict:
        """Enlève une étagère de la cave."""
        if num_eta not in self.etageres:
            return {"message": "Aucune étagère trouvée avec ce numéro.", "status": 404}

        del self.etageres[num_eta]
        self.update_cave()
        return {"message": "Étagère enlevée avec succès.", "status": 200}

    def consulter(self, bouteille: Bouteille = None) -> dict:
        """Consulte les détails de la cave ou d'une bouteille spécifique."""
        if bouteille:
            return bouteille.consulter()

        return {
            "nom": f"Cave {self.nom}",
            "nb_bouteille": sum(etagere.nb_bouteille for etagere in self.etageres.values()),
            "etageres": list(self.etageres.keys())
        }

    def update_cave(self) -> dict:
        """Met à jour les informations de la cave dans la base de données."""
        if not self.config_db:
            return {"message": "Configuration de la base de données requise.", "status": 500}

        connex = Connexdb(**self.config_db)
        update_data = {
            "nom": self.nom,
            "nb_emplacement": self.nb_emplacement,
            "etageres": list(self.etageres.keys())
        }

        update_status = connex.update_data_from_collection(
            self.collections,
            {"nom": self.nom},
            update_data
        )

        return {
            "message": "Mise à jour de la cave réussie." if update_status.get(
                "status") == 200 else "Échec de la mise à jour de la cave.",
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

        return {"status": 200, "data": cave_result['data'][0]}

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

        # Change this line
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
    print(cave.ajouter_etagere(1))  # Ajout d'une étagère
    print(cave.consulter())  # Consultation des informations de la cave
    print(cave.enlever_etagere(1))  # Enlève l'étagère
    print(cave.delete_cave(login_user))  # Supprime la cave


