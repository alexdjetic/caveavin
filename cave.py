from etageres import Etagere
from bouteille import Bouteille
from pydantic import BaseModel, Field
from connexiondb import Connexdb


class Cave(BaseModel):
    """
    Une classe représentant une cave à vin.

    Attributs
    ----------
    nom : str
        Le nom de la cave.
    nb_emplacement : int
        Le nombre d'emplacements disponibles dans la cave.
    etageres : dict[int, Etagere]
        Dictionnaire d'étagères dans la cave, où la clé est l'ID de l'étagère.
    config_db : dict
        La configuration de la base de données.
    collections : str
        Le nom de la collection dans la base de données.

    Méthodes
    -------
    ajouter_etagere(num_eta: int) -> dict
        Ajoute une étagère à la cave.
    enlever_etagere(num_eta: int, login_user: str) -> dict
        Enlève une étagère de la cave.
    consulter(bouteille: Bouteille = None) -> dict
        Consulte les détails de la cave et des bouteilles.
    update_cave() -> dict
        Met à jour les informations de la cave dans la base de données.
    get_cave() -> dict
        Récupère les informations de la cave depuis la base de données.
    delete_cave(login_user: str) -> dict
        Supprime la cave de la base de données.
    create_cave(login_user: str) -> dict
        Crée une nouvelle cave dans la base de données et met à jour l'utilisateur associé.
    update_user_caves(login_user: str, cave_name: str, connex: Connexdb, add: bool) -> dict
        Met à jour l'utilisateur pour ajouter ou supprimer le nom de la cave à son attribut "cave".
    """

    nom: str = Field(default="caveX")
    nb_emplacement: int = Field(default=-1)
    etageres: dict[int, Etagere] = Field(default_factory=dict)
    config_db: dict = Field(default_factory=dict)
    collections: str = Field(default="caves")

    def ajouter_etagere(self, num_eta: int) -> dict:
        if num_eta in self.etageres:
            return {
                "message": "Une étagère avec ce numéro existe déjà.",
                "status": 400,
            }

        if len(self.etageres) >= self.nb_emplacement > 0:
            return {
                "message": "Limite d'étagères atteinte.",
                "status": 400,
            }

        new_etagere = Etagere(num=num_eta)
        self.etageres[num_eta] = new_etagere
        self.update_cave()

        return {
            "message": "Étagère ajoutée avec succès.",
            "status": 200,
            "etagere": new_etagere.consulter()
        }

    def enlever_etagere(self, num_eta: int) -> dict:
        """
        Enlève une étagère de la cave.

        Paramètres
        ----------
        num_eta : int
            Le numéro de l'étagère à enlever.
        login_user: str
            Le login de l'utilisateur pour mettre à jour sa liste de caves.

        Retourne
        -------
        dict
            Un dictionnaire indiquant le résultat de l'opération de suppression.
        """
        if num_eta not in self.etageres:
            return {
                "message": "Aucune étagère trouvée avec ce numéro.",
                "status": 404,
            }

        del self.etageres[num_eta]
        self.update_cave()

        return {
            "message": "Étagère enlevée avec succès.",
            "status": 200,
        }

    def consulter(self, bouteille: Bouteille = None) -> dict:
        """
        Consulte les détails de la cave et des bouteilles.

        Paramètres
        ----------
        bouteille : Bouteille, optional
            Une bouteille spécifique à consulter dans la cave.

        Retourne
        -------
        dict
            Un dictionnaire contenant les informations de la cave et des bouteilles.
        """
        if bouteille:
            return bouteille.consulter()

        return {
            "nom": f"Cave {self.nom}",
            "nb_bouteille": sum(etagere.nb_bouteille for etagere in self.etageres.values()),
            "etageres": list(self.etageres.keys())
        }

    def update_cave(self) -> dict:
        """
        Met à jour les informations de la cave dans la base de données.

        Retourne
        -------
        dict
            Un dictionnaire indiquant le résultat de l'opération de mise à jour.
        """
        if not self.config_db:
            return {
                "message": "Donnez la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex = Connexdb(**self.config_db)

        update_data = {
            "nom": self.nom,
            "nb_emplacement": self.nb_emplacement,
            "etageres": list(self.etageres.keys())
        }

        update_status = connex.update_data_from_collection(self.collections, {"nom": self.nom}, update_data)

        if update_status.get("status") != 200:
            return {
                "message": "Échec de la mise à jour de la cave.",
                "status": update_status.get("status"),
            }

        return {
            "message": "Mise à jour de la cave réussie.",
            "status": 200,
        }

    def get_cave(self) -> dict:
        """
        Récupère les informations de la cave depuis la base de données.

        Retourne
        -------
        dict
            Un dictionnaire contenant les informations de la cave.
        """
        if not self.config_db:
            return {
                "message": "Donnez la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex = Connexdb(**self.config_db)

        query = {"nom": self.nom}
        cave_result = connex.get_data_from_collection(self.collections, query)

        if cave_result.get("status") != 200 or not cave_result['data']:
            return {
                "message": "Cave non trouvée.",
                "status": 404,
            }

        cave = cave_result['data'][0]

        return {
            "status": 200,
            "data": cave
        }

    def create_cave(self, login_user: str) -> dict:
        """
        Crée une nouvelle cave dans la base de données et met à jour l'utilisateur associé.

        Parameters
        ----------
        login_user: str
            Le login de l'utilisateur pour associer la cave.

        Retourne
        -------
        dict
            Un dictionnaire indiquant le résultat de l'opération de création.
        """
        if not self.config_db:
            return {
                "message": "Donnez la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex = Connexdb(**self.config_db)

        cave_data = {
            "nom": self.nom,
            "nb_emplacement": self.nb_emplacement,
            "etageres": []
        }

        insert_status = connex.insert_data_into_collection(self.collections, cave_data)

        if insert_status.get("status") != 200:
            return {
                "message": "Échec de la création de la cave.",
                "status": insert_status.get("status"),
            }

        user_update_status = self.update_user_caves(login_user, self.nom, connex, add=True)

        if user_update_status.get("status") != 200:
            return {
                "message": "Cave créée, mais échec de la mise à jour de l'utilisateur.",
                "status": user_update_status.get("status"),
            }

        return {
            "message": "Cave créée et utilisateur mis à jour avec succès.",
            "status": 200,
        }

    def delete_cave(self, login_user: str) -> dict:
        """
        Supprime la cave de la base de données et met à jour l'utilisateur associé.

        Parameters
        ----------
        login_user: str
            Le login de l'utilisateur pour mettre à jour sa liste de caves.

        Retourne
        -------
        dict
            Un dictionnaire indiquant le résultat de l'opération de suppression.
        """
        if not self.config_db:
            return {
                "message": "Donnez la configuration pour la base de données MongoDB",
                "status": 500,
            }

        connex = Connexdb(**self.config_db)

        delete_status = connex.delete_data_from_collection(self.collections, {"nom": self.nom})

        if delete_status.get("status") != 200:
            return {
                "message": "Échec de la suppression de la cave.",
                "status": delete_status.get("status"),
            }

        self.update_user_caves(login_user, self.nom, connex, add=False)

        return {
            "message": "Cave supprimée avec succès.",
            "status": 200,
        }

    def update_user_caves(self, login_user: str, cave_name: str, connex: Connexdb, add: bool) -> dict:
        """
        Met à jour l'utilisateur pour ajouter ou supprimer le nom de la cave à son attribut "cave".

        Parameters
        ----------
        login_user: str
            Le login de l'utilisateur à mettre à jour.
        cave_name: str
            Le nom de la cave à ajouter ou supprimer.
        connex: Connexdb
            L'objet de connexion à la base de données.
        add: bool
            True pour ajouter la cave, False pour la supprimer.

        Retourne
        -------
        dict
            Un dictionnaire indiquant le résultat de l'opération de mise à jour.
        """
        if not connex:
            return {
                "message": "La connexion à la base de données est requise.",
                "status": 500,
            }

        user_update_data = connex.get_data_from_collection("utilisateurs", {"login": login_user})

        if user_update_data.get("status") != 200 or not user_update_data['data']:
            return {
                "message": "Utilisateur non trouvé.",
                "status": 404,
            }

        user = user_update_data['data'][0]

        if add:
            if cave_name in user.get("caves", []):
                return {
                    "message": "La cave est déjà associée à l'utilisateur.",
                    "status": 400,
                }
            user["caves"].append(cave_name)
        else:
            if cave_name not in user.get("caves", []):
                return {
                    "message": "La cave n'est pas associée à l'utilisateur.",
                    "status": 400,
                }
            user["caves"].remove(cave_name)

        update_status = connex.update_data_from_collection("utilisateurs", {"login": login_user}, {"caves": user["caves"]})

        if update_status.get("status") != 200:
            return {
                "message": "Échec de la mise à jour de l'utilisateur.",
                "status": update_status.get("status"),
            }

        return {
            "message": "Mise à jour réussie de l'utilisateur.",
            "status": 200,
        }



if __name__ == "__main__":
    config_db: dict = {
        "host": 'localhost',
        "port": 27018,
        "username": "root",
        "password": "wm7ze*2b"
    }

    # Exemple de création et de manipulation d'une cave
    cave = Cave(config_db=config_db, nom="Cave 1", nb_emplacement=10)

    print(cave.ajouter_etagere(1))  # Ajout d'une étagère
    print(cave.consulter())          # Consultation des informations de la cave
    login_user = "example_user"  # Replace with actual user login
    print(cave.enlever_etagere(1))   # Enlève l'étagère
    print(cave.delete_cave(login_user))        # Supprime la cave


