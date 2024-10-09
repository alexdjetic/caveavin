from etageres import Etagere
from bouteille import Bouteille
from pydantic import BaseModel, Field


class Cave(BaseModel):
    num: int = Field(default=-1)
    nb_emplacement: int = Field(default=-1)
    etageres: dict[int, Etagere] = Field(default={})
    config_db: dict = Field(default={})
    collections: str = Field(default="caves")

    def ajouter_etagere(self, num_eta: int) -> dict:
        if num_eta in self.etageres:
            return {
                "message": "L'étagère éxiste déja dans la cave.",
                "status": 500
            }

        # CHANGEZ le ZERO par une vraie étagère lorsque la db et crée A FAIRE
        self.etageres.setdefault(num_eta, 0)

        return {
            "message": "l'étagère à ajouté avec succès de la cave.",
            "status": 200
        }

    def enlever_etagere(self, num_eta: int) -> dict:
        if num_eta not in self.etageres:
            return {
                "message": "L'étagère n'éxiste pas dans la cave",
                "status": 500
            }

        self.etageres.pop(num_eta)

        return {
            "message": "l'étagère à enlever avec succès de la cave.",
            "status": 200
        }

    def consulter(self, bouteille: Bouteille = None) -> dict:

        # obtention de toutes les
        if not bouteille:
            tmp: list = []

            for keys, data in enumerate(self.etageres):
                tmp.append(data.consulter())

            return {
                "bouteilles": tmp,
                "message": "",
                "status": 200
            }

        if not isinstance(bouteille, Bouteille):
            return {
                "message": "La bouteille n'est pas de type bouteille !",
                "status": 501
            }

        # CHECK bouteille existe dans la cave A FAIRE
        # return {
        #                 "message": "La bouteille n'éxiste pas dans la cave !",
        #                 "status": 501
        #             }

        return {
            "bouteilles": bouteille.consulter(),
            "message": "La bouteille à été obtenue avec succès !",
            "status": 200
        }

    def ajouter(self, bouteille: Bouteille) -> dict:
        if not isinstance(bouteille, Bouteille):
            return {
                "message": "La bouteille n'est pas de type bouteille !",
                "status": 501
            }

        # ajout dans la première étagère qui a de la place A FAIRE

        raise NotImplementedError()

    def sortir(self, bouteille: Bouteille) -> dict:
        if not isinstance(bouteille, Bouteille):
            return {
                "message": "La bouteille n'est pas de type bouteille !",
                "status": 501
            }

        # check bouteille présente dans une étagères
        raise NotImplementedError()

    def archiver(self, bouteille: Bouteille) -> dict:
        if not isinstance(bouteille, Bouteille):
            return {
                "message": "La bouteille n'est pas de type bouteille !",
                "status": 501
            }

        # check bouteille présente dans une étagères A FAIRE
        raise NotImplementedError()


    def commenter(self, bouteille: Bouteille) -> dict:
        if not isinstance(bouteille, Bouteille):
            return {
                "message": "La bouteille n'est pas de type bouteille !",
                "status": 501
            }

        # check bouteille présente dans une étagères A FAIRE
        raise NotImplementedError()

    def update_cave(self) -> dict:
        raise NotImplementedError

    def get_cave(self) -> dict:
        raise NotImplementedError

    def delete_cave(self) -> dict:
        raise NotImplementedError

##################
###
##################
