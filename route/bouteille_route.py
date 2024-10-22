from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from Classes import Bouteille, Personne
from .dependencies import config_db, get_user_cookies, effectuer_operation_db, ajouter_commentaire, ajouter_notes, recuperer_archives
from datetime import datetime

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.post("/add", response_class=JSONResponse)
async def add_bouteille(
    request: Request,
    user_cookies: dict = Depends(get_user_cookies),
    nom: str = Form("nom"),
    type: str = Form("type"),
    annee: int = Form("annee"),
    region: str = Form("region"),
    prix: float = Form("prix")
):
    """
    Ajoute une nouvelle bouteille à la collection de l'utilisateur.

    Parameters
    ----------
    request : Request
        La requête HTTP.
    user_cookies : dict
        Les cookies de l'utilisateur pour vérifier la connexion.
    nom : str
        Le nom de la bouteille.
    type : str
        Le type de la bouteille.
    annee : int
        L'année de la bouteille.
    region : str
        La région d'origine de la bouteille.
    prix : float
        Le prix de la bouteille.

    Returns
    -------
    JSONResponse
        Un message de succès ou d'erreur lors de l'ajout de la bouteille.
    """
    # Vérifie si l'utilisateur est connecté
    if not user_cookies["login"]:
        raise HTTPException(status_code=401, detail="Utilisateur non connecté")

    # Crée un objet utilisateur avec les données des cookies
    user = Personne(
        login=user_cookies["login"],
        password="",
        nom=user_cookies["nom"],
        prenom=user_cookies["prenom"],
        perm=user_cookies["perm"],
        collections="user",
        config_db=config_db
    )

    # Crée un objet Bouteille avec les détails fournis
    bouteille = Bouteille(
        nom=nom,
        type=type,
        annee=annee,
        region=region,
        prix=prix,
        config_db=config_db
    )

    # Crée la bouteille dans la base de données
    rstatus: dict = bouteille.create()

    print(rstatus)  # Impression pour débogage

    # Vérifie si la création a réussi
    if rstatus.get("status") != 200:
        return {
            "message": rstatus.get("message"),
            "status": rstatus.get("status")
        }

    # Ajoute la bouteille à la collection de l'utilisateur
    result = user.add_bottle(nom)

    print(result)  # Impression pour débogage

    # Vérifie si l'ajout à la collection a réussi
    if result.get("status") == 200:
        return JSONResponse(content={"status": "success", "message": "Bouteille ajoutée avec succès"})
    else:
        return JSONResponse(content={"status": "error", "message": result.get("message", "Échec de l'ajout de la bouteille")})

@router.get("/{nom_bouteille}", response_class=HTMLResponse)
async def get_bouteille(request: Request, nom_bouteille: str, user_cookies: dict = Depends(get_user_cookies)):
    """
    Récupère les détails d'une bouteille par son nom.

    Parameters
    ----------
    request : Request
        La requête HTTP.
    nom_bouteille : str
        Le nom de la bouteille à récupérer.
    user_cookies : dict
        Les cookies de l'utilisateur pour vérifier la connexion.

    Returns
    -------
    HTMLResponse
        La page HTML contenant les détails de la bouteille ou une page d'erreur.
    """
    print(f"Bouteille reçue : {nom_bouteille}")  # Impression pour débogage
    # Vérifie si l'utilisateur est connecté
    if not user_cookies["login"]:
        return RedirectResponse(url="/user/login", status_code=302)

    # Crée un objet Bouteille pour récupérer ses informations
    bouteille = Bouteille(nom=nom_bouteille, config_db=config_db)
    bottle_data = bouteille.get_all_information()

    print(f"Données de la bouteille récupérées : {bottle_data}")  # Impression pour débogage

    # Vérifie si la récupération des données a réussi
    if bottle_data.get("status") != 200:
        return templates.TemplateResponse("error.html", {
            "request": request,
            **user_cookies,
            "message": bottle_data.get("message", "Échec de la récupération des informations de la bouteille"),
        })

    return templates.TemplateResponse("bottle_details.html", {
        "request": request,
        **user_cookies,
        "data": bottle_data["data"]
    })

@router.get("/delete/{nom_bouteille}", response_class=HTMLResponse)
async def del_bouteille(request: Request, nom_bouteille: str, user_cookies: dict = Depends(get_user_cookies)):
    """
    Supprime une bouteille par son nom.

    Parameters
    ----------
    request : Request
        La requête HTTP.
    nom_bouteille : str
        Le nom de la bouteille à supprimer.
    user_cookies : dict
        Les cookies de l'utilisateur pour vérifier la connexion.

    Returns
    -------
    HTMLResponse
        Redirection vers la collection d'utilisateurs ou message d'erreur.
    """
    # Vérifie si l'utilisateur est connecté
    if not user_cookies["login"]:
        return RedirectResponse(url="/user/login", status_code=302)

    # Crée un objet Bouteille pour la suppression
    bouteille = Bouteille(nom=nom_bouteille, config_db=config_db)
    bottle_data = bouteille.delete()

    # Vérifie si la suppression a réussi
    if bottle_data.get("status") != 200:
        return {
            "message": "La suppression de la bouteille a échoué !",
            "status": bottle_data.get("status")
        }

    # Redirige vers la collection de l'utilisateur après suppression
    return RedirectResponse(url="/user/collection", status_code=302)

@router.get("/update/{nom_bouteille}", response_class=HTMLResponse)
async def get_update_bouteille(request: Request, nom_bouteille: str, user_cookies: dict = Depends(get_user_cookies)):
    """
    Affiche la page de mise à jour des détails d'une bouteille.

    Parameters
    ----------
    request : Request
        La requête HTTP.
    nom_bouteille : str
        Le nom de la bouteille à mettre à jour.
    user_cookies : dict
        Les cookies de l'utilisateur pour vérifier la connexion.

    Returns
    -------
    HTMLResponse
        La page HTML pour mettre à jour la bouteille ou une page d'erreur.
    """
    # Vérifie si l'utilisateur est connecté
    if not user_cookies["login"]:
        return RedirectResponse(url="/user/login", status_code=302)

    # Crée un objet Bouteille pour récupérer ses informations
    bouteille = Bouteille(nom=nom_bouteille, config_db=config_db)
    bottle_data = bouteille.get_all_information()

    # Vérifie si la récupération des données a réussi
    if bottle_data.get("status") != 200:
        return templates.TemplateResponse("error.html", {
            "request": request,
            **user_cookies,
            "message": "Échec de la récupération des informations de la bouteille",
        })

    return templates.TemplateResponse("update_bouteille.html", {
        "request": request,
        **user_cookies,
        "bouteille": bottle_data["data"]
    })

@router.post("/update/{nom_bouteille}", response_class=JSONResponse)
async def post_update_bouteille(
    request: Request,
    nom_bouteille: str,
    user_cookies: dict = Depends(get_user_cookies),
    type: str = Form("type"),
    annee: int = Form("annee"),
    region: str = Form("region"),
    prix: float = Form("prix")
):
    """
    Met à jour les détails d'une bouteille.

    Parameters
    ----------
    request : Request
        La requête HTTP.
    nom_bouteille : str
        Le nom de la bouteille à mettre à jour.
    user_cookies : dict
        Les cookies de l'utilisateur pour vérifier la connexion.
    type : str
        Le nouveau type de la bouteille.
    annee : int
        La nouvelle année de la bouteille.
    region : str
        La nouvelle région d'origine de la bouteille.
    prix : float
        Le nouveau prix de la bouteille.

    Returns
    -------
    JSONResponse
        Un message de succès ou d'erreur lors de la mise à jour de la bouteille.
    """
    # Vérifie si l'utilisateur est connecté
    if not user_cookies["login"]:
        raise HTTPException(status_code=401, detail="Utilisateur non connecté")

    # Crée un objet Bouteille pour la mise à jour
    bouteille = Bouteille(nom=nom_bouteille, config_db=config_db)

    # Prépare les données à mettre à jour
    data: dict = {
        "type": type,
        "annee": annee,
        "region": region,
        "prix": prix
    }

    # Met à jour la bouteille avec les nouvelles informations
    rstatus: dict = bouteille.update(data)

    # Vérifie si la mise à jour a réussi
    if rstatus.get("status") != 200:
        return {
            "message": rstatus.get("message"),
            "status": rstatus.get("status")
        }

    return JSONResponse(content={"status": "success", "message": "Bouteille mise à jour avec succès"})

@router.post("/commentandpair", response_class=JSONResponse)
async def comment_and_pair(
    request: Request,
    user_cookies: dict = Depends(get_user_cookies),
    comment: str = Form(...),  # Ensure to use ... to require this field
    rating: float = Form(...),  # Ensure to use ... to require this field
    nom_bouteille: str = Form(...)
):
    if not user_cookies["login"]:
        raise HTTPException(status_code=401, detail="User not logged in")

    # Use the login as the unique identifier for the user
    login = user_cookies["login"]

    # Get the current date in the desired format (e.g., YYYY-MM-DD)
    current_date = datetime.now().strftime("%Y-%m-%d")

    # Add the comment to the database
    comment_response = ajouter_commentaire(config_db, nom_bouteille, comment, login, date=current_date)

    # Check if the comment was added successfully
    if comment_response.get("status") != 200:
        return JSONResponse(content={"status": "error", "message": comment_response.get("message")})

    # Add the rating to the database
    rating_response = ajouter_notes(config_db, nom_bouteille, rating, login)

    # Check if the rating was added successfully
    if rating_response.get("status") != 200:
        return JSONResponse(content={"status": "error", "message": rating_response.get("message")})

    # Redirect to the bottle details page
    return RedirectResponse(url=f"/bottle/{nom_bouteille}", status_code=302)

@router.get("/archive/{nom_bouteille}", response_class=HTMLResponse)
async def get_archiver_bouteille(request: Request, nom_bouteille: str, user_cookies: dict = Depends(get_user_cookies)):
    # Vérifie si l'utilisateur est connecté
    if not user_cookies["login"]:
        return RedirectResponse(url="/user/login", status_code=302)

    # Crée un objet Bouteille pour récupérer ses informations
    bouteille: Bouteille = Bouteille(nom=nom_bouteille, config_db=config_db)
    bouteille.archiver()

    return RedirectResponse(url=f"/user/collection", status_code=302)

@router.get("/get-archive", response_class=HTMLResponse)
async def get_archiver_bouteille(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    # Vérifie si l'utilisateur est connecté
    if not user_cookies["login"]:
        return RedirectResponse(url="/user/login", status_code=302)

    # Crée un objet Bouteille pour récupérer ses informations
    archive_data: dict = recuperer_archives(config_db)

    return templates.TemplateResponse("archive.html", {
        "request": request,
        **user_cookies,
        "archive": archive_data["archives"][0]
    })
