from fastapi import APIRouter, Request, Depends, Form, HTTPException, Body
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from Classes import Cave, Personne, Etagere
from .dependencies import (
    get_user_cookies, 
    config_db
)

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Route pour afficher le formulaire d'ajout de cave
@router.get("/add-cave", response_class=HTMLResponse)
async def add_cave_form_html(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    """
    Affiche le formulaire pour ajouter une nouvelle cave.

    Args:
        request (Request): La requête HTTP.
        user_cookies (dict): Les cookies de l'utilisateur pour l'authentification.

    Returns:
        HTMLResponse: La page de formulaire pour ajouter une cave.
    """
    if user_cookies["login"] is None:
        return RedirectResponse(url="/user/login", status_code=302)

    # Rendre le formulaire d'ajout de cave sans vérifier les données de cave existantes
    return templates.TemplateResponse("add_cave.html", {
        "request": request,
        **user_cookies
    })

# Route pour ajouter une étagère à une cave
@router.post("/add-etagere", response_class=JSONResponse)
async def add_etagere(
    request: Request,
    user_cookies: dict = Depends(get_user_cookies),
    nom_cave: str = Body(...),  # ... rend le paramètre obligatoire à fournir
    num_etagere: int = Body(...),
    nb_place: int = Body(...)
):
    """
    Ajoute une étagère à une cave spécifiée.

    Args:
        request (Request): La requête HTTP.
        user_cookies (dict): Les cookies de l'utilisateur pour l'authentification.
        nom_cave (str): Le nom de la cave à laquelle ajouter l'étagère.
        num_etagere (int): Le numéro de l'étagère à ajouter.
        nb_place (int): Le nombre de places dans l'étagère.

    Returns:
        JSONResponse: Le statut de l'ajout d'étagère.
    """
    # Vérifier si l'utilisateur est connecté
    if user_cookies.get("login") is None:
        return JSONResponse(content={"status": 401, "message": "Utilisateur non connecté"}, status_code=401)

    # Valider que num_etagere et nb_place sont des entiers positifs
    if num_etagere <= 0 or nb_place <= 0:
        return JSONResponse(content={"status": 400, "message": "num_etagere et nb_place doivent être des entiers positifs."}, status_code=400)
    
    # Vérifier si la cave existe
    cave = Cave(config_db=config_db, nom=nom_cave)
    cave_info = cave.get_cave()

    if cave_info.get("status") != 200:
        return JSONResponse(content={"status": 404, "message": "Cave non trouvée."}, status_code=404)

    # Créer l'étagère et l'ajouter à la cave
    etagere = Etagere(num=num_etagere, nb_place=nb_place, cave=nom_cave, config_db=config_db)
    result = cave.add_etagere(etagere)

    # Retourner le succès ou l'erreur en fonction du résultat
    if result.get("status") == 200:
        return JSONResponse(content={"status": "success", "message": "Étagère ajoutée avec succès."})
    else:
        return JSONResponse(content={"status": "error", "message": result.get("message")}, status_code=400)

# Route pour récupérer les étagères d'une cave
@router.get("/get-etageres/{cave_id}")
async def get_etageres(cave_id: str, user_cookies: dict = Depends(get_user_cookies)):
    """
    Récupère les étagères d'une cave spécifiée.

    Args:
        cave_id (str): L'identifiant de la cave.
        user_cookies (dict): Les cookies de l'utilisateur pour l'authentification.

    Returns:
        JSONResponse: La liste des étagères de la cave.
    """
    if user_cookies["login"] is None:
        return JSONResponse(content={"status": "error", "message": "Utilisateur non connecté"}, status_code=401)

    cave: Cave = Cave(id=cave_id, config_db=config_db)
    etageres = cave.get_etageres()
    return JSONResponse(content={"etageres": etageres})

# Route pour ajouter une nouvelle cave
@router.post("/add-cave")
async def add_cave(
    request: Request,
    user_cookies: dict = Depends(get_user_cookies),
    cave_name: str = Form("cave_name"),
    nb_emplacement: int = Form("nb_emplacement")
):
    """
    Ajoute une nouvelle cave.

    Args:
        request (Request): La requête HTTP.
        user_cookies (dict): Les cookies de l'utilisateur pour l'authentification.
        cave_name (str): Le nom de la cave à ajouter.
        nb_emplacement (int): Le nombre d'emplacements dans la cave.

    Returns:
        RedirectResponse: Redirige vers la collection de l'utilisateur ou affiche une erreur.
    """
    if user_cookies["login"] is None:
        return RedirectResponse(url="/user/login", status_code=302)

    cave: Cave = Cave(config_db=config_db, nom=cave_name, nb_emplacement=nb_emplacement)
    result = cave.create_cave(user_cookies["login"])
    if result["status"] == 200:
        return RedirectResponse(url="/user/collection", status_code=302)
    else:
        return templates.TemplateResponse("add_cave.html", {
            "request": request,
            **user_cookies,
            "error": result["message"]
        })

# Route pour supprimer une cave
@router.delete("/delete/{cave_name}", response_model=dict)
async def delete_cave(cave_name: str, user_cookies: dict = Depends(get_user_cookies)):
    """
    Supprime une cave spécifiée.

    Args:
        cave_name (str): Le nom de la cave à supprimer.
        user_cookies (dict): Les cookies de l'utilisateur pour l'authentification.

    Returns:
        dict: Statut de la suppression de la cave.
    """
    if user_cookies["login"] is None:
        return RedirectResponse(url="/user/login", status_code=302)

    cave: Cave = Cave(config_db=config_db, nom=cave_name)
    result = cave.delete_cave(user_cookies["login"])

    if result.get("stay") != 200:
        raise HTTPException(status_code=404, detail="Cave non trouvée")

    return {"status": "success", "message": "Cave supprimée avec succès"}

# Route pour afficher les détails d'une cave
@router.get("/get/{nom_cave}", response_class=HTMLResponse)
async def cave_details(request: Request, nom_cave: str, user_cookies: dict = Depends(get_user_cookies)):
    """
    Affiche les détails d'une cave spécifiée.

    Args:
        request (Request): La requête HTTP.
        nom_cave (str): Le nom de la cave à afficher.
        user_cookies (dict): Les cookies de l'utilisateur pour l'authentification.

    Returns:
        HTMLResponse: La page avec les détails de la cave.
    """
    if user_cookies["login"] is None:
        return RedirectResponse(url="/user/login", status_code=302)

    # Créer une instance de la classe Cave
    cave: Cave = Cave(nom=nom_cave, config_db=config_db)

    # Récupérer les détails de la cave depuis la base de données
    cave_info = cave.get_cave()  # Supposons que cette méthode récupère les détails de la cave

    if cave_info.get("status") != 200:
        return templates.TemplateResponse("error.html", {"request": request, "message": "Cave non trouvée."})

    # Préparer les données pour le rendu
    cave_data = cave_info['data']

    print(cave_data)  # Affiche les données de la cave pour le débogage

    # Rendre le modèle avec les détails de la cave
    return templates.TemplateResponse("cave_details.html", {"request": request, "data": cave_data, **user_cookies})
