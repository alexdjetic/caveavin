from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from Classes.personne import Personne
from .dependencies import get_user_cookies, config_db

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    """Affiche la page de connexion. Si l'utilisateur est déjà connecté, redirige vers la page d'accueil."""
    if user_cookies["login"]:
        response = RedirectResponse(url="/", status_code=302)
        return response
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/auth", response_class=HTMLResponse)
async def login_post(request: Request, login: str = Form(...), password: str = Form(...)):
    """Authentifie l'utilisateur avec les identifiants fournis. Redirige vers l'accueil en cas de succès."""
    user = Personne(
        login=login,
        password=password,
        collections="user",
        config_db=config_db
    )
    auth_result: dict = user.auth()  # Appelle la méthode d'authentification

    if auth_result.get("status") == 200:
        user_data = auth_result.get("user_data", {})
        response = RedirectResponse(url="/", status_code=302)
        cookie_options = {
            "httponly": True,
            "samesite": 'Lax',
            "expires": 3600,
            "secure": request.url.scheme == "https"
        }
        # Définit les cookies de session pour l'utilisateur
        for key in ["login", "perm", "email", "nom", "prenom"]:
            response.set_cookie(key=key, value=user_data.get(key, ""), **cookie_options)
        return response

    error_message = "Authentication failed"  # Message d'erreur par défaut
    if auth_result["status"] == 401:
        error_message = "Invalid credentials"
    elif auth_result["status"] == 404:
        error_message = "User not found"
    return templates.TemplateResponse("login.html", {"request": request, "error": error_message})

@router.get("/logout")
async def logout():
    """Déconnecte l'utilisateur en supprimant les cookies de session."""
    response = RedirectResponse(url="/user/login")
    for key in ["login", "nom", "prenom", "perm"]:
        response.delete_cookie(key=key)  # Supprime les cookies de session
    return response

@router.get("/profil", response_class=HTMLResponse)
async def profil(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    """Affiche le profil de l'utilisateur connecté. Redirige vers la page de connexion si non authentifié."""
    if not user_cookies["login"]:
        response = RedirectResponse(url="/user/login", status_code=302)
        return response
    return templates.TemplateResponse("profil.html", {
        "request": request,
        **user_cookies
    })

@router.get("/collection", response_class=HTMLResponse)
async def collection(request: Request, user_cookies: dict = Depends(get_user_cookies)):
    """Affiche la collection de bouteilles et de caves de l'utilisateur."""
    if user_cookies["login"] is None:
        return RedirectResponse(url="/user/login", status_code=302)

    user = Personne(
        perm=user_cookies["perm"],
        login=user_cookies["login"],
        password="",  # Le mot de passe n'est pas nécessaire pour récupérer les caves
        nom=user_cookies["nom"],
        prenom=user_cookies["prenom"],
        collections="user",
        config_db=config_db
    )

    bottles_response = user.get_bottles()  # Récupère les bouteilles réservées
    caves_response = user.get_caves()  # Récupère les caves associées

    return templates.TemplateResponse("collection.html", {
        "request": request,
        **user_cookies,
        "bouteilles": bottles_response["data"],
        "caves": caves_response["data"]  # Passe les données des caves au template
    })

@router.get("/delete/{user_login}", response_class=HTMLResponse)
async def delete(request: Request, user_login: str, user_cookies: dict = Depends(get_user_cookies)):
    """Supprime un utilisateur de la base de données. Redirige vers la page de déconnexion après suppression."""
    if user_cookies["login"] is None:
        return RedirectResponse(url="/", status_code=302)

    user: Personne = Personne(
        login=user_login,
        config_db=config_db,
        collections="user"
    )

    # Vérifie d'abord si l'utilisateur existe
    user_data: dict = user.get()

    if user_data.get("status") != 200:
        return {
            "message": "l'utilisateur n'éxiste pas dans la base de donnée",
            "status_code": 403
        }

    # Supprime de la base de données
    user.delete()

    # Réinitialise toutes les variables de cookie
    response = RedirectResponse(url="/user/logout", status_code=302)
    return response

@router.get("/create/", response_class=HTMLResponse)
async def create(request: Request, user_cookies: dict = Depends(get_user_cookies), error: str = None):
    """Affiche le formulaire de création d'utilisateur."""
    return templates.TemplateResponse("create_user.html", {"request": request, "error": error})

@router.post("/create/", response_class=HTMLResponse)
async def create_post(request: Request,
                     login: str = Form("login"),
                     password: str = Form("password"),
                     nom: str = Form("nom"),
                     prenom: str = Form("prenom"),
                     perm: str = Form("perm"),
                     email: str = Form("email"),
                     user_cookies: dict = Depends(get_user_cookies)):
    """Crée un nouvel utilisateur avec les données fournies. Redirige vers la page d'accueil en cas de succès."""
    user: Personne = Personne(
        login=str(login),
        password=str(password),
        nom=str(nom),
        prenom=str(prenom),
        perm=str(perm),
        email=str(email),
        config_db=config_db,
        collections="user"
    )

    rstatus: dict = user.create()  # Appelle la méthode de création d'utilisateur

    print(rstatus)

    if rstatus.get("status") != 200:
        error_message = rstatus.get("message", rstatus.get("message"))
        return templates.TemplateResponse("create_user.html", {"request": request, "error": error_message})

    if user_cookies["login"] is None:
        response = RedirectResponse(url="/user/login", status_code=302)
        return response

    response = RedirectResponse(url="/", status_code=302)
    return response

@router.get("/update", response_class=HTMLResponse)
async def update(request: Request, user_cookies: dict = Depends(get_user_cookies), error: str = None):
    """Affiche le formulaire de mise à jour des informations utilisateur."""
    return templates.TemplateResponse("update_user.html", {"request": request, "error": error, **user_cookies})

@router.post("/update", response_class=HTMLResponse)
async def update_post(request: Request,
                     login: str = Form("login"),
                     password: str = Form("password"),
                     nom: str = Form("nom"),
                     prenom: str = Form("prenom"),
                     perm: str = Form("perm"),
                     email: str = Form("email"),
                     user_cookies: dict = Depends(get_user_cookies)):
    """Met à jour les informations de l'utilisateur avec les données fournies. Redirige vers la page de profil après la mise à jour."""
    if user_cookies["login"] is None:
        response = RedirectResponse(url="/user/login", status_code=302)
        return response

    user: Personne = Personne(
        login=str(login),
        nom=str(nom),
        prenom=str(prenom),
        perm=str(perm),
        email=str(email),
        config_db=config_db,
        collections="user"
    )

    data: dict = {
        "login": str(login),
        "nom": str(nom),
        "prenom": str(prenom),
        "perm": str(perm)
    }

    if password:
        user.password = password

    rstatus: dict = user.update(data)  # Appelle la méthode de mise à jour des informations utilisateur

    print(rstatus)

    cookie_options = {
        "httponly": True,
        "samesite": 'Lax',
        "expires": 3600,
        "secure": request.url.scheme == "https"
    }

    # Met à jour les cookies
    response = RedirectResponse(url="/user/profil", status_code=302)
    response.set_cookie(key="nom", value=nom, **cookie_options)
    response.set_cookie(key="prenom", value=prenom, **cookie_options)
    response.set_cookie(key="perm", value=perm, **cookie_options)
    response.set_cookie(key="email", value=email, **cookie_options)
    return response
