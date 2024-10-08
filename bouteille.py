from pydantic import BaseModel, Field


class Bouteille(BaseModel):
    """
    A class to represent a bottle of wine.

    Attributes
    ----------
    id : int
        The unique identifier for the bottle.
    nom : str
        The name of the bottle.
    type : str
        The type of wine.
    annee : int
        The year of production.
    region : str
        The region where the wine was produced.
    commentaire : list of str
        Comments about the wine.
    note : float
        The rating of the wine.
    moyen : float
        The average rating of the wine.
    photo : bytes
        The photo of the bottle in binary format.
    prix : float
        The price of the bottle.

    Methods
    -------
    consulter() -> dict
        Returns a dictionary with the bottle's details.
    supprimer() -> dict
        Raises NotImplementedError.
    archiver() -> dict
        Raises NotImplementedError.
    moyenne() -> dict
        Raises NotImplementedError.
    """

    id: int = Field(default=-1)
    nom: str = Field(default="bouteille")
    type: str = Field(default="inconnue")
    annee: int = Field(default=-1)
    region: str = Field(default="Russie")
    commentaire: list[str] = Field(default=[])
    note: float = Field(default=-1.0)
    moyen: float = Field(default=-1.0)
    photo: bytes = Field(default=b"")
    prix: float = Field(default=-1.0)

    def consulter(self) -> dict:
        """
        Returns a dictionary with the bottle's details.

        Returns
        -------
        dict
            A dictionary containing the bottle's details.
        """
        return {
            "id": self.id,
            "nom": self.nom,
            "type": self.type,
            "annee": self.annee,
            "region": self.region,
            "commentaire": self.commentaire,
            "moyen": self.moyen,
            "photo": self.photo,
            "prix": self.prix,
        }

    def supprimer(self) -> dict:
        """
        Raises NotImplementedError.

        Returns
        -------
        dict
            A dictionary with an error message.
        """
        raise NotImplementedError("La method supprimer n'est pas encore implémenté !")

    def archiver(self) -> dict:
        """
        Raises NotImplementedError.

        Returns
        -------
        dict
            A dictionary with an error message.
        """
        raise NotImplementedError("La method archiver n'est pas encore implémenté !")

    def moyenne(self) -> dict:
        """
        Raises NotImplementedError.

        Returns
        -------
        dict
            A dictionary with an error message.
        """
        raise NotImplementedError("La method moyenne n'est pas encore implémenté !")

    def commenter(self, comment: str) -> dict:
        """
        Raises NotImplementedError.

        Returns
        -------
        dict
            A dictionary with an error message.
        """
        if not isinstance(comment, str):
            return {
                "message": "Le commentaire n'est pas de chaine de caractère !",
                "status": 501
            }

        raise NotImplementedError("La method moyenne n'est pas encore implémenté !")

    def noter(self, note: float) -> dict:
        """
        Raises NotImplementedError.

        Returns
        -------
        dict
            A dictionary with an error message.
        """
        if not isinstance(note, float):
            return {
                "message": "La note n'est pas de chaine de caractère !",
                "status": 501
            }

        raise NotImplementedError("La method moyenne n'est pas encore implémenté !")


if __name__ == '__main__':
    user = Bouteille(
        id=1,
        nom="Chateau Margaux",
        type="Rouge",
        annee=2015,
        region="France",
        commentaire=["Excellent wine", "Rich in flavor"],
        note=95.0,
        moyen=94.5,
        photo=b'binarydatahere',
        prix=150.0
    )

    print(user.consulter())
