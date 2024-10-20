from pydantic import BaseModel, Field
from .connexiondb import Connexdb


class Etagere(BaseModel):
    """
    Classe représentant une étagère pour stocker des bouteilles.

    Attributs :
    -----------
    num : int
        Le numéro de l'étagère (par défaut -1).
    nb_place : int
        Le nombre de places disponibles sur l'étagère (par défaut -1).
    nb_bouteille : int
        Le nombre de bouteilles présentes sur l'étagère (par défaut -1).
    bouteilles : list[str]
        La liste des noms de bouteilles stockées sur l'étagère (par défaut vide).
    config_db : dict
        La configuration de connexion à la base de données MongoDB.
    collections : str
        Le nom de la collection MongoDB pour les étagères.
    cave : str
        Le nom de la cave à laquelle l'étagère appartient.
    login : str
        Le login de l'utilisateur associé à l'étagère.
    """

    num: int = Field(default=-1)
    nb_place: int = Field(default=-1)
    nb_bouteille: int = Field(default=-1)
    bouteilles: list[str] = Field(default=[])  # Liste des noms de bouteilles stockées
    config_db: dict = Field(default={})  # Configuration de la base de données MongoDB
    collections: str = Field(default="etagere")
    cave: str = Field(default="")
    login: str = Field(default="")  # Nouveau champ pour le login de l'utilisateur

    def ajouter(self, nom_bouteille: str) -> dict:
        """
        Ajoute une bouteille sur l'étagère si de la place est disponible.

        Paramètre :
        -----------
        nom_bouteille : str
            Le nom de la bouteille à ajouter.

        Retour :
        --------
        dict :
            Message indiquant le succès ou l'échec de l'opération et le statut HTTP correspondant.
        """
        if not isinstance(nom_bouteille, str):
            return {
                "message": "Le nom de la bouteille n'est pas valide !",
                "status": 501
            }

        if self.nb_place <= 0:
            return {
                "message": "Plus de place disponible sur l'étagère !",
                "status": 500
            }

        self.bouteilles.append(nom_bouteille)  # Ajoute la bouteille
        self.nb_place -= 1  # Diminue la place disponible
        self.nb_bouteille += 1  # Incrémente le nombre de bouteilles

        rstatus = self.update_etageres()  # Met à jour la base de données
        if rstatus.get("status") != 200:
            return rstatus

        return {
            "message": f"La bouteille '{nom_bouteille}' a été ajoutée sur l'étagère !",
            "status": 200
        }

    def sortir(self, nom_bouteille: str) -> dict:
        """
        Retire une bouteille de l'étagère.

        Paramètre :
        -----------
        nom_bouteille : str
            Le nom de la bouteille à retirer.

        Retour :
        --------
        dict :
            Message indiquant le succès ou l'échec de l'opération et le statut HTTP correspondant.
        """
        if not isinstance(nom_bouteille, str):
            return {
                "message": "Le nom de la bouteille n'est pas valide !",
                "status": 501
            }

        if nom_bouteille not in self.bouteilles:
            return {
                "message": "La bouteille n'est pas présente sur cette étagère !",
                "status": 500
            }

        self.bouteilles.remove(nom_bouteille)  # Retire la bouteille
        self.nb_place += 1  # Augmente la place disponible
        self.nb_bouteille -= 1  # Diminue le nombre de bouteilles

        rstatus = self.update_etageres()  # Met à jour la base de données
        if rstatus.get("status") != 200:
            return rstatus

        return {
            "message": f"La bouteille '{nom_bouteille}' a été retirée de l'étagère !",
            "status": 200
        }

    def assign_cave(self, nom_cave: str) -> dict:
        """
        Assigne une cave à l'étagère.

        Paramètre :
        -----------
        nom_cave : str
            Le nom de la cave à assigner.

        Retour :
        --------
        dict :
            Message indiquant le succès de l'opération et le statut HTTP correspondant.
        """
        if not isinstance(nom_cave, str):
            return {
                "message": "Le nom de la cave n'est pas valide !",
                "status": 501
            }

        self.cave = nom_cave  # Assigne la cave
        rstatus = self.update_etageres()  # Met à jour la base de données
        if rstatus.get("status") != 200:
            return rstatus

        return {
            "message": f"L'étagère a été assignée à la cave '{nom_cave}' !",
            "status": 200
        }

    def delete_cave(self) -> dict:
        """
        Dissocie l'étagère de sa cave.

        Retour :
        --------
        dict :
            Message indiquant le succès de l'opération et le statut HTTP correspondant.
        """
        self.cave = ""  # Dissocie la cave
        rstatus = self.update_etageres()  # Met à jour la base de données
        if rstatus.get("status") != 200:
            return rstatus

        return {
            "message": "L'étagère a été dissociée de la cave.",
            "status": 200
        }

    def delete_etageres(self) -> dict:
        """
        Supprime une étagère de la base de données.

        Retour :
        --------
        dict :
            Message indiquant le succès ou l'échec de l'opération.
        """
        if not self.config_db:
            return {
                "message": "Configuration de la base de données requise.",
                "status": 500,
            }

        connex = Connexdb(**self.config_db)  # Crée une connexion à la base de données

        # Supprimer l'étagère de la base de données
        rstatus = connex.delete_data_from_collection(self.collections, {"num": self.num, "login": self.login})
        if rstatus.get("status") != 200:
            return {
                "message": "La suppression de l'étagère a échoué !",
                "status": rstatus.get("status"),
            }

        return {
            "message": "L'étagère a été supprimée avec succès.",
            "status": 200
        }

    def create_etageres(self) -> dict:
        """
        Crée une nouvelle étagère dans la base de données.

        Retour :
        --------
        dict :
            Message indiquant le succès ou l'échec de l'opération.
        """
        if not self.config_db:
            return {
                "message": "Donner la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex = Connexdb(**self.config_db)  # Crée une connexion à la base de données
        data_etagere = {
            "num": self.num,
            "nb_place": self.nb_place,
            "nb_bouteille": self.nb_bouteille,
            "bouteilles": self.bouteilles,  # Liste des bouteilles stockées
            "login": self.login  # Login de l'utilisateur associé
        }

        # Insérer l'étagère dans la base de données
        rstatus = connex.insert_data_into_collection(self.collections, data_etagere)
        if rstatus.get("status") != 200:
            return {
                "message": "La création de l'étagère a échoué !",
                "status": rstatus.get("status"),
            }

        return rstatus

    def update_etageres(self) -> dict:
        """
        Met à jour une étagère dans la base de données.

        Retour :
        --------
        dict :
            Message indiquant le succès ou l'échec de l'opération.
        """
        if not self.config_db:
            return {
                "message": "Donner la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex = Connexdb(**self.config_db)  # Crée une connexion à la base de données
        data_etagere = {
            "num": self.num,
            "nb_place": self.nb_place,
            "nb_bouteille": self.nb_bouteille,
            "bouteilles": self.bouteilles,
            "caves": self.cave
        }

        # Mise à jour de l'étagère dans la base de données
        rstatus = connex.update_data_from_collection(self.collections, {"num": self.num}, data_etagere)

        if rstatus.get("status") != 200:
            return {
                "message": "La mise à jour de l'étagère a échoué !",
                "status": rstatus.get("status"),
            }

        return rstatus

    def get_etageres(self) -> dict:
        """
        Récupère les informations d'une étagère depuis la base de données.

        Retour :
        --------
        dict :
            Les informations de l'étagère ou un message d'erreur si échec.
        """
        if not self.config_db:
            return {
                "message": "Configuration de la base de données manquante.",
                "status": 500,
            }

        connex = Connexdb(**self.config_db)  # Crée une connexion à la base de données

        # Récupération des données de l'étagère
        rstatus = connex.get_data_from_collection(self.collections, {"num": self.num})
        if rstatus.get("status") != 200:
            return {
                "message": "La récupération des données de l'étagère a échoué !",
                "status": rstatus.get("status"),
            }

        return rstatus
