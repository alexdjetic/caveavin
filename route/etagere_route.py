# route/etagere_route.py

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from Classes.etageres import Etagere
from route.dependencies import get_user_cookies, config_db
from typing import Optional

router = APIRouter()
templates = Jinja2Templates(directory="templates")

def check_login(user_cookies: dict):
    """Vérifie si l'utilisateur est connecté.

    Args:
        user_cookies (dict): Dictionnaire contenant les cookies de l'utilisateur.

    Raises:
        HTTPException: Si l'utilisateur n'est pas connecté (403 Forbidden).
    """
    if user_cookies.get("login") is None:
        raise HTTPException(status_code=403, detail="User not logged in.")

@router.get("/", response_class=HTMLResponse)
async def manage_etageres(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    """Affiche la page de gestion des étagères.

    Args:
        request (Request): L'objet de requête FastAPI.
        user_cookies (dict): Dictionnaire contenant les cookies de l'utilisateur.

    Returns:
        HTMLResponse: La réponse HTML avec les données des étagères.
    
    Raises:
        HTTPException: Si aucune étagère n'est trouvée (404 Not Found).
    """
    check_login(user_cookies)  # Vérifie si l'utilisateur est connecté
    
    login = user_cookies.get("login")  # Récupère le login de l'utilisateur à partir des cookies
    etagere = Etagere(config_db=config_db, login=login)  # Crée une instance d'Etagere
    etageres_info = etagere.get_etageres()  # Appelle la méthode pour obtenir les étagères

    if etageres_info.get("status") != 200:
        raise HTTPException(status_code=404, detail="Aucune étagère trouvée.")

    return templates.TemplateResponse("etagere.html", {
        "request": request,
        "etageres": etageres_info['data'],  # Passe la liste des étagères au modèle
        **user_cookies
    })

@router.delete("/delete/{num_etagere}", response_model=dict)
async def delete_etagere(num_etagere: int, cave: str, user_cookies: dict = Depends(get_user_cookies)):
    """Supprime une étagère spécifique.

    Args:
        num_etagere (int): Le numéro de l'étagère à supprimer.
        cave (str): Le nom de la cave associée.
        user_cookies (dict): Dictionnaire contenant les cookies de l'utilisateur.

    Returns:
        dict: Le résultat de la suppression de l'étagère.
    
    Raises:
        HTTPException: Si l'étagère n'est pas trouvée ou si la suppression échoue (404 Not Found).
    """
    check_login(user_cookies)  # Vérifie si l'utilisateur est connecté

    login = user_cookies.get("login")  # Récupère le login de l'utilisateur à partir des cookies
    etagere = Etagere(num=num_etagere, cave=cave, login=login, config_db=config_db)  # Crée une instance d'Etagere

    # Supprime l'étagère
    delete_result = etagere.delete_etageres()

    if delete_result.get("status") != 200:
        raise HTTPException(status_code=404, detail="Étagère non trouvée ou échec de la suppression.")

    return JSONResponse(content=delete_result)

@router.get("/get/{num_etagere}", response_model=dict)
async def get_etagere(num_etagere: int, user_cookies: dict = Depends(get_user_cookies)):
    """Récupère les détails d'une étagère spécifique.

    Args:
        num_etagere (int): Le numéro de l'étagère à récupérer.
        user_cookies (dict): Dictionnaire contenant les cookies de l'utilisateur.

    Returns:
        dict: Les informations de l'étagère.

    Raises:
        HTTPException: Si l'étagère n'est pas trouvée (404 Not Found).
    """
    check_login(user_cookies)  # Vérifie si l'utilisateur est connecté

    login = user_cookies.get("login")  # Récupère le login de l'utilisateur à partir des cookies
    etagere = Etagere(num=num_etagere, login=login, config_db=config_db)  # Crée une instance d'Etagere

    # Récupère les détails de l'étagère dans la base de données
    etagere_info = etagere.get_etageres()  # Supposons que cette méthode récupère les détails de l'étagère

    if etagere_info.get("status") != 200:
        raise HTTPException(status_code=404, detail="Étagère non trouvée.")

    return JSONResponse(content=etagere_info)

@router.get("/gets/", response_model=dict)
async def get_all_etageres(user_cookies: dict = Depends(get_user_cookies)):
    """Récupère toutes les étagères.

    Args:
        user_cookies (dict): Dictionnaire contenant les cookies de l'utilisateur.

    Returns:
        dict: Les informations sur toutes les étagères.

    Raises:
        HTTPException: Si aucune étagère n'est trouvée (404 Not Found).
    """
    check_login(user_cookies)  # Vérifie si l'utilisateur est connecté

    login = user_cookies.get("login")  # Récupère le login de l'utilisateur à partir des cookies
    etagere = Etagere(login=login, config_db=config_db)  # Crée une instance d'Etagere

    etageres_info = etagere.get_etageres()  # Supposons que cette méthode récupère toutes les étagères

    if etageres_info.get("status") != 200:
        raise HTTPException(status_code=404, detail="Aucune étagère trouvée.")

    return JSONResponse(content=etageres_info)

@router.put("/update/{num_etagere}", response_model=dict)
async def update_etagere(num_etagere: int, etagere_data: Etagere, user_cookies: dict = Depends(get_user_cookies)):
    """Met à jour les informations d'une étagère spécifique.

    Args:
        num_etagere (int): Le numéro de l'étagère à mettre à jour.
        etagere_data (Etagere): Les nouvelles données de l'étagère à mettre à jour.
        user_cookies (dict): Dictionnaire contenant les cookies de l'utilisateur.

    Returns:
        dict: Le résultat de la mise à jour de l'étagère.
    
    Raises:
        HTTPException: Si la mise à jour échoue (404 Not Found).
    """
    check_login(user_cookies)  # Vérifie si l'utilisateur est connecté

    login = user_cookies.get("login")  # Récupère le login de l'utilisateur à partir des cookies
    etagere = Etagere(num=num_etagere, login=login, **etagere_data.model_dump)  # Crée une instance d'Etagere

    # Met à jour l'étagère
    update_result = etagere.update_etageres()

    if update_result.get("status") != 200:
        raise HTTPException(status_code=404, detail="Échec de la mise à jour de l'étagère.")

    return JSONResponse(content=update_result)
