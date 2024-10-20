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

    # Attributs de la classe
    nom: str = Field(default="caveX")  # Nom par défaut de la cave
    nb_emplacement: int = Field(default=0)  # Initialisation du nombre d'emplacements
    etageres: list[Etagere] = Field(default_factory=list)  # Liste des objets Etagere
    config_db: dict = Field(default_factory=dict)  # Configuration de la base de données
    collections: str = Field(default="caves")  # Nom de la collection pour les caves

    def get_etageres(self) -> dict:
        """Récupère les étagères associées à la cave depuis la base de données."""
        # Vérifie que la configuration de la base de données est fournie
        if not self.config_db:
            return {"message": "Configuration de la base de données requise.", "status": 500}

        connex = Connexdb(**self.config_db)  # Connexion à la base de données

        # Requête pour obtenir toutes les étagères liées à cette cave
        etageres_result = connex.get_data_from_collection("etagere", {"caves": self.nom})

        print("Etageres Result:", etageres_result)  # Affichage pour le débogage

        # Vérifie le résultat de la requête
        if etageres_result.get("status") != 200:
            return {"message": "Étagères non trouvées.", "status": 404}

        # Prépare les données des étagères
        etageres_data = []
        for etagere in etageres_result['data']:
            etageres_data.append({
                "num_etagere": etagere.get("num"),  # Numéro de l'étagère
                "data": etagere  # Utilise directement les données de l'étagère
            })

        return {
            "status": 200,
            "etageres_data": etageres_data  # Retourne la liste des étagères
        }

    def add_etagere(self, etagere: Etagere) -> dict:
        """Ajoute une étagère à la cave et met à jour le nombre d'emplacements."""
        # Vérifie si l'étagère existe déjà
        if etagere in self.etageres:
            return {"message": "Une étagère avec ce numéro existe déjà.", "status": 400}

        self.etageres.append(etagere)  # Ajoute l'objet Etagere
        self.nb_emplacement += etagere.nb_place  # Met à jour le nombre total d'emplacements

        # Création de l'étagère dans la base de données
        etagere_creation_result: dict = etagere.create_etageres()
        if etagere_creation_result.get("status") != 200:
            return {
                "message": "Échec de la création de l'étagère dans la base de données.",
                "status": etagere_creation_result.get("status", 500)
            }

        # Mise à jour de la cave après ajout de l'étagère
        rstatus: dict = self.update_cave()
        if rstatus.get("status") != 200:
            return {
                "message": "Ajout de l'étagère à la cave a échoué !",
                "status": 500
            }

        return {
            "message": "Étagère ajoutée avec succès.",
            "status": 200,
            "num_etagere": etagere.num  # Retourne le numéro de l'étagère ajoutée
        }

    def del_etagere(self, etagere: Etagere) -> dict:
        """Enlève une étagère de la cave et met à jour le nombre d'emplacements."""
        # Vérifie si l'étagère existe dans la cave
        if etagere not in self.etageres:
            return {"message": "Aucune étagère trouvée.", "status": 404}

        self.nb_emplacement -= etagere.nb_place  # Diminue le nombre total d'emplacements
        self.etageres.remove(etagere)  # Supprime l'objet Etagere

        # Mise à jour de la cave après suppression de l'étagère
        rstatus: dict = self.update_cave()
        if rstatus.get("status") != 200:
            return {
                "message": "Échec de la mise à jour de la cave après suppression de l'étagère.",
                "status": 500
            }

        return {"message": "Étagère supprimée avec succès.", "status": 200}

    def update_cave(self) -> dict:
        """Met à jour la cave dans la base de données."""
        # Vérifie que la configuration de la base de données est fournie
        if not self.config_db:
            return {"message": "Configuration de la base de données requise.", "status": 500}

        connex = Connexdb(**self.config_db)  # Connexion à la base de données

        # Prépare les données pour mettre à jour la cave
        cave_data = {
            "nom": self.nom,
            "nb_emplacement": self.nb_emplacement,
            "etageres": [etagere.num for etagere in self.etageres]  # Stocke seulement le numéro de chaque Etagere
        }

        rstatus = connex.update_data_from_collection(self.collections, {"nom": self.nom}, cave_data)

        if rstatus.get("status") != 200:
            return {
                "message": "La mise à jour de la cave a échoué !",
                "status": rstatus.get("status"),
            }

        return {
            "message": "Cave mise à jour avec succès.",
            "status": 200
        }

    def get_cave(self) -> dict:
        """Récupère les informations de la cave depuis la base de données."""
        # Vérifie que la configuration de la base de données est fournie
        if not self.config_db:
            return {"message": "Configuration de la base de données requise.", "status": 500}

        connex = Connexdb(**self.config_db)  # Connexion à la base de données
        cave_result = connex.get_data_from_collection(self.collections, {"nom": self.nom})

        # Vérifie le résultat de la requête
        if cave_result.get("status") != 200 or not cave_result['data']:
            return {"message": "Cave non trouvée.", "status": 404}

        # Extraction des données de la cave
        cave_data = cave_result['data'][0]
        
        # Récupère les données des étagères
        etageres_response = self.get_etageres()

        # Retourne les données de la cave dans le format désiré
        return {
            "status": 200,
            "data": {
                "_id": str(cave_data['_id']),  # Convertit ObjectId en chaîne de caractères
                "nom": cave_data['nom'],
                "nb_emplacement": cave_data['nb_emplacement'],
                "etageres": [etagere.num for etagere in self.etageres],  # Stocke seulement le numéro de chaque Etagere
                "etagere_data": etageres_response.get("etageres_data", [])  # Ajoute les données des étagères
            }
        }

    def create_cave(self, login_user: str) -> dict:
        """Crée une nouvelle cave et associe l'utilisateur."""
        # Vérifie que la configuration de la base de données est fournie
        if not self.config_db:
            return {"message": "Configuration de la base de données requise.", "status": 500}

        connex = Connexdb(**self.config_db)  # Connexion à la base de données

        # Prépare les données pour la création de la cave
        cave_data = {
            "nom": self.nom,
            "nb_emplacement": self.nb_emplacement,
            "etageres": [],
        }

        rstatus = connex.add_data_to_collection(self.collections, cave_data)

        if rstatus.get("status") != 200:
            return {
                "message": "La création de la cave a échoué !",
                "status": rstatus.get("status")
            }

        # Met à jour les caves de l'utilisateur
        self.update_user_caves(login_user, self.nom, connex, add=True)

        return {
            "message": "Cave créée avec succès.",
            "status": 200,
        }

    def delete_cave(self, login_user: str) -> dict:
        """Supprime la cave de la base de données."""
        # Vérifie que la configuration de la base de données est fournie
        if not self.config_db:
            return {"message": "Configuration de la base de données requise.", "status": 500}

        connex = Connexdb(**self.config_db)  # Connexion à la base de données
        rstatus = connex.delete_data_from_collection(self.collections, {"nom": self.nom})

        if rstatus.get("status") != 200:
            return {
                "message": "La suppression de la cave a échoué !",
                "status": rstatus.get("status")
            }

        # Met à jour les caves de l'utilisateur
        self.update_user_caves(login_user, self.nom, connex, add=False)

        return {
            "message": "Cave supprimée avec succès.",
            "status": 200,
        }

    def update_user_caves(self, login_user: str, cave_name: str, connex: Connexdb, add: bool) -> dict:
        """Met à jour l'utilisateur pour l'association de la cave."""
        # Prépare la mise à jour en fonction de l'ajout ou de la suppression de la cave
        update_data = {"$addToSet": {"caves": cave_name}} if add else {"$pull": {"caves": cave_name}}

        # Met à jour l'utilisateur en fonction des modifications
        user_update_result = connex.update_data_from_collection("utilisateurs", {"login": login_user}, update_data)

        if user_update_result.get("status") != 200:
            return {
                "message": "Échec de la mise à jour de l'utilisateur.",
                "status": user_update_result.get("status")
            }

        return {
            "message": "Mise à jour des caves de l'utilisateur réussie.",
            "status": 200
        }
