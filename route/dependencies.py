from fastapi import Cookie
from Classes.connexiondb import Connexdb

########################################
#####     Configuration de la DB   #####
########################################

config_db: dict = {
    "host": 'localhost',
    "port": 27018,
    "username": "root",
    "password": "wm7ze*2b"
}

def get_user_cookies(
    login: str = Cookie(None),
    perm: str = Cookie(None),
    nom: str = Cookie(None),
    prenom: str = Cookie(None),
    email: str = Cookie(None)
) -> dict:
    """
    Récupère les cookies de l'utilisateur.

    Parameters
    ----------
    login : str
        Le login de l'utilisateur.
    perm : str
        Les permissions de l'utilisateur.
    nom : str
        Le nom de l'utilisateur.
    prenom : str
        Le prénom de l'utilisateur.
    email : str
        L'email de l'utilisateur.

    Returns
    -------
    dict
        Un dictionnaire contenant les informations de l'utilisateur.
    """
    return {
        "login": login,
        "email": email,
        "perm": perm,
        "nom": nom,
        "prenom": prenom
    }

#######################################
##### Fonction nécessaire au CRUD #####
#######################################

def effectuer_operation_db(
    config_db: dict,
    collection: str,
    operation: str,
    data: dict = None,
    query: dict = None
) -> dict:
    """
    Effectue une opération de base de données (insertion, suppression, mise à jour ou récupération)
    sur la collection spécifiée.

    Parameters
    ----------
    config_db : dict
        Un dictionnaire contenant la configuration pour se connecter à la base de données.
    collection : str
        Le nom de la collection MongoDB (ex: "commentaire", "note").
    operation : str
        L'opération de base de données à effectuer ("insert", "delete", "update", "get").
    data : dict, optional
        Les données à insérer ou à mettre à jour (par défaut None).
    query : dict, optional
        La requête pour localiser les documents à récupérer, mettre à jour ou supprimer (par défaut None).

    Returns
    -------
    dict
        Un dictionnaire contenant le statut de l'opération et un message.
    """
    connex: Connexdb = Connexdb(**config_db)
    rstatus: dict = {}

    # Effectuer l'opération en fonction du type spécifié
    match operation:
        case "insert":
            rstatus = connex.insert_data_into_collection(collection, data)
        case "delete":
            rstatus = connex.delete_data_from_collection(collection, query)
        case "update":
            rstatus = connex.update_data_from_collection(collection, query, data)
        case "get":
            if query is None:
                rstatus = connex.get_all_data_from_collection(collection)
            else:
                rstatus = connex.get_data_from_collection(collection, query)
        case _:
            return {
                "message": f"Opération CRUD invalide '{operation}' (options valides : insert, delete, update, get)",
                "status": 502,
            }

    return rstatus

####################################
##### Gestion des commentaires #####
####################################

def ajouter_commentaire(
    config_db: dict,
    nom_bouteille: str,
    commentaire: str,
    login: str,
    date: str
) -> dict:
    """
    Ajoute un commentaire à la collection 'commentaire'.

    Parameters
    ----------
    config_db : dict
        La configuration de la base de données.
    nom_bouteille : str
        Le nom de la bouteille.
    commentaire : str
        Le contenu du commentaire.
    login : str
        Le login de l'utilisateur ajoutant le commentaire.
    date : str
        La date du commentaire.

    Returns
    -------
    dict
        Un dictionnaire avec le résultat de l'opération.
    """
    data: dict = {
        "auteur": login,
        "comment": commentaire,
        "nom_bouteille": nom_bouteille,
        "date": date
    }
    rstatus: dict = effectuer_operation_db(config_db, "commentaire", "insert", data)

    # Vérifie si une erreur est survenue lors de l'opération
    if rstatus.get("status") != 200:
        return rstatus

    return {"message": "Le commentaire a été ajouté avec succès !", "status": 200}

def supprimer_commentaire(config_db: dict, query: dict) -> dict:
    """
    Supprime un commentaire de la collection 'commentaire'.

    Parameters
    ----------
    config_db : dict
        La configuration de la base de données.
    query : dict
        La requête pour localiser le commentaire à supprimer.

    Returns
    -------
    dict
        Un dictionnaire avec le résultat de l'opération.
    """
    rstatus: dict = effectuer_operation_db(config_db, "commentaire", "delete", query=query)

    # Vérifie si une erreur est survenue lors de l'opération
    if rstatus.get("status") != 200:
        return rstatus

    return {"message": "Le commentaire a été supprimé avec succès !", "status": 200}

def mettre_a_jour_commentaire(config_db: dict, query: dict, data: dict) -> dict:
    """
    Met à jour un commentaire dans la collection 'commentaire'.

    Parameters
    ----------
    config_db : dict
        La configuration de la base de données.
    query : dict
        La requête pour localiser le commentaire à mettre à jour.
    data : dict
        Les nouvelles données pour le commentaire.

    Returns
    -------
    dict
        Un dictionnaire avec le résultat de l'opération.
    """
    rstatus: dict = effectuer_operation_db(config_db, "commentaire", "update", data=data, query=query)

    # Vérifie si une erreur est survenue lors de l'opération
    if rstatus.get("status") != 200:
        return rstatus

    return {"message": "Le commentaire a été mis à jour avec succès !", "status": 200}

def recuperer_commentaire(config_db: dict, query: dict = None) -> dict:
    """
    Récupère des commentaires de la collection 'commentaire'.

    Parameters
    ----------
    config_db : dict
        La configuration de la base de données.
    query : dict, optional
        La requête pour localiser les commentaires (par défaut None, ce qui récupère tous les commentaires).

    Returns
    -------
    dict
        Un dictionnaire avec le résultat de l'opération.
    """
    rstatus: dict = effectuer_operation_db(config_db, "commentaire", "get", query=query)

    # Vérifie si une erreur est survenue lors de l'opération
    if rstatus.get("status") != 200:
        return rstatus

    return {
        "message": "La liste des commentaires a été récupérée avec succès !",
        "status": 200,
        "commentaires": rstatus.get("data")
    }

####################################
#####     Gestion des notes    #####
####################################

def ajouter_notes(config_db: dict, nom_bouteille: str, note: float, login: str) -> dict:
    """
    Ajoute une note à la collection 'note'.

    Parameters
    ----------
    config_db : dict
        La configuration de la base de données.
    nom_bouteille : str
        Le nom de la bouteille.
    note : float
        La valeur de la note.
    login : str
        Le login de l'utilisateur ajoutant la note.

    Returns
    -------
    dict
        Un dictionnaire avec le résultat de l'opération.
    """
    data: dict = {
        "auteur": login,  # Identifiant unique de l'auteur
        "note": note,
        "nom_bouteille": nom_bouteille
    }

    rstatus: dict = effectuer_operation_db(config_db, "note", "insert", data)

    # Vérifie si une erreur est survenue lors de l'opération
    if rstatus.get("status") != 200:
        return rstatus

    return {"message": "La note a été ajoutée avec succès !", "status": 200}

def supprimer_notes(config_db: dict, query: dict) -> dict:
    """
    Supprime une note de la collection 'note'.

    Parameters
    ----------
    config_db : dict
        La configuration de la base de données.
    query : dict
        La requête pour localiser la note à supprimer.

    Returns
    -------
    dict
        Un dictionnaire avec le résultat de l'opération.
    """
    rstatus: dict = effectuer_operation_db(config_db, "note", "delete", query=query)

    # Vérifie si une erreur est survenue lors de l'opération
    if rstatus.get("status") != 200:
        return rstatus

    return {"message": "La note a été supprimée avec succès !", "status": 200}

def mettre_a_jour_notes(config_db: dict, query: dict, data: dict) -> dict:
    """
    Met à jour une note dans la collection 'note'.

    Parameters
    ----------
    config_db : dict
        La configuration de la base de données.
    query : dict
        La requête pour localiser la note à mettre à jour.
    data : dict
        Les nouvelles données pour la note.

    Returns
    -------
    dict
        Un dictionnaire avec le résultat de l'opération.
    """
    rstatus: dict = effectuer_operation_db(config_db, "note", "update", data=data, query=query)

    # Vérifie si une erreur est survenue lors de l'opération
    if rstatus.get("status") != 200:
        return rstatus

    return {"message": "La note a été mise à jour avec succès !", "status": 200}

def recuperer_notes(config_db: dict, query: dict = None) -> dict:
    """
    Récupère des notes de la collection 'note'.

    Parameters
    ----------
    config_db : dict
        La configuration de la base de données.
    query : dict, optional
        La requête pour localiser les notes (par défaut None, ce qui récupère toutes les notes).

    Returns
    -------
    dict
        Un dictionnaire avec le résultat de l'opération.
    """
    rstatus: dict = effectuer_operation_db(config_db, "note", "get", query=query)

    # Vérifie si une erreur est survenue lors de l'opération
    if rstatus.get("status") != 200:
        return rstatus

    return {
        "message": "La liste des notes a été récupérée avec succès !",
        "status": 200,
        "notes": rstatus.get("data")
    }
