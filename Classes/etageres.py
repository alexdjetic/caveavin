from pydantic import BaseModel, Field
from .bouteille import Bouteille
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
    bouteilles : list[Bouteille]
        La liste des bouteilles stockées sur l'étagère (par défaut vide).
    config_db : dict
        La configuration de connexion à la base de données MongoDB.
    collections : str
        Le nom de la collection MongoDB pour les étagères.
    cave : str
        Le nom de la cave à laquelle l'étagère appartient.
    """

    num: int = Field(default=-1)
    nb_place: int = Field(default=-1)
    nb_bouteille: int = Field(default=-1)
    bouteilles: list[str] = Field(default=[])
    config_db: dict = Field(default={})
    collections: str = Field(default="etagere")
    cave: str = Field(default="")  # New field for cave association

    def ajouter(self, bouteille: Bouteille) -> dict:
        """
        Ajoute une bouteille sur l'étagère.

        Paramètres :
        ------------
        bouteille : Bouteille
            La bouteille à ajouter.

        Retour :
        --------
        dict :
            Un dictionnaire avec un message et un statut indiquant si l'opération a réussi ou échoué.
        """
        if not isinstance(bouteille, Bouteille):
            return {
                "message": "La bouteille n'est pas de type bouteille !",
                "status": 501
            }

        if self.nb_place <= 0:
            return {
                "message": "Plus de place disponible sur l'étagère !",
                "status": 500
            }

        # ajout à list locale de bouteille
        self.bouteilles.append(bouteille)

        # mise à jour des attributs de la bouteille
        bouteille.num = self.num
        bouteille.update({"nom": bouteille.nom}, {"num_etagere": self.num})

        self.nb_place -= 1
        self.nb_bouteille += 1

        # Mettre à jour l'étagère dans la base de données
        rstatus = self.update_etageres()
        if rstatus.get("status") != 200:
            return rstatus

        return {
            "message": "La bouteille a été ajoutée sur l'étagère !",
            "status": 200
        }

    def sortir(self, bouteille: Bouteille) -> dict:
        """
        Retire une bouteille de l'étagère.

        Paramètres :
        ------------
        bouteille : Bouteille
            La bouteille à retirer.

        Retour :
        --------
        dict :
            Un dictionnaire avec un message et un statut indiquant si l'opération a réussi ou échoué.
        """
        if not isinstance(bouteille, Bouteille):
            return {
                "message": "La bouteille n'est pas de type bouteille !",
                "status": 501
            }

        if bouteille not in self.bouteilles:
            return {
                "message": "La bouteille n'est pas présente sur cette étagère !",
                "status": 500
            }

        # Retirer la bouteille de l'étagère
        self.bouteilles.remove(bouteille)
        bouteille.delete({"nom": bouteille.nom})
        self.nb_place += 1
        self.nb_bouteille -= 1

        # Mettre à jour l'étagère dans la base de données
        rstatus = self.update_etageres()
        if rstatus.get("status") != 200:
            return rstatus

        return {
            "message": "La bouteille a été retirée de l'étagère !",
            "status": 200
        }

    def delete_etageres(self) -> dict:
        """
        Supprime une étagère de la base de données.

        Retour :
        --------
        dict :
            Un dictionnaire avec un message et un statut indiquant si l'opération a réussi ou échoué.
        """
        if not self.config_db:
            return {
                "message": "Configuration de la base de données requise.",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)

        # Supprimer l'étagère de la base de données
        rstatus = connex.delete_data_from_collection(self.collections, {"num": self.num})
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
            Un dictionnaire avec un message et un statut indiquant si l'opération a réussi ou échoué.
        """
        if not self.config_db:
            return {
                "message": "Donner la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)
        data_etagere = {
            "num": self.num,
            "nb_place": self.nb_place,
            "nb_bouteille": self.nb_bouteille,
            "_bouteilles": [b.consulter() for b in self.bouteilles],
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
            Un dictionnaire avec un message et un statut indiquant si l'opération a réussi ou échoué.
        """
        if not self.config_db:
            return {
                "message": "Donner la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)
        data_etagere = {
            "num": self.num,
            "nb_place": self.nb_place,
            "nb_bouteille": self.nb_bouteille,
            "_bouteilles": [b.consulter() for b in self.bouteilles],
        }

        rstatus = connex.update_data_from_collection(
            self.collections,
            {"num": self.num},  # Critère de mise à jour
            data_etagere
        )

        if rstatus.get("status") != 200:
            return {
                "message": "La mise à jour de l'étagère a échoué !",
                "status": rstatus.get("status"),
            }

        return rstatus

    def get_etageres(self) -> dict:
        """
        Récupère les étagères de la base de données.

        Retour :
        --------
        dict :
            Un dictionnaire contenant toutes les étagères.
        """
        if not self.config_db:
            return {
                "message": "Donner la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex: Connexdb = Connexdb(**self.config_db)
        result = connex.get_all_data_from_collection(self.collections)

        if result.get("status") != 200:
            return {
                "message": "La récupération des étagères a échoué !",
                "status": result.get("status"),
            }

        return {
            "message": "Voici toutes les étagères.",
            "status": 200,
            "data": result['data'],
        }


if __name__ == '__main__':
    # Exemple d'utilisation
    config_db = {
        "host": 'localhost',
        "port": 27018,
        "username": "root",
        "password": "wm7ze*2b"
    }

    # Créer une instance de Etagere
    etagere = Etagere(num=1, nb_place=10, nb_bouteille=0, config_db=config_db)

    # Créer une nouvelle étagère dans la base de données
    print(etagere.create_etageres())

    # Consulter les étagères
    print(etagere.get_etageres())
