from pydantic import BaseModel, Field
from bouteille import Bouteille
import unittest


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
    _bouteilles : list[Bouteille]
        La liste des bouteilles stockées sur l'étagère (par défaut vide).
    """

    num: int = Field(default=-1)
    nb_place: int = Field(default=-1)
    nb_bouteille: int = Field(default=-1)
    _bouteilles: list[Bouteille] = Field(default=[])

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

        if self.nb_place <= 1:
            return {
                "message": "Plus de place disponible sur l'étagère !",
                "status": 500
            }

        self._bouteilles.append(bouteille)
        self.nb_place -= 1
        self.nb_bouteille += 1

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

        if bouteille not in self._bouteilles:
            return {
                "message": "La bouteille n'est pas présente sur cette étagère !",
                "status": 500
            }

        bouteille.supprimer()
        self._bouteilles.remove(bouteille)
        self.nb_place += 1
        self.nb_bouteille -= 1

        return {
            "message": "La bouteille a été retirée de l'étagère !",
            "status": 200
        }

    def consulter(self, bouteille: Bouteille = None) -> dict:
        """
        Consulte une ou toutes les bouteilles sur l'étagère.

        Paramètres :
        ------------
        bouteille : Bouteille, optionnel
            La bouteille spécifique à consulter, sinon toutes les bouteilles sont retournées.

        Retour :
        --------
        dict :
            Un dictionnaire avec un message, un statut et les informations sur les bouteilles.
        """
        tmp: list = []

        if not bouteille:
            for bouteilles in self._bouteilles:
                tmp.append(bouteilles.consulter())

            return {
                "bouteilles": tmp,
                "message": "Voici toutes les bouteilles !",
                "status": 200
            }

        if not isinstance(bouteille, Bouteille):
            return {
                "message": "La bouteille n'est pas de type bouteille !",
                "status": 501
            }

        if bouteille not in self._bouteilles:
            return {
                "message": "La bouteille n'est pas présente sur cette étagère !",
                "status": 500
            }

        return {
            "bouteilles": bouteille.consulter(),
            "message": "Voici la bouteille demandée !",
            "status": 200
        }
